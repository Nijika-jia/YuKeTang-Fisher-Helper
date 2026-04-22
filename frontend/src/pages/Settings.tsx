import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import type { NotificationSub, CourseItem } from '../types'
import { useToast } from '../components/Toast'

interface CourseConfig {
  name: string
  type1: string
  type2: string
  type3: string
  type4: string
  type5: string
  answer_delay_min: number
  answer_delay_max: number
  answer_last5s: boolean
  auto_danmu: boolean
  auto_redpacket: boolean
  danmu_threshold: number
  notification: NotificationSub
  voice_notification: NotificationSub
}

interface CourseState extends CourseConfig {
  courseId: string
  saveStatus: 'idle' | 'saving' | 'saved' | 'error'
}

interface AIKeyEntry {
  name: string
  provider: string
  key: string
  base_url?: string
  model?: string
}

const PROVIDER_LABELS: Record<string, string> = {
  google: 'Google',
  qwen: 'ModelScope',
  dashscope: 'Aliyun DashScope',
  moonshot: 'Moonshot (KIMI)',
  openai_compat: 'OpenAI-compatible',
}

interface AISettings {
  keys: AIKeyEntry[]
  active_key: number
  fallback_keys: boolean
}

type CoursesMap = Record<string, CourseConfig>

function buildCourseStates(allCourses: CourseItem[], settings: CoursesMap, defaults: CourseConfig): CourseState[] {
  return allCourses.map((c) => {
    const cfg = settings[c.classroom_id] ?? {} as Partial<CourseConfig>
    return {
      courseId: c.classroom_id,
      name: c.name,
      type1: cfg.type1 ?? defaults.type1,
      type2: cfg.type2 ?? defaults.type2,
      type3: cfg.type3 ?? defaults.type3,
      type4: cfg.type4 ?? defaults.type4,
      type5: cfg.type5 ?? defaults.type5,
      answer_delay_min: cfg.answer_delay_min ?? defaults.answer_delay_min,
      answer_delay_max: cfg.answer_delay_max ?? defaults.answer_delay_max,
      answer_last5s: cfg.answer_last5s ?? defaults.answer_last5s,
      auto_danmu: cfg.auto_danmu ?? defaults.auto_danmu,
      auto_redpacket: cfg.auto_redpacket ?? defaults.auto_redpacket,
      danmu_threshold: cfg.danmu_threshold ?? defaults.danmu_threshold,
      notification: { ...defaults.notification, ...cfg.notification },
      voice_notification: { ...defaults.voice_notification, ...cfg.voice_notification },
      saveStatus: 'idle',
    }
  })
}

function NotificationSection({
  label,
  value,
  onChange,
}: {
  label: string
  value: NotificationSub
  onChange: (v: NotificationSub) => void
}) {
  const { t } = useTranslation()
  const subKeys: (keyof Omit<NotificationSub, 'enabled'>)[] = ['signin', 'problem', 'call', 'danmu', 'red_packet']

  return (
    <div className="notif-section">
      <div className="form-row">
        <label className="form-label">{label}</label>
        <div className="toggle-group">
          <button
            className={`toggle-option ${value.enabled ? 'selected' : ''}`}
            onClick={() => onChange({ ...value, enabled: true })}
          >
            {t('common.on')}
          </button>
          <button
            className={`toggle-option ${!value.enabled ? 'selected' : ''}`}
            onClick={() => onChange({ ...value, enabled: false })}
          >
            {t('common.off')}
          </button>
        </div>
      </div>
      {value.enabled && (
        <div className="notif-suboptions">
          {subKeys.map((key) => (
            <label key={key} className="notif-sub-item">
              <input
                type="checkbox"
                checked={value[key]}
                onChange={(e) => onChange({ ...value, [key]: e.target.checked })}
              />
              <span>{t(`settings.notif_${key}`)}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  )
}

function QuizModeSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: string
  options: { value: string; label: string }[]
  onChange: (v: string) => void
}) {
  return (
    <div className="form-row">
      <label className="form-label">{label}</label>
      <select className="form-select" value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  )
}

export default function Settings() {
  const { t } = useTranslation()
  const { addToast } = useToast()
  const [courses, setCourses] = useState<CourseState[]>([])
  const [loading, setLoading] = useState(true)
  const [ai, setAi] = useState<AISettings>({ keys: [], active_key: -1, fallback_keys: true })
  const [newKey, setNewKey] = useState<AIKeyEntry>({
    name: '',
    provider: 'qwen',
    key: '',
    base_url: '',
    model: '',
  })
  const [addingKey, setAddingKey] = useState(false)
  const [testingKey, setTestingKey] = useState<number | null>(null)
  const [testImageFile, setTestImageFile] = useState<File | null>(null)
  const [audioConfig, setAudioConfig] = useState({ enabled: false })
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [uploadingAudio, setUploadingAudio] = useState(false)
  const [audioExists, setAudioExists] = useState(false)
  const [appliedAllFrom, setAppliedAllFrom] = useState<string | null>(null)
  const [defaults, setDefaults] = useState<CourseConfig | null>(null)
  const savedCoursesRef = useRef<Record<string, string>>({})
  const [answerQueue, setAnswerQueue] = useState<Array<{page: string, answer: string, type: string}>>([])
  const [newAnswer, setNewAnswer] = useState({page: '', answer: '', type: 'single'})
  const [queueExpanded, setQueueExpanded] = useState(true)

  const reloadAi = () =>
    fetch('/api/ai/settings').then((r) => r.json()).then(setAi).catch(() => { })

  const reloadAnswerQueue = () =>
    fetch('/api/answer/queue').then((r) => r.json()).then((data) => setAnswerQueue(data.queue)).catch(() => { })

  const handleAddAnswer = async () => {
    if (!newAnswer.answer.trim()) return
    try {
      const resp = await fetch('/api/answer/queue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAnswer),
      })
      if (!resp.ok) throw new Error('Failed')
      const typeLabel = newAnswer.type === 'single'
        ? t('settings.singleChoice')
        : newAnswer.type === 'multiple'
          ? t('settings.multipleChoice')
          : t('settings.shortAnswer')
      const pageLabel = newAnswer.page
        ? `${t('settings.pptPage')}: ${newAnswer.page}`
        : ''
      const detail = [pageLabel, typeLabel, `${t('settings.answer')}: ${newAnswer.answer}`].filter(Boolean).join(' | ')
      addToast('success', `${t('settings.addedToQueue')}: ${detail}`)
      setNewAnswer({ page: '', answer: '', type: 'single' })
      await reloadAnswerQueue()
    } catch {
      addToast('error', t('settings.addToQueueFailed'))
    }
  }

  const handleRemoveAnswer = async (index: number) => {
    try {
      await fetch(`/api/answer/queue/${index}`, { method: 'DELETE' })
      await reloadAnswerQueue()
    } catch { }
  }

  const handleClearQueue = async () => {
    if (answerQueue.length === 0) return
    try {
      await fetch('/api/answer/queue', { method: 'DELETE' })
      await reloadAnswerQueue()
    } catch { }
  }

  useEffect(() => {
    Promise.all([
      fetch('/api/courses/all').then((r) => r.json()),
      fetch('/api/courses/settings').then((r) => r.json()),
      fetch('/api/ai/settings').then((r) => r.json()),
      fetch('/api/courses/defaults').then((r) => r.json()),
      fetch('/api/audio/settings').then((r) => r.json()),
      fetch('/api/audio/exists').then((r) => r.json()),
      fetch('/api/answer/queue').then((r) => r.json()),
    ])
      .then(([allCourses, settings, aiSettings, defs, audioSet, audioExistsData, answerQueueData]) => {
        setDefaults(defs)
        const built = buildCourseStates(allCourses, settings, defs)
        setCourses(built)
        const snap: Record<string, string> = {}
        for (const c of built) snap[c.courseId] = courseFingerprint(c)
        savedCoursesRef.current = snap
        setAi(aiSettings)
        setAudioConfig({ enabled: !!audioSet.enabled })
        setAudioExists(!!audioExistsData.exists)
        setAnswerQueue(answerQueueData.queue || [])
      })
      .catch(() => { })
      .finally(() => setLoading(false))
  }, [])

  function courseFingerprint(c: CourseState): string {
    const { courseId: _, name: __, saveStatus: ___, ...rest } = c
    return JSON.stringify(rest)
  }

  function isDirty(course: CourseState): boolean {
    return courseFingerprint(course) !== savedCoursesRef.current[course.courseId]
  }

  const handleAddKey = async () => {
    if (!newKey.name.trim() || !newKey.key.trim()) return
    if (newKey.provider === 'openai_compat') {
      if (!newKey.base_url?.trim() || !newKey.model?.trim()) return
    }
    setAddingKey(true)
    try {
      const payload: Record<string, string> = {
        name: newKey.name.trim(),
        provider: newKey.provider,
        key: newKey.key.trim(),
      }
      if (newKey.provider === 'openai_compat') {
        payload.base_url = newKey.base_url!.trim()
        payload.model = newKey.model!.trim()
      }
      const resp = await fetch('/api/ai/keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!resp.ok) throw new Error('Add failed')
      setNewKey({ name: '', provider: 'qwen', key: '', base_url: '', model: '' })
      await reloadAi()
    } catch { }
    setAddingKey(false)
  }

  const handleDeleteKey = async (index: number) => {
    await fetch(`/api/ai/keys/${index}`, { method: 'DELETE' })
    await reloadAi()
  }

  const handleSetActiveKey = async (index: number) => {
    await fetch('/api/ai/active', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ active_key: index }),
    })
    await reloadAi()
  }

  const handleToggleFallback = async (enabled: boolean) => {
    await fetch('/api/ai/fallback', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fallback_keys: enabled }),
    })
    await reloadAi()
  }

  const handleTestKey = async (index: number) => {
    const entry = ai.keys[index]
    setTestingKey(index)
    try {
      const formData = new FormData()
      formData.append('provider', entry.provider)
      formData.append('key_index', index.toString())
      if (testImageFile) {
        formData.append('image', testImageFile)
      }
      
      const resp = await fetch('/api/ai/test', {
        method: 'POST',
        body: formData,
      })
      const data = await resp.json()
      if (data.ok) {
        alert(t('settings.testSuccess') + ':\n' + data.message)
      } else {
        alert(t('settings.testFailed') + ':\n' + data.error)
      }
    } catch (e: any) {
      alert(t('settings.testFailed') + ':\n' + e.message)
    } finally {
      setTestingKey(null)
    }
  }

  const handleAudioUpload = async () => {
    if (!audioFile) return
    setUploadingAudio(true)
    const formData = new FormData()
    formData.append('file', audioFile)
    try {
      const resp = await fetch('/api/audio/upload', {
        method: 'POST',
        body: formData,
      })
      if (resp.ok) {
        alert(t('settings.uploadSuccess') || 'Upload successful')
        setAudioFile(null)
        setAudioExists(true)
      } else {
        alert(t('settings.uploadFailed') || 'Upload failed')
      }
    } catch (e: any) {
      alert((t('settings.uploadFailed') || 'Upload failed') + ': ' + e.message)
    } finally {
      setUploadingAudio(false)
    }
  }

  const handleAudioToggle = async (enabled: boolean) => {
    setAudioConfig({ enabled })
    await fetch('/api/audio/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    })
  }

  const updateField = <K extends keyof CourseConfig>(
    courseId: string,
    field: K,
    value: CourseConfig[K]
  ) => {
    setCourses((prev) =>
      prev.map((c) =>
        c.courseId === courseId ? { ...c, [field]: value, saveStatus: 'idle' } : c
      )
    )
  }

  const handleSave = async (course: CourseState) => {
    setCourses((prev) =>
      prev.map((c) =>
        c.courseId === course.courseId ? { ...c, saveStatus: 'saving' } : c
      )
    )

    try {
      const resp = await fetch(`/api/courses/settings/${course.courseId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type1: course.type1,
          type2: course.type2,
          type3: course.type3,
          type4: course.type4,
          type5: course.type5,
          answer_delay_min: course.answer_delay_min,
          answer_delay_max: course.answer_delay_max,
          answer_last5s: course.answer_last5s,
          auto_danmu: course.auto_danmu,
          auto_redpacket: course.auto_redpacket,
          danmu_threshold: course.danmu_threshold,
          notification: course.notification,
          voice_notification: course.voice_notification,
        }),
      })
      if (!resp.ok) throw new Error('Save failed')
      savedCoursesRef.current[course.courseId] = courseFingerprint(course)
      setCourses((prev) =>
        prev.map((c) =>
          c.courseId === course.courseId ? { ...c, saveStatus: 'saved' } : c
        )
      )
      setTimeout(() => {
        setCourses((prev) =>
          prev.map((c) =>
            c.courseId === course.courseId ? { ...c, saveStatus: 'idle' } : c
          )
        )
      }, 2000)
    } catch {
      setCourses((prev) =>
        prev.map((c) =>
          c.courseId === course.courseId ? { ...c, saveStatus: 'error' } : c
        )
      )
    }
  }

  const applyToAll = async (source: CourseState) => {
    const payload = {
      type1: source.type1,
      type2: source.type2,
      type3: source.type3,
      type4: source.type4,
      type5: source.type5,
      answer_delay_min: source.answer_delay_min,
      answer_delay_max: source.answer_delay_max,
      answer_last5s: source.answer_last5s,
      auto_danmu: source.auto_danmu,
      auto_redpacket: source.auto_redpacket,
      danmu_threshold: source.danmu_threshold,
      notification: source.notification,
      voice_notification: source.voice_notification,
    }
    const results = await Promise.all(
      courses.map((c) =>
        fetch(`/api/courses/settings/${c.courseId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        }).then((r) => r.ok)
      )
    )
    if (results.every(Boolean)) {
      setCourses((prev) => {
        const updated = prev.map((c) => ({
          ...c,
          ...payload,
          notification: { ...payload.notification },
          voice_notification: { ...payload.voice_notification },
          saveStatus: 'idle' as const,
        }))
        for (const c of updated) savedCoursesRef.current[c.courseId] = courseFingerprint(c)
        return updated
      })
      setAppliedAllFrom(source.courseId)
      setTimeout(() => setAppliedAllFrom(null), 2000)
    }
  }

  const resetToDefault = (courseId: string) => {
    if (!defaults) return
    setCourses((prev) =>
      prev.map((c) =>
        c.courseId === courseId
          ? {
            ...c,
            type1: defaults.type1,
            type2: defaults.type2,
            type3: defaults.type3,
            type4: defaults.type4,
            type5: defaults.type5,
            answer_delay_min: defaults.answer_delay_min,
            answer_delay_max: defaults.answer_delay_max,
            answer_last5s: defaults.answer_last5s,
            auto_danmu: defaults.auto_danmu,
            auto_redpacket: defaults.auto_redpacket,
            danmu_threshold: defaults.danmu_threshold,
            notification: { ...defaults.notification },
            voice_notification: { ...defaults.voice_notification },
            saveStatus: 'idle',
          }
          : c
      )
    )
  }

  const modeOptions = (hasAi: boolean) => {
    const opts = [
      { value: 'random', label: t('settings.random') },
      { value: 'off', label: t('settings.disabled') },
    ]
    if (hasAi) {
      opts.splice(1, 0, { value: 'ai', label: 'AI' })
      opts.splice(1, 0, { value: 'queue', label: t('settings.answerQueue') || 'Answer Queue' })
    }
    return opts
  }

  if (loading) {
    return (
      <div className="page">
        <h1 className="page-title">{t('settings.title')}</h1>
        <p className="empty-message">{t('common.loading')}</p>
      </div>
    )
  }

  return (
    <div className="page">
      <h1 className="page-title">{t('settings.title')}</h1>

      {/* AI Settings */}
      <section className="settings-section">
        <h2 className="settings-section-title">{t('settings.aiSettings')}</h2>

        <div className="card">
          {ai.keys.length > 0 && (
            <>
              <div className="form-row" style={{ padding: '0 16px', marginBottom: 16 }}>
                <div style={{ flex: 1 }}>
                  <label className="form-label">{t('settings.testImagePlaceholder') || 'Upload test image'} *</label>
                  <p className="form-help" style={{ fontSize: '12px', color: '#666', marginTop: '4px', marginBottom: '8px' }}>
                    {t('settings.testImageHint') || 'Please upload an image containing a question for AI testing. Image is required.'}
                  </p>
                  <input
                    type="file"
                    className="form-input"
                    accept="image/*"
                    onChange={(e) => {
                      if (e.target.files && e.target.files.length > 0) {
                        setTestImageFile(e.target.files[0])
                      } else {
                        setTestImageFile(null)
                      }
                    }}
                  />
                </div>
              </div>

              <div className="ai-key-list">
                {ai.keys.map((entry, idx) => (
                  <div key={idx} className={`ai-key-item ${idx === ai.active_key ? 'ai-key-active' : ''}`}>
                    <div className="ai-key-info">
                      <span className="ai-key-name">{entry.name}</span>
                      <span className="ai-key-provider">
                        {entry.provider === 'openai_compat'
                          ? t('settings.openaiCompat')
                          : (PROVIDER_LABELS[entry.provider] ?? entry.provider)}
                        {entry.provider === 'openai_compat' && entry.model
                          ? ` · ${entry.model}`
                          : ''}
                      </span>
                      {entry.provider === 'openai_compat' && entry.base_url && (
                        <span className="ai-key-meta" style={{ fontSize: 12, opacity: 0.85 }}>
                          {entry.base_url}
                        </span>
                      )}
                      <span className="ai-key-masked">{entry.key}</span>
                    </div>
                    <div className="ai-key-actions">
                      <button
                        className={`btn btn-sm ${idx === ai.active_key ? 'btn-success' : 'btn-secondary'}`}
                        onClick={() => handleSetActiveKey(idx)}
                      >
                        {idx === ai.active_key ? t('settings.inUse') : t('settings.use')}
                      </button>
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => handleTestKey(idx)}
                        disabled={testingKey === idx || !testImageFile}
                      >
                        {testingKey === idx ? t('settings.testing') || 'Testing...' : t('settings.test') || 'Test'}
                      </button>
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDeleteKey(idx)}
                      >
                        {t('settings.delete')}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {ai.keys.length > 1 && (
            <div className="form-row" style={{ padding: '0 16px', marginBottom: 8 }}>
              <label className="form-label">
                {t('settings.fallbackKeys')}
                <span className="tooltip-trigger" data-tooltip={t('settings.fallbackKeysDesc')}>?</span>
              </label>
              <div className="toggle-group">
                <button
                  className={`toggle-option ${ai.fallback_keys ? 'selected' : ''}`}
                  onClick={() => handleToggleFallback(true)}
                >
                  {t('common.on')}
                </button>
                <button
                  className={`toggle-option ${!ai.fallback_keys ? 'selected' : ''}`}
                  onClick={() => handleToggleFallback(false)}
                >
                  {t('common.off')}
                </button>
              </div>
            </div>
          )}

          <div
            className="ai-add-form"
            style={
              newKey.provider === 'openai_compat'
                ? { flexDirection: 'column', alignItems: 'stretch' }
                : undefined
            }
          >
            <div
              style={{
                display: 'flex',
                gap: 10,
                alignItems: 'center',
                width: '100%',
                flexWrap: 'wrap',
              }}
            >
              <div className="ai-add-fields" style={{ flex: 1, minWidth: 0 }}>
                <input
                  type="text"
                  className="form-input"
                  value={newKey.name}
                  placeholder={t('settings.keyNamePlaceholder')}
                  onChange={(e) => setNewKey({ ...newKey, name: e.target.value })}
                />
                <select
                  className="form-select"
                  value={newKey.provider}
                  onChange={(e) => {
                    const provider = e.target.value
                    setNewKey({
                      ...newKey,
                      provider,
                      base_url: provider === 'openai_compat' ? newKey.base_url || '' : '',
                      model: provider === 'openai_compat' ? newKey.model || '' : '',
                    })
                  }}
                >
                  <option value="google">Google</option>
                  <option value="qwen">ModelScope</option>
                  <option value="dashscope">Aliyun DashScope</option>
                  <option value="moonshot">Moonshot (KIMI)</option>
                  <option value="openai_compat">{t('settings.openaiCompat')}</option>
                </select>
                <input
                  type="password"
                  className="form-input"
                  value={newKey.key}
                  placeholder={t('settings.apiKeyPlaceholder')}
                  onChange={(e) => setNewKey({ ...newKey, key: e.target.value })}
                />
              </div>
              <button
                className="btn btn-primary"
                style={{ flexShrink: 0 }}
                onClick={handleAddKey}
                disabled={
                  addingKey
                  || !newKey.name.trim()
                  || !newKey.key.trim()
                  || (newKey.provider === 'openai_compat'
                    && (!newKey.base_url?.trim() || !newKey.model?.trim()))
                }
              >
                {addingKey ? t('settings.applying') : t('settings.addKey')}
              </button>
            </div>
            {newKey.provider === 'openai_compat' && (
              <div className="ai-add-fields" style={{ width: '100%', marginTop: 8 }}>
                <input
                  type="text"
                  className="form-input"
                  value={newKey.base_url ?? ''}
                  placeholder={t('settings.openaiBaseUrlPlaceholder')}
                  onChange={(e) => setNewKey({ ...newKey, base_url: e.target.value })}
                  autoComplete="off"
                />
                <input
                  type="text"
                  className="form-input"
                  value={newKey.model ?? ''}
                  placeholder={t('settings.openaiModelPlaceholder')}
                  onChange={(e) => setNewKey({ ...newKey, model: e.target.value })}
                  autoComplete="off"
                />
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Answer Queue Settings */}
      <section className="settings-section">
        <h2 className="settings-section-title">{t('settings.answerQueue') || 'Answer Queue'}</h2>
        <div className="card">
          <div className="form-row">
            <label className="form-label">{t('settings.pptPage') || 'PPT Page'}</label>
            <input
              type="text"
              className="form-input"
              placeholder={t('settings.enterPptPage') || 'Enter PPT page number (e.g., 5)'}
              value={newAnswer.page}
              onChange={(e) => setNewAnswer({...newAnswer, page: e.target.value})}
            />
          </div>
          <div className="form-row">
            <label className="form-label">{t('settings.questionType') || 'Question Type'}</label>
            <select
              className="form-input"
              value={newAnswer.type}
              onChange={(e) => {
                const newType = e.target.value;
                // Reset answer when changing question type
                if (newType === 'short') {
                  setNewAnswer({...newAnswer, type: newType, answer: ''});
                } else {
                  setNewAnswer({...newAnswer, type: newType, answer: ''});
                }
              }}
            >
              <option value="single">{t('settings.singleChoice') || 'Single Choice'}</option>
              <option value="multiple">{t('settings.multipleChoice') || 'Multiple Choice'}</option>
              <option value="short">{t('settings.shortAnswer') || 'Short Answer'}</option>
            </select>
          </div>
          
          {/* Choice options for single and multiple choice */}
          {newAnswer.type !== 'short' && (
            <div className="form-row">
              <label className="form-label">{t('settings.answer') || 'Answer'}</label>
              <div className="option-buttons">
                {['A', 'B', 'C', 'D', 'E', 'F'].map((option) => (
                  <button
                    key={option}
                    className={`option-btn ${newAnswer.type === 'single' && newAnswer.answer === option ? 'selected' : ''} ${newAnswer.type === 'multiple' && newAnswer.answer.split(',').includes(option) ? 'selected' : ''}`}
                    onClick={() => {
                      if (newAnswer.type === 'single') {
                        setNewAnswer({...newAnswer, answer: option});
                      } else {
                        const currentAnswers = newAnswer.answer ? newAnswer.answer.split(',') : [];
                        const newAnswers = currentAnswers.includes(option)
                          ? currentAnswers.filter(a => a !== option)
                          : [...currentAnswers, option].sort();
                        setNewAnswer({...newAnswer, answer: newAnswers.join(',')});
                      }
                    }}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {/* Text input for short answer */}
          {newAnswer.type === 'short' && (
            <div className="form-row">
              <label className="form-label">{t('settings.answer') || 'Answer'}</label>
              <input
                type="text"
                className="form-input"
                placeholder={t('settings.enterAnswer') || 'Enter answer text'}
                value={newAnswer.answer}
                onChange={(e) => setNewAnswer({...newAnswer, answer: e.target.value})}
              />
            </div>
          )}
          <div className="form-row">
            <button
              className="btn btn-primary"
              onClick={handleAddAnswer}
              disabled={!newAnswer.answer.trim()}
            >
              {t('settings.addToQueue') || 'Add to Queue'}
            </button>
            <button
              className="btn btn-danger"
              onClick={handleClearQueue}
              disabled={answerQueue.length === 0}
              style={{ marginLeft: '10px' }}
            >
              {t('settings.clearQueue') || 'Clear Queue'}
            </button>
          </div>
          
          {answerQueue.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h3>{t('settings.queueItems') || 'Queue Items'} ({answerQueue.length})</h3>
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={() => setQueueExpanded(!queueExpanded)}
                >
                  {queueExpanded ? '▼' : '▶'}
                </button>
              </div>
              {queueExpanded && (
                <div className="answer-queue-table">
                  <div className="answer-queue-table-header">
                    <div className="answer-queue-table-cell">{t('settings.pptPage') || 'PPT Page'}</div>
                    <div className="answer-queue-table-cell">{t('settings.questionType') || 'Question Type'}</div>
                    <div className="answer-queue-table-cell">{t('settings.answer') || 'Answer'}</div>
                    <div className="answer-queue-table-cell">{t('settings.actions') || 'Actions'}</div>
                  </div>
                  <div className="answer-queue-table-body">
                    {answerQueue.map((item, idx) => (
                      <div key={idx} className="answer-queue-table-row">
                        <div className="answer-queue-table-cell">{item.page || '-'}</div>
                        <div className="answer-queue-table-cell">
                          {item.type === 'single' ? (t('settings.singleChoice') || 'Single Choice') :
                           item.type === 'multiple' ? (t('settings.multipleChoice') || 'Multiple Choice') :
                           (t('settings.shortAnswer') || 'Short Answer')}
                        </div>
                        <div className="answer-queue-table-cell">{item.answer}</div>
                        <div className="answer-queue-table-cell">
                          <button
                            className="btn btn-sm btn-danger"
                            onClick={() => handleRemoveAnswer(idx)}
                          >
                            {t('settings.remove') || 'Remove'}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Custom Audio Settings */}
      <section className="settings-section">
        <h2 className="settings-section-title">{t('settings.customAudioSettings') || 'Custom Audio Notification'}</h2>
        <div className="card">
          <div className="form-row">
            <label className="form-label">{t('settings.enableCustomAudio') || 'Enable Custom Audio (Overrides TTS)'}</label>
            <div className="toggle-group">
              <button
                className={`toggle-option ${audioConfig.enabled ? 'selected' : ''}`}
                onClick={() => handleAudioToggle(true)}
              >
                {t('common.on')}
              </button>
              <button
                className={`toggle-option ${!audioConfig.enabled ? 'selected' : ''}`}
                onClick={() => handleAudioToggle(false)}
              >
                {t('common.off')}
              </button>
            </div>
          </div>
          <div className="ai-add-form" style={{ marginTop: '16px' }}>
            <div className="ai-add-fields">
              <input
                type="file"
                className="form-input"
                accept=".mp3,.wav,.ogg,.m4a"
                onChange={(e) => {
                  if (e.target.files && e.target.files.length > 0) {
                    setAudioFile(e.target.files[0])
                  }
                }}
              />
            </div>
            {audioExists && !audioFile && (
              <div className="audio-status" style={{ marginBottom: '8px', padding: '8px', backgroundColor: '#e8f5e9', borderRadius: '4px', color: '#2e7d32' }}>
                ✓ {t('settings.audioUploaded') || 'Audio file uploaded'}
              </div>
            )}
            <button
              className="btn btn-primary"
              onClick={handleAudioUpload}
              disabled={uploadingAudio || !audioFile}
            >
              {uploadingAudio ? t('settings.uploading') || 'Uploading...' : t('settings.upload') || 'Upload Audio'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => {
                const audio = new Audio(`/api/audio/custom?t=${Date.now()}`)
                audio.play().catch((e) => alert('No custom audio found or play failed: ' + e.message))
              }}
            >
              {t('settings.testAudio') || 'Play/Test'}
            </button>
          </div>
        </div>
      </section>

      {/* Course Settings */}
      <section className="settings-section">
        <h2 className="settings-section-title">{t('settings.courseSettings')}</h2>

        {courses.length === 0 ? (
          <div className="card">
            <p className="empty-message">{t('settings.noCourses')}</p>
          </div>
        ) : (
          <div className="course-grid">
            {courses.map((course) => (
              <div key={course.courseId} className="course-card">
                <div className="course-card-header">
                  <h3 className="course-card-title">
                    {course.name || course.courseId}
                  </h3>
                </div>

                <div className="course-card-body">
                  {/* Quiz Modes */}
                  <div className="settings-group">
                    <span className="settings-group-label">{t('settings.quizModes')}</span>
                    <QuizModeSelect
                      label={t('settings.type1')}
                      value={course.type1}
                      options={modeOptions(true)}
                      onChange={(v) => updateField(course.courseId, 'type1', v)}
                    />
                    <QuizModeSelect
                      label={t('settings.type2')}
                      value={course.type2}
                      options={modeOptions(true)}
                      onChange={(v) => updateField(course.courseId, 'type2', v)}
                    />
                    <QuizModeSelect
                      label={t('settings.type3')}
                      value={course.type3}
                      options={modeOptions(false)}
                      onChange={(v) => updateField(course.courseId, 'type3', v)}
                    />
                    <div className="form-row">
                      <label className="form-label">{t('settings.type4')}</label>
                      <span className="badge badge-gray">{t('settings.reserved')}</span>
                    </div>
                    <QuizModeSelect
                      label={t('settings.type5')}
                      value={course.type5}
                      options={[
                        { value: 'ai', label: 'AI' },
                        { value: 'blank', label: t('settings.blank') },
                        { value: 'off', label: t('settings.disabled') },
                      ]}
                      onChange={(v) => updateField(course.courseId, 'type5', v)}
                    />
                  </div>

                  {/* Timing */}
                  <div className="settings-group">
                    <span className="settings-group-label">{t('settings.timing')}</span>
                    <div className="form-row">
                      <label className="form-label">
                        {t('settings.answerLast5s')}
                        <span className="tooltip-trigger" data-tooltip={t('settings.answerLast5sTooltip')}>?</span>
                      </label>
                      <div className="toggle-group">
                        <button
                          className={`toggle-option ${course.answer_last5s ? 'selected' : ''}`}
                          onClick={() => updateField(course.courseId, 'answer_last5s', true)}
                        >
                          {t('common.on')}
                        </button>
                        <button
                          className={`toggle-option ${!course.answer_last5s ? 'selected' : ''}`}
                          onClick={() => updateField(course.courseId, 'answer_last5s', false)}
                        >
                          {t('common.off')}
                        </button>
                      </div>
                    </div>
                    {!course.answer_last5s && (
                      <div className="form-row">
                        <label className="form-label">
                          {t('settings.answerDelay')}
                          <span className="tooltip-trigger" data-tooltip={t('settings.answerDelayTooltip')}>?</span>
                        </label>
                        <div className="input-with-unit">
                          <input
                            type="number"
                            className="form-input-number"
                            min={1}
                            max={course.answer_delay_max - 1}
                            value={course.answer_delay_min}
                            onChange={(e) => {
                              const val = Math.max(1, parseInt(e.target.value) || 1)
                              updateField(course.courseId, 'answer_delay_min', val)
                              if (val >= course.answer_delay_max) {
                                updateField(course.courseId, 'answer_delay_max', val + 1)
                              }
                            }}
                          />
                          <span className="input-unit">{t('settings.to')}</span>
                          <input
                            type="number"
                            className="form-input-number"
                            min={course.answer_delay_min + 1}
                            max={300}
                            value={course.answer_delay_max}
                            onChange={(e) => {
                              const val = Math.max(course.answer_delay_min + 1, parseInt(e.target.value) || course.answer_delay_min + 1)
                              updateField(course.courseId, 'answer_delay_max', val)
                            }}
                          />
                          <span className="input-unit">{t('settings.seconds')}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Danmu */}
                  <div className="settings-group">
                    <span className="settings-group-label">{t('settings.danmu')}</span>
                    <div className="form-row">
                      <label className="form-label">{t('settings.autoDanmu')}</label>
                      <div className="toggle-group">
                        <button
                          className={`toggle-option ${course.auto_danmu ? 'selected' : ''}`}
                          onClick={() => updateField(course.courseId, 'auto_danmu', true)}
                        >
                          {t('common.yes')}
                        </button>
                        <button
                          className={`toggle-option ${!course.auto_danmu ? 'selected' : ''}`}
                          onClick={() => updateField(course.courseId, 'auto_danmu', false)}
                        >
                          {t('common.no')}
                        </button>
                      </div>
                    </div>
                    {course.auto_danmu && (
                      <div className="form-row form-row-sub">
                        <label className="form-label">{t('settings.danmuThreshold')}</label>
                        <div className="input-with-unit">
                          <input
                            type="number"
                            className="form-input-number"
                            min={1}
                            max={99}
                            value={course.danmu_threshold}
                            onChange={(e) =>
                              updateField(course.courseId, 'danmu_threshold', Math.max(1, parseInt(e.target.value) || 1))
                            }
                          />
                          <span className="input-unit">{t('settings.times')}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Red Packet */}
                  <div className="settings-group">
                    <span className="settings-group-label">{t('settings.redPacket')}</span>
                    <div className="form-row">
                      <label className="form-label">{t('settings.autoRedpacket')}</label>
                      <div className="toggle-group">
                        <button
                          className={`toggle-option ${course.auto_redpacket ? 'selected' : ''}`}
                          onClick={() => updateField(course.courseId, 'auto_redpacket', true)}
                        >
                          {t('common.yes')}
                        </button>
                        <button
                          className={`toggle-option ${!course.auto_redpacket ? 'selected' : ''}`}
                          onClick={() => updateField(course.courseId, 'auto_redpacket', false)}
                        >
                          {t('common.no')}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Notifications */}
                  <div className="settings-group">
                    <span className="settings-group-label">{t('settings.notifications')}</span>
                    <NotificationSection
                      label={t('settings.notification')}
                      value={course.notification}
                      onChange={(v) => updateField(course.courseId, 'notification', v)}
                    />
                    <NotificationSection
                      label={t('settings.voiceNotification')}
                      value={course.voice_notification}
                      onChange={(v) => updateField(course.courseId, 'voice_notification', v)}
                    />
                  </div>
                </div>

                <div className="course-card-footer">
                  <button
                    className="btn btn-ghost"
                    onClick={() => resetToDefault(course.courseId)}
                  >
                    {t('settings.default')}
                  </button>
                  <div className="footer-spacer" />
                  {courses.length > 1 && (
                    <button
                      className={`btn ${appliedAllFrom === course.courseId ? 'btn-success' : 'btn-secondary'}`}
                      onClick={() => applyToAll(course)}
                      disabled={appliedAllFrom !== null}
                    >
                      {appliedAllFrom === course.courseId ? t('settings.applied') : t('settings.applyToAll')}
                    </button>
                  )}
                  <button
                    className={`btn ${course.saveStatus === 'saved'
                      ? 'btn-success'
                      : course.saveStatus === 'error'
                        ? 'btn-danger'
                        : 'btn-primary'
                      }`}
                    onClick={() => handleSave(course)}
                    disabled={course.saveStatus === 'saving' || !isDirty(course)}
                  >
                    {course.saveStatus === 'saving'
                      ? t('settings.applying')
                      : course.saveStatus === 'saved'
                        ? t('settings.applied')
                        : t('settings.apply')}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

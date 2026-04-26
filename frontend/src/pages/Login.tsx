import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

type LoginStatus = 'waiting' | 'qr_ready' | 'scanning' | 'success'
type LoginMethod = 'qrcode' | 'password'

interface ServerOption {
  key: string
  label: string
  label_zh: string
}

interface LoginProps {
  onSuccess: () => void
}

declare global {
  interface Window {
    TencentCaptcha: new (
      appId: string,
      callback: (res: { ret: number; ticket: string; randstr: string }) => void,
    ) => { show: () => void; destroy: () => void }
  }
}

export default function Login({ onSuccess }: LoginProps) {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const wsRef = useRef<WebSocket | null>(null)
  const [status, setStatus] = useState<LoginStatus>('waiting')
  const [qrUrl, setQrUrl] = useState<string>('')
  const [domain, setDomain] = useState<string>('')
  const [serverOptions, setServerOptions] = useState<ServerOption[]>([])
  const domainRef = useRef<string>('')

  const [method, setMethod] = useState<LoginMethod>('qrcode')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [pwLoading, setPwLoading] = useState(false)
  const [pwError, setPwError] = useState('')

  useEffect(() => {
    fetch('/api/domain')
      .then(r => r.json())
      .then(data => {
        setDomain(data.domain)
        domainRef.current = data.domain
        setServerOptions(data.options)
        saveDomainAndConnect(data.domain)
      })
    return () => { wsRef.current?.close() }
  }, [])

  function saveDomainAndConnect(d: string) {
    fetch('/api/domain', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain: d }),
    }).then(() => { if (method === 'qrcode') connectWs() })
  }

  function handleDomainChange(newDomain: string) {
    setDomain(newDomain)
    domainRef.current = newDomain
    wsRef.current?.close()
    saveDomainAndConnect(newDomain)
  }

  function handleMethodChange(m: LoginMethod) {
    setMethod(m)
    setPwError('')
    if (m === 'qrcode') {
      saveDomainAndConnect(domainRef.current)
    } else {
      wsRef.current?.close()
    }
  }

  function connectWs() {
    setStatus('waiting')
    setQrUrl('')

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${protocol}://${window.location.host}/ws/login`)
    wsRef.current = ws

    ws.onmessage = (ev) => {
      let msg: Record<string, unknown>
      try {
        msg = JSON.parse(ev.data as string) as Record<string, unknown>
      } catch {
        return
      }

      const type = msg['type'] as string

      if (type === 'qr') {
        setQrUrl(msg['url'] as string)
        setStatus('qr_ready')
      } else if (type === 'scanning') {
        setStatus('scanning')
      } else if (type === 'success') {
        setStatus('success')
        onSuccess()
        setTimeout(() => navigate('/dashboard'), 1000)
      }
    }
  }

  const handleRefresh = () => {
    wsRef.current?.close()
    saveDomainAndConnect(domainRef.current)
  }

  function handlePasswordLogin() {
    if (!phone || !password) {
      setPwError(t('login.pwFillAll'))
      return
    }
    setPwError('')
    setPwLoading(true)

    const captcha = new window.TencentCaptcha('2091064951', (res) => {
      if (res.ret !== 0) {
        setPwLoading(false)
        return
      }

      fetch('/api/auth/password-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone,
          password,
          ticket: res.ticket,
          randstr: res.randstr,
        }),
      })
        .then(r => r.json())
        .then(data => {
          setPwLoading(false)
          if (data.ok) {
            setStatus('success')
            onSuccess()
            setTimeout(() => navigate('/dashboard'), 1000)
          } else {
            setPwError(data.error || t('login.pwFailed'))
          }
        })
        .catch(err => {
          setPwLoading(false)
          setPwError(String(err))
        })
    })
    captcha.show()
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-method-toggle">
          <button
            className={`method-tab ${method === 'qrcode' ? 'active' : ''}`}
            onClick={() => handleMethodChange('qrcode')}
            disabled={status === 'success'}
          >
            {t('login.methodQR')}
          </button>
          <button
            className={`method-tab ${method === 'password' ? 'active' : ''}`}
            onClick={() => handleMethodChange('password')}
            disabled={status === 'success'}
          >
            {t('login.methodPassword')}
          </button>
        </div>

        <div className="login-form-group">
          <label className="form-label">{t('login.server')}</label>
          <select
            className="form-select"
            value={domain}
            onChange={e => handleDomainChange(e.target.value)}
            disabled={status === 'waiting' || status === 'scanning' || status === 'success'}
          >
            {serverOptions.map(opt => (
              <option key={opt.key} value={opt.key}>
                {i18n.language.startsWith('zh') ? opt.label_zh : opt.label}
              </option>
            ))}
          </select>
        </div>

        {method === 'qrcode' ? (
          <>
            <div className="qr-wrapper">
              {status === 'waiting' && (
                <div className="qr-placeholder">
                  <div className="spinner" />
                  <span>{t('login.waiting')}</span>
                </div>
              )}

              {(status === 'qr_ready' || status === 'scanning') && qrUrl && (
                <>
                  <img
                    src={qrUrl}
                    alt="QR Code"
                    className={`qr-image ${status === 'scanning' ? 'qr-dimmed' : ''}`}
                  />
                  {status === 'scanning' && (
                    <div className="qr-overlay">
                      <div className="spinner spinner-white" />
                      <span>{t('login.scanning')}</span>
                    </div>
                  )}
                </>
              )}

              {status === 'success' && (
                <div className="qr-placeholder qr-success">
                  <div className="success-icon">✓</div>
                  <span>{t('login.success')}</span>
                </div>
              )}
            </div>

            {status === 'qr_ready' && (
              <button className="btn btn-secondary" onClick={handleRefresh}>
                {t('login.refresh')}
              </button>
            )}
          </>
        ) : (
          <>
            {status === 'success' ? (
              <div className="qr-wrapper">
                <div className="qr-placeholder qr-success">
                  <div className="success-icon">✓</div>
                  <span>{t('login.success')}</span>
                </div>
              </div>
            ) : (
              <div className="login-form-group">
                <div className="login-form-group">
                  <input
                    type="tel"
                    className="form-input"
                    placeholder={t('login.phonePlaceholder')}
                    value={phone}
                    onChange={e => setPhone(e.target.value)}
                    disabled={pwLoading}
                  />
                </div>
                <div className="login-form-group">
                  <input
                    type="password"
                    className="form-input"
                    placeholder={t('login.passwordPlaceholder')}
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    disabled={pwLoading}
                    onKeyDown={e => { if (e.key === 'Enter') handlePasswordLogin() }}
                  />
                </div>
                {pwError && (
                  <p className="login-error">{pwError}</p>
                )}
                <button
                  className="btn btn-primary login-btn-full"
                  onClick={handlePasswordLogin}
                  disabled={pwLoading}
                >
                  {pwLoading ? t('login.pwLoggingIn') : t('login.pwLogin')}
                </button>
              </div>
            )}
          </>
        )}

        <p className="login-note">{t('login.note')}</p>
      </div>
    </div>
  )
}

import { type ReactNode, useEffect, useState } from 'react'
import { Routes, Route, NavLink, Navigate, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import { ToastProvider } from './components/Toast'

interface AuthState {
  checked: boolean
  loggedIn: boolean
  user: Record<string, unknown> | null
}

function ProtectedRoute({
  auth,
  children,
}: {
  auth: AuthState
  children: ReactNode
}) {
  if (!auth.checked) {
    return <div className="loading-screen">Loading...</div>
  }
  if (!auth.loggedIn) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

export default function App() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const [auth, setAuth] = useState<AuthState>({
    checked: false,
    loggedIn: false,
    user: null,
  })

  useEffect(() => {
    fetch('/api/auth/status')
      .then((r) => r.json())
      .then((data) => {
        setAuth({ checked: true, loggedIn: data.logged_in, user: data.user })
      })
      .catch(() => {
        setAuth({ checked: true, loggedIn: false, user: null })
      })
  }, [])

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' })
    setAuth({ checked: true, loggedIn: false, user: null })
    navigate('/login')
  }

  const toggleLanguage = () => {
    const next = i18n.language.startsWith('zh') ? 'en' : 'zh'
    i18n.changeLanguage(next)
  }

  const onLoginSuccess = () => {
    fetch('/api/auth/status')
      .then((r) => r.json())
      .then((data) => {
        setAuth({ checked: true, loggedIn: data.logged_in, user: data.user })
      })
      .catch(() => {})
  }

  return (
    <ToastProvider>
    <div className="app">
      <div className="sticky-header">
      <nav className="navbar">
        <div className="navbar-brand">{t('nav.brand')}</div>
        <div className="navbar-links">
          {auth.loggedIn ? (
            <>
              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  isActive ? 'nav-link active' : 'nav-link'
                }
              >
                {t('nav.dashboard')}
              </NavLink>
              <NavLink
                to="/settings"
                className={({ isActive }) =>
                  isActive ? 'nav-link active' : 'nav-link'
                }
              >
                {t('nav.settings')}
              </NavLink>
            </>
          ) : null}
        </div>
        <div className="navbar-actions">
          {auth.loggedIn && (
            <div className="navbar-user">
              <img
                className="navbar-avatar"
                src="/api/user/avatar"
                alt={String(auth.user?.name ?? '')}
                onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
              />
              <span className="navbar-username">{String(auth.user?.name ?? '')}</span>
            </div>
          )}
          <button className="btn-ghost btn-sm" onClick={toggleLanguage}>
            {i18n.language.startsWith('zh') ? 'EN' : '中文'}
          </button>
          {auth.loggedIn && (
            <button className="btn-ghost btn-sm" onClick={handleLogout}>
              {t('common.logout')}
            </button>
          )}
        </div>
      </nav>

      <div className="beta-banner">
        <strong className="beta-banner-label">{t('common.betaLabel')}</strong>
        {t('common.betaWarning')}
      </div>
      </div>

      <main className="main-content">
        <Routes>
          <Route
            path="/"
            element={
              auth.checked ? (
                auth.loggedIn ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Navigate to="/login" replace />
                )
              ) : (
                <div className="loading-screen">Loading...</div>
              )
            }
          />
          <Route
            path="/login"
            element={
              auth.checked && auth.loggedIn ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Login onSuccess={onLoginSuccess} />
              )
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute auth={auth}>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute auth={auth}>
                <Settings />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
    </ToastProvider>
  )
}

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Loader2, Check } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { Brand } from '../components/ui'

const perks = [
  'Career paths matched to your skills and interests',
  'ATS score and fixes for your resume',
  'A month-by-month plan to reach your goal',
]

export default function AuthPage({ mode = 'login' }) {
  const isLogin = mode !== 'register'
  const { login, register, isAuth } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [show, setShow] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => { if (isAuth) navigate('/dashboard', { replace: true }) }, [isAuth, navigate])
  useEffect(() => { setError('') }, [mode])

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    if (!form.email || !form.password) { setError('Please fill in all fields.'); return }
    if (!isLogin && !form.name) { setError('Please enter your name.'); return }
    if (!isLogin && form.password.length < 8) { setError('Password must be at least 8 characters.'); return }
    setLoading(true)
    try {
      if (isLogin) await login(form.email.trim(), form.password)
      else await register(form.name.trim(), form.email.trim(), form.password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="flex flex-col px-6 py-8 sm:px-12">
        <Brand />
        <div className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center py-10">
          <h1 className="font-serif text-4xl">{isLogin ? 'Welcome back' : 'Create your account'}</h1>
          <p className="mt-2 text-sm text-muted">
            {isLogin ? 'Sign in to continue planning your career.' : 'Free to start. No credit card needed.'}
          </p>

          <form onSubmit={submit} className="mt-8 space-y-4">
            {!isLogin && (
              <div>
                <label className="label" htmlFor="name">Full name</label>
                <input id="name" className="input" value={form.name} onChange={set('name')} placeholder="Your name" autoComplete="name" />
              </div>
            )}
            <div>
              <label className="label" htmlFor="email">Email</label>
              <input id="email" type="email" className="input" value={form.email} onChange={set('email')} placeholder="you@example.com" autoComplete="email" />
            </div>
            <div>
              <label className="label" htmlFor="password">Password</label>
              <div className="relative">
                <input
                  id="password"
                  type={show ? 'text' : 'password'}
                  className="input pr-10"
                  value={form.password}
                  onChange={set('password')}
                  placeholder={isLogin ? 'Your password' : 'At least 8 characters'}
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                />
                <button type="button" onClick={() => setShow((s) => !s)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink" aria-label="Toggle password visibility">
                  {show ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-600 dark:text-red-400">{error}</p>}

            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading && <Loader2 size={16} className="animate-spin" />}
              {isLogin ? 'Sign in' : 'Create account'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-muted">
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <Link to={isLogin ? '/register' : '/login'} className="font-medium text-accent hover:underline">
              {isLogin ? 'Sign up' : 'Sign in'}
            </Link>
          </p>
        </div>
      </div>

      <div className="relative hidden items-center justify-center overflow-hidden bg-subtle lg:flex">
        <div className="bg-grid absolute inset-0" />
        <div className="relative max-w-md px-10">
          <p className="font-serif text-4xl leading-tight">Know where you're going, and how to get there.</p>
          <ul className="mt-8 space-y-3">
            {perks.map((p) => (
              <li key={p} className="flex items-start gap-3 text-sm text-muted">
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-accent text-accent-ink"><Check size={12} /></span>
                {p}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

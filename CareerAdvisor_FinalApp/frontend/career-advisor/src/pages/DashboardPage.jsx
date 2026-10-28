import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Compass, FileText, MessageSquare, Map, ArrowUpRight, Target } from 'lucide-react'
import { api } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import { Spinner, ErrorBox, Tags } from '../components/ui'

const actions = [
  { to: '/career', icon: Compass, title: 'Find career paths', text: 'Roles that match your skills, with salary ranges.' },
  { to: '/resume', icon: FileText, title: 'Analyze resume', text: 'Get your ATS score and what to fix.' },
  { to: '/chat', icon: MessageSquare, title: 'Ask the advisor', text: 'Questions about careers, skills or interviews.' },
  { to: '/roadmap', icon: Map, title: 'Build a roadmap', text: 'A month-by-month plan for your target role.' },
]

function completeness(p) {
  const checks = [p.full_name, p.degree, p.department, p.skills?.length, p.interests?.length, p.career_goals]
  return Math.round((checks.filter(Boolean).length / checks.length) * 100)
}

export default function DashboardPage() {
  const { user } = useAuth()
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try { setProfile(await api.get('/profile')) } catch (e) { setError(e.message) } finally { setLoading(false) }
  }, [])
  useEffect(() => { load() }, [load])

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'
  const pct = profile ? completeness(profile) : 0

  return (
    <div className="page">
      <p className="text-sm text-muted">{greeting}</p>
      <h1 className="font-serif text-4xl md:text-5xl">{user?.name?.split(' ')[0] || 'there'}</h1>

      <div className="mt-8">
        {loading ? <Spinner /> : error ? <ErrorBox message={error} onRetry={load} /> : (
          <div className="grid gap-4 md:grid-cols-3">
            <div className="card p-6 md:col-span-2">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold">Your profile</h2>
                <span className="text-sm text-muted">{pct}% complete</span>
              </div>
              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-subtle">
                <div className="h-full rounded-full bg-accent transition-all" style={{ width: `${pct}%` }} />
              </div>
              <div className="mt-6">
                <p className="label">Skills</p>
                {profile.skills?.length ? <Tags items={profile.skills} /> : <p className="text-sm text-muted">No skills added yet.</p>}
              </div>
              <Link to="/profile" className="mt-6 inline-flex items-center gap-1 text-sm font-medium text-accent hover:underline">
                {pct < 100 ? 'Complete your profile' : 'Edit profile'} <ArrowUpRight size={14} />
              </Link>
            </div>

            <div className="card p-6">
              <h2 className="flex items-center gap-2 text-sm font-semibold"><Target size={16} className="text-accent" /> Career goal</h2>
              <p className="mt-3 text-sm leading-relaxed text-muted">
                {profile.career_goals || 'You have not set a goal yet. Add one in your profile or let the career finder suggest some.'}
              </p>
            </div>
          </div>
        )}
      </div>

      <h2 className="mb-4 mt-12 text-sm font-semibold">Where to next</h2>
      <div className="grid gap-4 sm:grid-cols-2">
        {actions.map(({ to, icon: Icon, title, text }) => (
          <Link key={to} to={to} className="card group flex items-start gap-4 p-5 transition hover:border-accent/50">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent-soft text-accent"><Icon size={20} /></div>
            <div className="flex-1">
              <p className="font-medium">{title}</p>
              <p className="mt-0.5 text-sm text-muted">{text}</p>
            </div>
            <ArrowUpRight size={16} className="text-muted transition group-hover:text-accent" />
          </Link>
        ))}
      </div>
    </div>
  )
}

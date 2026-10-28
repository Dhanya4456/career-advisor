import { useCallback, useEffect, useState } from 'react'
import { User, Loader2, Check, X } from 'lucide-react'
import { api } from '../utils/api'
import { PageHeader, Spinner, ErrorBox } from '../components/ui'

const empty = {
  full_name: '', email: '', degree: '', department: '', cgpa: '', years_of_experience: 0,
  career_goals: '', linkedin_url: '', github_url: '', skills: [], interests: [],
}

function normalize(d) {
  return {
    ...empty, ...d,
    cgpa: d.cgpa ?? '',
    years_of_experience: d.years_of_experience ?? 0,
    skills: Array.isArray(d.skills) ? d.skills : [],
    interests: Array.isArray(d.interests) ? d.interests : [],
    full_name: d.full_name || '', degree: d.degree || '', department: d.department || '',
    career_goals: d.career_goals || '', linkedin_url: d.linkedin_url || '', github_url: d.github_url || '',
  }
}

function TagInput({ label, items, onChange, placeholder }) {
  const [v, setV] = useState('')
  const add = () => {
    const t = v.trim().replace(/,$/, '')
    if (t && !items.some((i) => i.toLowerCase() === t.toLowerCase())) onChange([...items, t])
    setV('')
  }
  return (
    <div>
      <label className="label">{label}</label>
      <div className="flex flex-wrap gap-1.5 rounded-xl border border-line bg-surface p-2 focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/20">
        {items.map((t) => (
          <span key={t} className="tag bg-accent-soft text-accent">
            {t}
            <button type="button" onClick={() => onChange(items.filter((i) => i !== t))} aria-label={`Remove ${t}`}><X size={12} /></button>
          </span>
        ))}
        <input
          value={v}
          onChange={(e) => setV(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); add() } else if (e.key === 'Backspace' && !v && items.length) onChange(items.slice(0, -1)) }}
          onBlur={add}
          placeholder={items.length ? '' : placeholder}
          className="min-w-[8rem] flex-1 bg-transparent px-1.5 py-1 text-sm outline-none placeholder:text-muted/70"
        />
      </div>
      <p className="mt-1 text-xs text-muted">Press Enter or comma to add.</p>
    </div>
  )
}

export default function ProfilePage() {
  const [form, setForm] = useState(empty)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setLoadError('')
    try { setForm(normalize(await api.get('/profile'))) } catch (e) { setLoadError(e.message) } finally { setLoading(false) }
  }, [])
  useEffect(() => { load() }, [load])

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    setMsg(null)
    try {
      const data = await api.put('/profile', {
        full_name: form.full_name || null,
        degree: form.degree || null,
        department: form.department || null,
        cgpa: form.cgpa === '' ? null : Number(form.cgpa),
        skills: form.skills,
        interests: form.interests,
        career_goals: form.career_goals || null,
        years_of_experience: form.years_of_experience === '' ? 0 : Number(form.years_of_experience),
        linkedin_url: form.linkedin_url || null,
        github_url: form.github_url || null,
      })
      setForm(normalize(data))
      setMsg({ ok: true, text: 'Profile saved.' })
    } catch (err) {
      setMsg({ ok: false, text: err.message })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page">
      <PageHeader icon={User} title="Profile" subtitle="This is what the career finder, resume analyzer and advisor use to personalize results." />
      {loading ? <Spinner /> : loadError ? <ErrorBox message={loadError} onRetry={load} /> : (
        <form onSubmit={save} className="space-y-6">
          <div className="card grid gap-5 p-6 md:grid-cols-2 md:p-8">
            <div><label className="label">Full name</label><input className="input" value={form.full_name} onChange={set('full_name')} /></div>
            <div><label className="label">Email</label><input className="input opacity-70" value={form.email} disabled /></div>
            <div><label className="label">Degree</label><input className="input" value={form.degree} onChange={set('degree')} placeholder="e.g. B.Tech" /></div>
            <div><label className="label">Department</label><input className="input" value={form.department} onChange={set('department')} placeholder="e.g. Computer Science" /></div>
            <div><label className="label">CGPA (0–10)</label><input type="number" min="0" max="10" step="0.01" className="input" value={form.cgpa} onChange={set('cgpa')} /></div>
            <div><label className="label">Years of experience</label><input type="number" min="0" className="input" value={form.years_of_experience} onChange={set('years_of_experience')} /></div>
            <div><label className="label">LinkedIn URL</label><input className="input" value={form.linkedin_url} onChange={set('linkedin_url')} placeholder="https://linkedin.com/in/…" /></div>
            <div><label className="label">GitHub URL</label><input className="input" value={form.github_url} onChange={set('github_url')} placeholder="https://github.com/…" /></div>
            <div className="md:col-span-2"><label className="label">Career goals</label><textarea rows={3} className="input" value={form.career_goals} onChange={set('career_goals')} placeholder="Where do you want to be in a few years?" /></div>
          </div>

          <div className="card space-y-5 p-6 md:p-8">
            <TagInput label="Skills" items={form.skills} onChange={(skills) => setForm((f) => ({ ...f, skills }))} placeholder="e.g. Python, SQL" />
            <TagInput label="Interests" items={form.interests} onChange={(interests) => setForm((f) => ({ ...f, interests }))} placeholder="e.g. Data & Analytics" />
          </div>

          <div className="flex items-center justify-end gap-4">
            {msg && (
              <p className={`flex items-center gap-1.5 text-sm ${msg.ok ? 'text-accent' : 'text-red-500'}`}>
                {msg.ok && <Check size={15} />}{msg.text}
              </p>
            )}
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving && <Loader2 size={16} className="animate-spin" />} Save changes
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

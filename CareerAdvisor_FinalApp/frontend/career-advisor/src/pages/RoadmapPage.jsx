import { useState } from 'react'
import { Map, Loader2, ChevronDown, Check, RefreshCw, Award, FolderKanban } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../utils/api'
import { PageHeader, SectionTitle, ErrorBox, Tags } from '../components/ui'

const goalOptions = [
  'Become a Data Scientist', 'Learn Web Development', 'Break into Product Management',
  'Become a UX Designer', 'Learn Machine Learning', 'Start a Career in DevOps',
  'Transition to Cybersecurity', 'Become a Cloud Architect',
]
// Backend wants an integer 1–24 for duration_months.
const timeOptions = [
  { label: '4 weeks', months: 1 },
  { label: '8 weeks', months: 2 },
  { label: '12 weeks', months: 3 },
  { label: '6 months', months: 6 },
  { label: '1 year', months: 12 },
]
const levelOptions = ['Complete beginner', 'Some basics', 'Intermediate', 'Advanced']

function Choice({ options, value, onChange, getLabel = (o) => o }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => (
        <button key={getLabel(o)} type="button" onClick={() => onChange(o)} className={clsx('chip', value === o && 'chip-on')}>{getLabel(o)}</button>
      ))}
    </div>
  )
}

export default function RoadmapPage() {
  const [goal, setGoal] = useState('')
  const [customGoal, setCustomGoal] = useState('')
  const [time, setTime] = useState(timeOptions[2])
  const [level, setLevel] = useState('Some basics')
  const [loading, setLoading] = useState(false)
  const [roadmap, setRoadmap] = useState(null)
  const [error, setError] = useState('')
  const [expanded, setExpanded] = useState({})
  const [done, setDone] = useState({})

  const target = (customGoal || goal).trim()

  const generate = async () => {
    if (target.length < 2) return
    setLoading(true)
    setRoadmap(null)
    setError('')
    setDone({})
    try {
      const data = await api.post('/roadmap/generate', {
        target_role: target,
        duration_months: time.months,
        additional_context: `Current level: ${level}`,
      })
      setRoadmap(data)
      setExpanded({ 0: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const total = roadmap?.monthly_plan?.reduce((n, m) => n + (m.milestones?.length || 0), 0) || 0
  const doneCount = Object.values(done).filter(Boolean).length
  const pct = total ? Math.round((doneCount / total) * 100) : 0

  return (
    <div className="page">
      <PageHeader icon={Map} title="Learning roadmap" subtitle="A personalized, month-by-month plan for any career goal." />

      {!roadmap && (
        <div className="card space-y-7 p-6 md:p-8">
          <div>
            <p className="mb-3 text-sm font-semibold">What is your goal?</p>
            <Choice options={goalOptions} value={goal} onChange={(g) => { setGoal(g); setCustomGoal('') }} />
            <input className="input mt-4 max-w-md" placeholder="Or type your own goal" value={customGoal} onChange={(e) => { setCustomGoal(e.target.value); setGoal('') }} />
          </div>
          <div>
            <p className="mb-3 text-sm font-semibold">Where are you now?</p>
            <Choice options={levelOptions} value={level} onChange={setLevel} />
          </div>
          <div>
            <p className="mb-3 text-sm font-semibold">How long do you want to take?</p>
            <Choice options={timeOptions} value={time} onChange={setTime} getLabel={(t) => t.label} />
          </div>
          {error && <ErrorBox message={error} onRetry={generate} />}
          <div className="flex justify-end">
            <button className="btn-primary" disabled={target.length < 2 || loading} onClick={generate}>
              {loading && <Loader2 size={16} className="animate-spin" />}
              {loading ? 'Building your roadmap…' : 'Generate roadmap'}
            </button>
          </div>
        </div>
      )}

      {roadmap && (
        <div className="space-y-8">
          <div className="card p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="font-serif text-2xl">{roadmap.target_role}</h2>
                <p className="mt-1 text-sm text-muted">
                  {roadmap.duration_months} month{roadmap.duration_months > 1 ? 's' : ''}
                  {roadmap.total_skills_to_learn ? ` · ${roadmap.total_skills_to_learn} skills to learn` : ''}
                </p>
              </div>
              <button className="btn-secondary" onClick={() => setRoadmap(null)}><RefreshCw size={15} /> New roadmap</button>
            </div>
            {total > 0 && (
              <div className="mt-5">
                <div className="mb-1.5 flex justify-between text-xs text-muted"><span>{doneCount} of {total} milestones</span><span>{pct}%</span></div>
                <div className="h-1.5 overflow-hidden rounded-full bg-subtle"><div className="h-full rounded-full bg-accent transition-all" style={{ width: `${pct}%` }} /></div>
              </div>
            )}
          </div>

          <ol className="space-y-3">
            {roadmap.monthly_plan?.map((m, mi) => {
              const open = !!expanded[mi]
              return (
                <li key={mi} className="card overflow-hidden">
                  <button className="flex w-full items-center gap-4 p-5 text-left" onClick={() => setExpanded((e) => ({ ...e, [mi]: !e[mi] }))}>
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent-soft text-sm font-semibold text-accent">{m.month}</span>
                    <div className="min-w-0 flex-1">
                      <p className="font-medium">{m.title}</p>
                      {!open && m.skills?.length > 0 && <p className="mt-0.5 truncate text-sm text-muted">{m.skills.join(', ')}</p>}
                    </div>
                    <ChevronDown size={18} className={clsx('shrink-0 text-muted transition', open && 'rotate-180')} />
                  </button>

                  {open && (
                    <div className="space-y-5 border-t border-line p-5">
                      {m.skills?.length > 0 && <div><p className="label">Skills</p><Tags items={m.skills} tone="accent" /></div>}
                      <div className="grid gap-5 md:grid-cols-2">
                        {m.projects?.length > 0 && (
                          <div><p className="label">Projects</p><ul className="space-y-1.5 text-sm text-muted">{m.projects.map((p, i) => <li key={i}>• {p}</li>)}</ul></div>
                        )}
                        {m.resources?.length > 0 && (
                          <div><p className="label">Resources</p><ul className="space-y-1.5 text-sm text-muted">{m.resources.map((r, i) => <li key={i}>• {r}</li>)}</ul></div>
                        )}
                      </div>
                      {m.milestones?.length > 0 && (
                        <div>
                          <p className="label">Milestones</p>
                          <ul className="space-y-1.5">
                            {m.milestones.map((ms, i) => {
                              const key = `${mi}-${i}`
                              return (
                                <li key={key}>
                                  <button onClick={() => setDone((d) => ({ ...d, [key]: !d[key] }))} className="flex w-full items-start gap-2.5 rounded-lg px-1 py-1 text-left text-sm hover:bg-subtle">
                                    <span className={clsx('mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border', done[key] ? 'border-accent bg-accent text-accent-ink' : 'border-line')}>
                                      {done[key] && <Check size={11} />}
                                    </span>
                                    <span className={done[key] ? 'text-muted line-through' : ''}>{ms}</span>
                                  </button>
                                </li>
                              )
                            })}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </li>
              )
            })}
          </ol>

          <div className="grid gap-5 md:grid-cols-2">
            {roadmap.certifications?.length > 0 && (
              <div className="card p-5">
                <SectionTitle icon={Award}>Certifications</SectionTitle>
                <ul className="space-y-3">
                  {roadmap.certifications.map((c, i) => (
                    <li key={i} className="text-sm">
                      <p className="font-medium">{c.name}</p>
                      <p className="text-xs text-muted">{c.provider}{c.estimated_time ? ` · ${c.estimated_time}` : ''}</p>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {roadmap.projects?.length > 0 && (
              <div className="card p-5">
                <SectionTitle icon={FolderKanban}>Portfolio projects</SectionTitle>
                <ul className="space-y-3">
                  {roadmap.projects.map((p, i) => (
                    <li key={i} className="text-sm">
                      <p className="font-medium">{p.name} {p.complexity && <span className="ml-1 text-xs font-normal text-muted">{p.complexity}</span>}</p>
                      <p className="text-muted">{p.description}</p>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

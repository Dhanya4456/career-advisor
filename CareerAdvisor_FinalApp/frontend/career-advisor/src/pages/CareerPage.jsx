import { useState } from 'react'
import {
  Compass,
  ArrowRight,
  ArrowLeft,
  Plus,
  Check,
  RefreshCw,
  TrendingUp,
} from 'lucide-react'
import clsx from 'clsx'
import { api } from '../utils/api'
import SkillQuiz from '../components/SkillQuiz'
import {
  PageHeader,
  SectionTitle,
  Spinner,
  ErrorBox,
} from '../components/ui'

const technicalSkills = [
  'Web Development',
  'Frontend Development',
  'Backend Development',
  'Full-Stack Development',
  'Mobile App Development',
  'Data Analytics',
  'Artificial Intelligence',
  'Machine Learning',
  'Generative AI',
  'Cybersecurity',
  'Cloud Computing',
  'Database Management',
  'Data Engineering',
  'Blockchain',
  'Internet of Things (IoT)',
  'UI/UX Design',
  'Computer Networking',
  'AR/VR Development',
  'Technical Support',
  'IT Infrastructure',
  'Research & Development',
]

const nonTechnicalSkills = [
  'Communication',
  'Leadership',
  'Team Management',
  'Project Management',
  'Marketing',
  'Digital Marketing',
  'Sales',
  'Business Development',
  'Customer Service',
  'Content Writing',
  'Social Media Management',
  'Event Management',
  'Teaching & Training',
  'Administration',
  'Hospitality Management',
  'Advertising',
  'Brand Management',
  'Market Research',
  'Strategy & Planning',
]

const interestsList = [
  'Technology',
  'Data & Analytics',
  'Healthcare',
  'Finance',
  'Education',
  'Creative Arts',
  'Business Strategy',
  'Research',
  'Product Development',
  'Social Impact',
]

const expLevels = [
  'Student',
  'Entry level (0–2 yrs)',
  'Mid level (3–5 yrs)',
  'Senior (6+ yrs)',
  'Executive',
]

const stepNames = [
  'Skills',
  'Interests & Experience',
  'Skill Quiz',
  'Results',
]

function findSalary(insights, role) {
  if (!insights) return null

  if (Array.isArray(insights)) {
    return (
      insights.find(
        (s) => s.role?.toLowerCase() === role.toLowerCase()
      ) || null
    )
  }

  return insights[role] ? { ...insights[role], role } : null
}

function ChipPicker({ options, selected, onToggle }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => (
        <button
          key={o}
          type="button"
          onClick={() => onToggle(o)}
          className={clsx(
            'chip',
            selected.includes(o) && 'chip-on'
          )}
        >
          {selected.includes(o) && <Check size={13} />}
          {o}
        </button>
      ))}
    </div>
  )
}

function AddOwn({ placeholder, onAdd }) {
  const [v, setV] = useState('')

  const add = () => {
    const t = v.trim()

    if (t) {
      onAdd(t)
      setV('')
    }
  }

  return (
    <div className="mt-4 flex max-w-sm gap-2">
      <input
        className="input"
        value={v}
        placeholder={placeholder}
        onChange={(e) => setV(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault()
            add()
          }
        }}
      />

      <button
        type="button"
        onClick={add}
        className="btn-secondary px-3"
        aria-label="Add"
      >
        <Plus size={16} />
      </button>
    </div>
  )
}

export default function CareerPage() {
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')
  const [quizResults, setQuizResults] = useState(null)

  const [form, setForm] = useState({
    skills: [],
    interests: [],
    experience: '',
    goal: '',
  })

  const toggle = (field) => (val) =>
    setForm((f) => ({
      ...f,
      [field]: f[field].includes(val)
        ? f[field].filter((v) => v !== val)
        : [...f[field], val],
    }))

  const addOwn = (field) => (val) =>
    setForm((f) =>
      f[field].some(
        (v) => v.toLowerCase() === val.toLowerCase()
      )
        ? f
        : {
            ...f,
            [field]: [...f[field], val],
          }
    )

  const analyze = async () => {
    setStep(4)
    setLoading(true)
    setResults(null)
    setError('')

    try {
      await api.put('/profile', {
        skills: form.skills,
        interests: form.interests,
        career_goals: form.goal || undefined,
      })

      const context = [
        form.experience &&
          `Experience level: ${form.experience}`,
        form.goal && `Career goal: ${form.goal}`,
      ]
        .filter(Boolean)
        .join('. ')

      setResults(
        await api.post('/career/recommend', {
          additional_context: context || undefined,
        })
      )
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setStep(1)
    setQuizResults(null)
    setResults(null)
    setError('')
  }

  const owned = form.skills.map((s) => s.toLowerCase())

  return (
    <div className="page">
      <PageHeader
        icon={Compass}
        title="Career path finder"
        subtitle="Tell us about yourself and get the roles that fit best."
      />

      <ol className="mb-8 flex items-center gap-3 text-sm">
        {stepNames.map((n, i) => {
          const active = step === i + 1
          const done = step > i + 1

          return (
            <li
              key={n}
              className="flex items-center gap-3"
            >
              <span
                className={clsx(
                  'flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium',
                  done || active
                    ? 'bg-accent text-accent-ink'
                    : 'bg-subtle text-muted'
                )}
              >
                {done ? <Check size={12} /> : i + 1}
              </span>

              <span
                className={
                  active ? 'font-medium' : 'text-muted'
                }
              >
                {n}
              </span>

              {i < stepNames.length - 1 && (
                <span className="h-px w-8 bg-line" />
              )}
            </li>
          )
        })}
      </ol>

      {/* STEP 1 */}
      {step === 1 && (
        <div className="card p-6 md:p-8">
          <h2 className="font-semibold">
            What are you good at?
          </h2>

          <p className="mb-5 mt-1 text-sm text-muted">
            Pick everything that applies, or add your own.
          </p>

          {/* Technical Skills */}
          <div className="mb-6 rounded-xl border border-line p-5">
            <h3 className="mb-4 font-semibold">
              Technical
            </h3>

            <ChipPicker
              options={[
                ...new Set([
                  ...technicalSkills,
                  ...form.skills.filter(
                    (skill) =>
                      !nonTechnicalSkills.some(
                        (item) =>
                          item.toLowerCase() ===
                          skill.toLowerCase()
                      )
                  ),
                ]),
              ]}
              selected={form.skills}
              onToggle={toggle('skills')}
            />
          </div>

          {/* Non-Technical Skills */}
          <div className="mb-6 rounded-xl border border-line p-5">
            <h3 className="mb-4 font-semibold">
              Non-Technical
            </h3>

            <ChipPicker
              options={[
                ...new Set([
                  ...nonTechnicalSkills,
                  ...form.skills.filter(
                    (skill) =>
                      !technicalSkills.some(
                        (item) =>
                          item.toLowerCase() ===
                          skill.toLowerCase()
                      )
                  ),
                ]),
              ]}
              selected={form.skills}
              onToggle={toggle('skills')}
            />
          </div>

          {/* Add Own Skill */}
          <AddOwn
            placeholder="Add another skill"
            onAdd={addOwn('skills')}
          />

          {/* Continue */}
          <div className="mt-8 flex justify-end">
            <button
              className="btn-primary"
              disabled={!form.skills.length}
              onClick={() => setStep(2)}
            >
              Continue
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2 */}
      {step === 2 && (
        <div className="card space-y-8 p-6 md:p-8">
          <div>
            <h2 className="font-semibold">
              What interests you?
            </h2>

            <div className="mt-4">
              <ChipPicker
                options={[
                  ...new Set([
                    ...interestsList,
                    ...form.interests,
                  ]),
                ]}
                selected={form.interests}
                onToggle={toggle('interests')}
              />
            </div>
          </div>

          <div>
            <h2 className="font-semibold">
              Experience level
            </h2>

            <div className="mt-4 flex flex-wrap gap-2">
              {expLevels.map((l) => (
                <button
                  key={l}
                  type="button"
                  onClick={() =>
                    setForm((f) => ({
                      ...f,
                      experience: l,
                    }))
                  }
                  className={clsx(
                    'chip',
                    form.experience === l && 'chip-on'
                  )}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-between">
            <button
              className="btn-ghost"
              onClick={() => setStep(1)}
            >
              <ArrowLeft size={16} />
              Back
            </button>

            <button
              className="btn-primary"
              onClick={() => setStep(3)}
            >
              Continue
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3 - SKILL QUIZ */}
      {step === 3 && (
        <SkillQuiz
          skills={form.skills}
          experience={form.experience}
          onBack={() => setStep(2)}
          onSkip={() => {
            setQuizResults(null)
            analyze()
          }}
          onDone={(r) => {
            setQuizResults(r)
            analyze()
          }}
        />
      )}

      {/* STEP 4 - RESULTS */}
      {step === 4 && (
        <>
          {loading && (
            <Spinner label="Analyzing your profile…" />
          )}

          {error && !loading && (
            <div className="space-y-3">
              <ErrorBox
                message={error}
                onRetry={analyze}
              />

              <button
                className="btn-ghost"
                onClick={() => setStep(2)}
              >
                <ArrowLeft size={16} />
                Edit answers
              </button>
            </div>
          )}

          {results && !loading && (
            <div className="space-y-10">
              {/* Best Matches */}
              <section>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="font-serif text-2xl">
                    Your best matches
                  </h2>

                  <button
                    className="btn-ghost"
                    onClick={reset}
                  >
                    <RefreshCw size={15} />
                    Start over
                  </button>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  {results.recommended_roles?.map(
                    (role, i) => {
                      const sal = findSalary(
                        results.salary_insights,
                        role
                      )

                      return (
                        <div
                          key={role}
                          className="card p-5"
                        >
                          <span className="text-xs font-medium text-accent">
                            #{i + 1}
                          </span>

                          <h3 className="mt-1 font-semibold">
                            {role}
                          </h3>

                          {sal && (
                            <p className="mt-3 text-sm text-muted">
                              {sal.min_salary} –{' '}
                              {sal.max_salary}

                              {sal.avg_salary && (
                                <span className="ml-1 text-xs">
                                  · avg {sal.avg_salary}
                                </span>
                              )}
                            </p>
                          )}
                        </div>
                      )
                    }
                  )}
                </div>
              </section>

              {/* Skill check */}
              {quizResults?.length > 0 && (
                <section>
                  <SectionTitle>Your skill check</SectionTitle>

                  <div className="flex flex-wrap gap-1.5">
                    {quizResults.map((r) => (
                      <span key={r.skill} className="tag">
                        {r.skill} · {r.percentage}%
                      </span>
                    ))}
                  </div>
                </section>
              )}

              {/* Required Skills */}
              {results.required_skills?.length > 0 && (
                <section>
                  <SectionTitle>
                    Skills these roles ask for
                  </SectionTitle>

                  <div className="flex flex-wrap gap-1.5">
                    {results.required_skills.map((s) => (
                      <span
                        key={s}
                        className={clsx(
                          'tag',
                          owned.includes(
                            s.toLowerCase()
                          ) &&
                            'bg-accent-soft text-accent'
                        )}
                      >
                        {owned.includes(
                          s.toLowerCase()
                        ) && <Check size={11} />}

                        {s}
                      </span>
                    ))}
                  </div>

                  <p className="mt-2 text-xs text-muted">
                    Highlighted skills are ones you
                    already have.
                  </p>
                </section>
              )}

              {/* Career Roadmap */}
              {results.career_roadmap && (
                <section>
                  <SectionTitle>
                    Your path
                  </SectionTitle>

                  <div className="grid gap-4 md:grid-cols-3">
                    {[
                      ['short_term', 'Short term'],
                      ['mid_term', 'Mid term'],
                      ['long_term', 'Long term'],
                    ].map(([key, label]) => {
                      const items =
                        results.career_roadmap[key]

                      if (!items?.length) return null

                      return (
                        <div
                          key={key}
                          className="card p-5"
                        >
                          <p className="mb-3 text-xs font-medium uppercase tracking-wide text-muted">
                            {label}
                          </p>

                          <ul className="space-y-2 text-sm">
                            {items.map((it, i) => (
                              <li
                                key={i}
                                className="flex gap-2"
                              >
                                <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-accent" />
                                {it}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )
                    })}
                  </div>
                </section>
              )}

              {/* Market Trends */}
              {results.market_trends?.length > 0 && (
                <section>
                  <SectionTitle icon={TrendingUp}>
                    Market trends
                  </SectionTitle>

                  <div className="card divide-y divide-line">
                    {results.market_trends.map(
                      (t, i) => (
                        <p
                          key={i}
                          className="px-5 py-3 text-sm text-muted"
                        >
                          {t}
                        </p>
                      )
                    )}
                  </div>
                </section>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
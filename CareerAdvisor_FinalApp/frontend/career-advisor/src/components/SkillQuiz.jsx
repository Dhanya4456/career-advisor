import { useCallback, useEffect, useState } from 'react'
import { ArrowLeft, ArrowRight, Loader2, Check } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../utils/api'
import { Spinner, ErrorBox } from './ui'

const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F']

const LEVEL_STYLE = {
  stronger: 'bg-accent-soft text-accent',
  developing: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
  needs_practice: 'bg-red-500/10 text-red-600 dark:text-red-400',
}
const BAR_STYLE = {
  stronger: 'bg-accent',
  developing: 'bg-amber-500',
  needs_practice: 'bg-red-500',
}

/**
 * Skill quiz shown between "Interests & Experience" and the results.
 * Questions come from the backend (/assessment/start) and are graded there
 * (/assessment/submit), so the answer key never reaches the browser.
 */
export default function SkillQuiz({ skills, experience, onDone, onSkip, onBack }) {
  const [phase, setPhase] = useState('loading') // loading | none | quiz | submitting | summary | error
  const [error, setError] = useState('')
  const [quizzes, setQuizzes] = useState([])
  const [unsupported, setUnsupported] = useState([])
  const [levelLabel, setLevelLabel] = useState('')
  const [page, setPage] = useState(0)
  const [answers, setAnswers] = useState({}) // question id -> chosen option text
  const [summary, setSummary] = useState(null)

  const load = useCallback(async () => {
    setPhase('loading')
    setError('')
    try {
      const data = await api.post('/assessment/start', { skills, experience })
      setUnsupported(data.unsupported || [])
      setLevelLabel(data.experience_level || '')
      setQuizzes(data.quizzes || [])
      setAnswers({})
      setPage(0)
      setPhase(data.quizzes?.length ? 'quiz' : 'none')
    } catch (e) {
      setError(e.message)
      setPhase('error')
    }
  }, [skills, experience])

  useEffect(() => { load() }, [load])

  const submit = async () => {
    setPhase('submitting')
    setError('')
    try {
      const payload = Object.entries(answers).map(([question_id, answer]) => ({ question_id, answer }))
      setSummary(await api.post('/assessment/submit', { answers: payload }))
      setPhase('summary')
    } catch (e) {
      setError(e.message)
      setPhase('quiz')
    }
  }

  if (phase === 'loading') return <Spinner label="Preparing your skill quiz…" />

  if (phase === 'error') {
    return (
      <div className="space-y-3">
        <ErrorBox message={error} onRetry={load} />
        <div className="flex justify-between">
          <button className="btn-ghost" onClick={onBack}><ArrowLeft size={16} /> Back</button>
          <button className="btn-secondary" onClick={onSkip}>Skip the quiz</button>
        </div>
      </div>
    )
  }

  if (phase === 'none') {
    return (
      <div className="card p-6 md:p-8">
        <h2 className="font-semibold">No quiz for your skills yet</h2>
        <p className="mt-2 text-sm text-muted">
          We don't have quiz questions for {unsupported.length ? unsupported.join(', ') : 'the skills you chose'}.
          You can continue straight to your career paths.
        </p>
        <div className="mt-8 flex justify-between">
          <button className="btn-ghost" onClick={onBack}><ArrowLeft size={16} /> Back</button>
          <button className="btn-primary" onClick={onSkip}>Find my paths <ArrowRight size={16} /></button>
        </div>
      </div>
    )
  }

  if (phase === 'summary' && summary) {
    return (
      <div className="card p-6 md:p-8">
        <h2 className="font-serif text-2xl">Your skill check</h2>
        <p className="mt-1 text-sm text-muted">
          Overall {summary.overall_percentage}% correct. This is a quick self-assessment, not a certification.
          Your results are used to tailor your career recommendations.
        </p>
        <ul className="mt-6 space-y-4">
          {summary.results.map((r) => (
            <li key={r.skill}>
              <div className="mb-1.5 flex items-center justify-between gap-3 text-sm">
                <span className="font-medium">{r.skill}</span>
                <span className="flex items-center gap-2">
                  <span className="text-xs text-muted">{r.correct}/{r.total} correct</span>
                  <span className={clsx('tag', LEVEL_STYLE[r.level])}>{r.label}</span>
                </span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-subtle">
                <div className={clsx('h-full rounded-full transition-all', BAR_STYLE[r.level])} style={{ width: `${r.percentage}%` }} />
              </div>
            </li>
          ))}
        </ul>
        {unsupported.length > 0 && (
          <p className="mt-5 text-xs text-muted">Not tested (no questions yet): {unsupported.join(', ')}.</p>
        )}
        <div className="mt-8 flex justify-end">
          <button className="btn-primary" onClick={() => onDone(summary.results)}>
            Find my career paths <ArrowRight size={16} />
          </button>
        </div>
      </div>
    )
  }

  // ---- quiz pages: one skill per page ----
  const quiz = quizzes[page]
  const answeredHere = quiz.questions.filter((q) => answers[q.id] !== undefined).length
  const pageDone = answeredHere === quiz.questions.length
  const isLast = page === quizzes.length - 1
  const submitting = phase === 'submitting'

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1">
          <div className="mb-1.5 flex justify-between text-xs text-muted">
            <span>Skill {page + 1} of {quizzes.length}</span>
            <span>{answeredHere}/{quiz.questions.length} answered</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-subtle">
            <div className="h-full rounded-full bg-accent transition-all" style={{ width: `${((page + answeredHere / quiz.questions.length) / quizzes.length) * 100}%` }} />
          </div>
        </div>
        <button className="btn-ghost shrink-0" onClick={onSkip} disabled={submitting}>Skip quiz</button>
      </div>

      <div className="card p-6 md:p-8">
        <h2 className="font-serif text-2xl">{quiz.skill}</h2>
        <p className="mt-1 text-sm text-muted">
          Pick the best answer for each question.
          {levelLabel && <> Questions are matched to your experience level: <span className="font-medium text-ink">{levelLabel}</span>.</>}
        </p>

        <div className="mt-6 space-y-8">
          {quiz.questions.map((q, qi) => (
            <fieldset key={q.id}>
              <legend className="mb-3 flex gap-2 text-sm font-medium">
                <span className="text-muted">{qi + 1}.</span>
                <span className="flex-1">{q.question}</span>
                <span className="tag shrink-0 self-start capitalize">{q.level}</span>
              </legend>
              <div className="space-y-2" role="radiogroup">
                {q.options.map((opt, oi) => {
                  const selected = answers[q.id] === opt
                  return (
                    <button
                      key={opt}
                      type="button"
                      role="radio"
                      aria-checked={selected}
                      onClick={() => setAnswers((a) => ({ ...a, [q.id]: opt }))}
                      className={clsx(
                        'flex w-full items-start gap-3 rounded-xl border px-4 py-3 text-left text-sm transition',
                        selected ? 'border-accent bg-accent-soft' : 'border-line hover:bg-subtle'
                      )}
                    >
                      <span className={clsx('flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[11px] font-medium',
                        selected ? 'border-accent bg-accent text-accent-ink' : 'border-line text-muted')}>
                        {selected ? <Check size={11} /> : LETTERS[oi]}
                      </span>
                      <span>{opt}</span>
                    </button>
                  )
                })}
              </div>
            </fieldset>
          ))}
        </div>

        {error && <p className="mt-6 rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-600 dark:text-red-400">{error}</p>}

        <div className="mt-8 flex justify-between">
          <button className="btn-ghost" disabled={submitting} onClick={() => (page === 0 ? onBack() : setPage((p) => p - 1))}>
            <ArrowLeft size={16} /> Back
          </button>
          {isLast ? (
            <button className="btn-primary" disabled={!pageDone || submitting} onClick={submit}>
              {submitting && <Loader2 size={16} className="animate-spin" />}
              {submitting ? 'Grading…' : 'Submit answers'}
            </button>
          ) : (
            <button className="btn-primary" disabled={!pageDone} onClick={() => setPage((p) => p + 1)}>
              Next skill <ArrowRight size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

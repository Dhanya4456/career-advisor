import { useRef, useState } from 'react'
import { FileText, UploadCloud, Loader2, RefreshCw, Check, X } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../utils/api'
import { PageHeader, SectionTitle, ErrorBox, Tags } from '../components/ui'

function ScoreRing({ score }) {
  const pct = Math.max(0, Math.min(100, Math.round(score || 0)))
  const r = 52
  const c = 2 * Math.PI * r
  const color = pct >= 75 ? 'text-accent' : pct >= 50 ? 'text-amber-500' : 'text-red-500'
  return (
    <div className="relative h-36 w-36 shrink-0">
      <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90">
        <circle cx="60" cy="60" r={r} fill="none" strokeWidth="9" className="stroke-subtle" />
        <circle cx="60" cy="60" r={r} fill="none" strokeWidth="9" strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c - (pct / 100) * c} className={clsx('stroke-current transition-all duration-700', color)} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-serif text-4xl leading-none">{pct}</span>
        <span className="mt-1 text-xs text-muted">ATS score</span>
      </div>
    </div>
  )
}

function ListCard({ title, items, icon: Icon, tone }) {
  if (!items?.length) return null
  return (
    <div className="card p-5">
      <SectionTitle>{title}</SectionTitle>
      <ul className="space-y-2 text-sm">
        {items.map((t, i) => (
          <li key={i} className="flex gap-2.5">
            <Icon size={15} className={clsx('mt-0.5 shrink-0', tone)} />
            <span className="text-muted">{t}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function ResumePage() {
  const [file, setFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [drag, setDrag] = useState(false)
  const inputRef = useRef(null)

  const pick = (f) => {
    if (!f) return
    if (f.type !== 'application/pdf' && !f.name.toLowerCase().endsWith('.pdf')) { setError('Please choose a PDF file.'); return }
    setError('')
    setFile(f)
  }

  const analyze = async () => {
    if (!file || !jobDescription.trim()) return
    setLoading(true)
    setResult(null)
    setError('')
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('job_description', jobDescription)
      setResult(await api.upload('/resume/analyze', formData))
    } catch (err) {
      setError(err.message || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

      const reset = () => { 
        setFile(null)
        setJobDescription('')
        setResult(null)
        setError('')
        if (inputRef.current) inputRef.current.value = ''
      }

  return (
    <div className="page">
      <PageHeader icon={FileText} title="Resume analyzer" subtitle="Upload your resume and paste a job description to get a JD-based ATS score, skill gaps and concrete fixes." />

      {!result && (
        <div className="card p-6 md:p-8">
          <div
            onDragOver={(e) => { e.preventDefault(); setDrag(true) }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => { e.preventDefault(); setDrag(false); pick(e.dataTransfer.files?.[0]) }}
            onClick={() => inputRef.current?.click()}
            className={clsx('flex cursor-pointer flex-col items-center rounded-xl border-2 border-dashed px-6 py-14 text-center transition', drag ? 'border-accent bg-accent-soft' : 'border-line hover:bg-subtle')}
          >
            <UploadCloud size={30} className="text-accent" />
            {file ? (
              <p className="mt-3 text-sm font-medium">{file.name} <span className="font-normal text-muted">· {(file.size / 1024).toFixed(0)} KB</span></p>
            ) : (
              <>
                <p className="mt-3 text-sm font-medium">Drop your resume here or click to browse</p>
                <p className="mt-1 text-xs text-muted">PDF only</p>
              </>
            )}
            <input ref={inputRef} type="file" accept="application/pdf,.pdf" className="hidden" onChange={(e) => pick(e.target.files?.[0])} />
          </div>

          {error && <p className="mt-4 rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-600 dark:text-red-400">{error}</p>}
                    <div className="mt-6">
            <label className="mb-2 block text-sm font-medium">
              Job Description
            </label>

            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
              rows={8}
              className="w-full rounded-xl border border-line bg-transparent px-4 py-3 text-sm outline-none focus:border-accent"
            />

            <p className="mt-1 text-xs text-muted">
              Paste the job description you want your resume compared against.
            </p>
          </div>

          <div className="mt-6 flex justify-end">
            <button className="btn-primary" disabled={!file || !jobDescription.trim() || loading} onClick={analyze}>
              {loading && <Loader2 size={16} className="animate-spin" />}
              {loading ? 'Analyzing…' : 'Analyze resume'}
            </button>
          </div>
        </div>
      )}

      {result && (
        <div className="space-y-5">
          <div className="card flex flex-col items-center gap-6 p-6 sm:flex-row md:p-8">
            <ScoreRing score={result.ats_score} />
            <div className="flex-1">
              <p className="text-xs text-muted">{result.filename}</p>
              <h2 className="mt-1 font-serif text-2xl">Overall feedback</h2>
              <p className="mt-2 text-sm leading-relaxed text-muted">{result.overall_feedback || 'No summary was returned.'}</p>
            </div>
            <button className="btn-secondary self-start" onClick={reset}><RefreshCw size={15} /> New resume</button>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <ListCard title="Strengths" items={result.strengths} icon={Check} tone="text-accent" />
            <ListCard title="Weaknesses" items={result.weaknesses} icon={X} tone="text-red-500" />
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <div className="card p-5"><SectionTitle>Skills found</SectionTitle><Tags items={result.extracted_skills} tone="accent" /></div>
            <div className="card p-5"><SectionTitle>Skills to add</SectionTitle><Tags items={result.missing_skills} tone="warn" /></div>
          </div>

          {result.improvement_suggestions?.length > 0 && (
            <div className="card p-5">
              <SectionTitle>How to improve</SectionTitle>
              <ol className="space-y-3 text-sm">
                {result.improvement_suggestions.map((t, i) => (
                  <li key={i} className="flex gap-3">
                    <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-accent-soft text-xs font-medium text-accent">{i + 1}</span>
                    <span className="text-muted">{t}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}
      {!result && error && !file && <div className="mt-4"><ErrorBox message={error} /></div>}
    </div>
  )
}

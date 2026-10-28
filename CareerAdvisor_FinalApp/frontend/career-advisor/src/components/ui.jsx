import { Loader2, AlertCircle, RefreshCw, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'

export function Brand({ to = '/', size = 'md' }) {
  const box = size === 'lg' ? 'h-9 w-9' : 'h-7 w-7'
  return (
    <Link to={to} className="inline-flex items-center gap-2.5">
      <span className={`${box} flex items-center justify-center rounded-lg bg-accent text-accent-ink`}>
        <Sparkles size={size === 'lg' ? 18 : 14} />
      </span>
      <span className="text-[17px] font-semibold tracking-tight">PathAI</span>
    </Link>
  )
}

export function PageHeader({ icon: Icon, title, subtitle, action }) {
  return (
    <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
      <div className="flex items-start gap-3.5">
        {Icon && (
          <div className="mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent-soft text-accent">
            <Icon size={20} />
          </div>
        )}
        <div>
          <h1 className="font-serif text-3xl leading-tight md:text-4xl">{title}</h1>
          {subtitle && <p className="mt-1 max-w-xl text-sm text-muted">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  )
}

export function SectionTitle({ icon: Icon, children }) {
  return (
    <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold">
      {Icon && <Icon size={16} className="text-accent" />}
      {children}
    </h2>
  )
}

export function Spinner({ label = 'Loading…' }) {
  return (
    <div className="flex items-center justify-center gap-2.5 py-16 text-sm text-muted">
      <Loader2 size={18} className="animate-spin text-accent" />
      {label}
    </div>
  )
}

export function ErrorBox({ message, onRetry }) {
  return (
    <div className="card flex flex-col items-center gap-3 px-6 py-10 text-center">
      <AlertCircle size={22} className="text-red-500" />
      <p className="max-w-md text-sm text-muted">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary">
          <RefreshCw size={15} /> Try again
        </button>
      )}
    </div>
  )
}

export function Tags({ items = [], tone = 'default' }) {
  if (!items.length) return <p className="text-sm text-muted">Nothing to show.</p>
  const cls = tone === 'accent' ? 'bg-accent-soft text-accent' : tone === 'warn' ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400' : ''
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((t, i) => (
        <span key={`${t}-${i}`} className={`tag ${cls}`}>{t}</span>
      ))}
    </div>
  )
}

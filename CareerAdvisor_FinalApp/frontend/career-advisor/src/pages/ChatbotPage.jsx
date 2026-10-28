import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { ArrowUp, RefreshCw, Sparkles, User } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../utils/api'
import { useAuth } from '../context/AuthContext'

const suggestions = [
  'Review my career plan',
  'What skills should I learn for data science?',
  'How do I prepare for a technical interview?',
  'Help me switch careers',
]

export default function ChatbotPage() {
  const { user } = useAuth()
  const first = user?.name?.split(' ')[0] || 'there'
  const greeting = { role: 'assistant', content: `Hi ${first}, I'm your career advisor. I can help with career transitions, job market trends, learning plans and interview prep. What's on your mind?` }

  const [messages, setMessages] = useState([greeting])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [sending, setSending] = useState(false)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, sending])

  const send = async (text) => {
    const content = (text ?? input).trim()
    if (!content || sending) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', content }])
    setSending(true)
    try {
      const data = await api.post('/chat/message', { message: content, session_id: sessionId })
      setSessionId(data.session_id)
      setMessages((m) => [...m, { role: 'assistant', content: data.reply }])
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', content: err.message, error: true }])
    } finally {
      setSending(false)
    }
  }

  const newChat = () => { setMessages([greeting]); setSessionId(null); setInput('') }
  const started = messages.length > 1

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-line px-5 py-4 md:px-8">
        <div>
          <h1 className="font-serif text-2xl">AI advisor</h1>
          <p className="text-xs text-muted">Ask about careers, skills, salary or interviews</p>
        </div>
        <button className="btn-ghost" onClick={newChat}><RefreshCw size={15} /> New chat</button>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-6 md:px-8">
        <div className="mx-auto max-w-3xl space-y-6">
          {messages.map((m, i) => (
            <div key={i} className={clsx('flex gap-3', m.role === 'user' && 'flex-row-reverse')}>
              <div className={clsx('flex h-8 w-8 shrink-0 items-center justify-center rounded-full', m.role === 'user' ? 'bg-subtle text-muted' : 'bg-accent text-accent-ink')}>
                {m.role === 'user' ? <User size={15} /> : <Sparkles size={15} />}
              </div>
              <div className={clsx('max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
                m.role === 'user' ? 'bg-accent text-accent-ink' : m.error ? 'bg-red-500/10 text-red-600 dark:text-red-400' : 'border border-line bg-surface')}>
                {m.role === 'assistant' && !m.error ? <div className="md"><ReactMarkdown>{m.content}</ReactMarkdown></div> : m.content}
              </div>
            </div>
          ))}

          {sending && (
            <div className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent text-accent-ink"><Sparkles size={15} /></div>
              <div className="flex items-center gap-1 rounded-2xl border border-line bg-surface px-4 py-3.5">
                {[0, 1, 2].map((d) => <span key={d} className="h-1.5 w-1.5 animate-pulse rounded-full bg-muted" style={{ animationDelay: `${d * 0.2}s` }} />)}
              </div>
            </div>
          )}

          {!started && (
            <div className="flex flex-wrap gap-2 pt-2">
              {suggestions.map((s) => <button key={s} className="chip" onClick={() => send(s)}>{s}</button>)}
            </div>
          )}
          <div ref={endRef} />
        </div>
      </div>

      <div className="border-t border-line px-5 py-4 md:px-8">
        <div className="mx-auto flex max-w-3xl items-end gap-2">
          <textarea
            rows={1}
            maxLength={4000}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
            placeholder="Ask about careers, skills, salary, interviews…"
            className="input max-h-40 min-h-[44px] resize-none"
          />
          <button onClick={() => send()} disabled={!input.trim() || sending} className="btn-primary h-11 w-11 shrink-0 p-0" aria-label="Send">
            <ArrowUp size={18} />
          </button>
        </div>
        <p className="mt-2 text-center text-xs text-muted">Enter to send · Shift+Enter for a new line</p>
      </div>
    </div>
  )
}

import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Compass, FileText, MessageSquare, Map, ArrowRight } from 'lucide-react'
import { Brand } from '../components/ui'
import { useAuth } from '../context/AuthContext'

const features = [
  { icon: Compass, title: 'Career path finder', text: 'Tell us your skills and interests. Get roles that fit, with salary ranges and the skills each one needs.' },
  { icon: FileText, title: 'Resume analyzer', text: 'Upload your PDF resume for an ATS score, missing skills and clear fixes.' },
  { icon: MessageSquare, title: 'AI career advisor', text: 'Ask anything about switching careers, interviews or salary, and get a straight answer.' },
  { icon: Map, title: 'Learning roadmap', text: 'A month-by-month plan with projects, resources and certifications for your target role.' },
]

const steps = [
  { n: '01', title: 'Build your profile', text: 'Add your education, skills and goals once.' },
  { n: '02', title: 'Get your direction', text: 'See matching roles and what is missing from your resume.' },
  { n: '03', title: 'Follow the plan', text: 'Work through a roadmap and ask the advisor when you are stuck.' },
]

const fade = (i = 0) => ({
  initial: { opacity: 0, y: 14 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true },
  transition: { duration: 0.45, delay: i * 0.06 },
})

export default function LandingPage() {
  const { isAuth } = useAuth()
  const cta = isAuth ? { to: '/dashboard', label: 'Open dashboard' } : { to: '/register', label: 'Get started free' }

  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Brand />
        <nav className="flex items-center gap-2">
          {!isAuth && <Link to="/login" className="btn-ghost">Sign in</Link>}
          <Link to={cta.to} className="btn-primary">{cta.label}</Link>
        </nav>
      </header>

      <section className="relative overflow-hidden">
        <div className="bg-grid absolute inset-0 h-[520px]" />
        <div className="relative mx-auto max-w-3xl px-6 pb-20 pt-16 text-center md:pt-24">
          <motion.p {...fade()} className="mb-5 inline-block rounded-full border border-line bg-surface px-3 py-1 text-xs font-medium text-muted">
            Career and education guidance, powered by AI
          </motion.p>
          <motion.h1 {...fade(1)} className="font-serif text-5xl leading-[1.05] md:text-7xl">
            Find the career that fits you, <em className="text-accent">and the plan to get there.</em>
          </motion.h1>
          <motion.p {...fade(2)} className="mx-auto mt-6 max-w-xl text-lg text-muted">
            PathAI turns your skills and goals into matched roles, a sharper resume and a learning plan you can actually follow.
          </motion.p>
          <motion.div {...fade(3)} className="mt-9 flex flex-wrap justify-center gap-3">
            <Link to={cta.to} className="btn-primary px-6 py-3">{cta.label} <ArrowRight size={16} /></Link>
            {!isAuth && <Link to="/login" className="btn-secondary px-6 py-3">I have an account</Link>}
          </motion.div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="font-serif text-3xl md:text-4xl">Everything for your next step</h2>
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          {features.map(({ icon: Icon, title, text }, i) => (
            <motion.div key={title} {...fade(i)} className="card p-6">
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-accent-soft text-accent"><Icon size={20} /></div>
              <h3 className="font-semibold">{title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-muted">{text}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="border-y border-line bg-subtle">
        <div className="mx-auto grid max-w-6xl gap-10 px-6 py-16 md:grid-cols-3">
          {steps.map((s, i) => (
            <motion.div key={s.n} {...fade(i)}>
              <p className="font-serif text-4xl text-accent">{s.n}</p>
              <h3 className="mt-2 font-semibold">{s.title}</h3>
              <p className="mt-1 text-sm text-muted">{s.text}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-3xl px-6 py-20 text-center">
        <h2 className="font-serif text-4xl md:text-5xl">Ready to plan your path?</h2>
        <Link to={cta.to} className="btn-primary mt-8 px-6 py-3">{cta.label} <ArrowRight size={16} /></Link>
      </section>

      <footer className="border-t border-line py-6 text-center text-xs text-muted">© {new Date().getFullYear()} PathAI</footer>
    </div>
  )
}

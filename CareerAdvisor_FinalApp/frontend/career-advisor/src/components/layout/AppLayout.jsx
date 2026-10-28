import { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, User, Compass, FileText, MessageSquare, Map, LogOut, Menu, X, Sun, Moon } from 'lucide-react'
import clsx from 'clsx'
import { useAuth } from '../../context/AuthContext'
import { useTheme } from '../../context/ThemeContext'
import { Brand } from '../ui'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/career', icon: Compass, label: 'Career paths' },
  { to: '/roadmap', icon: Map, label: 'Learning roadmap' },
  { to: '/resume', icon: FileText, label: 'Resume analyzer' },
  { to: '/chat', icon: MessageSquare, label: 'AI advisor' },
  { to: '/profile', icon: User, label: 'Profile' },
]

function Sidebar({ onNavigate }) {
  const { user, logout } = useAuth()
  const { theme, toggle } = useTheme()
  const navigate = useNavigate()
  const initial = (user?.name || 'U').charAt(0).toUpperCase()

  return (
    <div className="flex h-full flex-col bg-surface">
      <div className="px-5 py-5"><Brand to="/dashboard" /></div>

      <nav className="flex-1 space-y-0.5 px-3">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onNavigate}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition',
                isActive ? 'bg-subtle font-medium text-ink' : 'text-muted hover:bg-subtle hover:text-ink'
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={17} className={isActive ? 'text-accent' : ''} />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="space-y-1 border-t border-line p-3">
        <button onClick={toggle} className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted transition hover:bg-subtle hover:text-ink">
          {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
          {theme === 'dark' ? 'Light mode' : 'Dark mode'}
        </button>
        <div className="flex items-center gap-3 rounded-lg px-3 py-2">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent-soft text-sm font-semibold text-accent">{initial}</div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{user?.name}</p>
            <p className="truncate text-xs text-muted">{user?.email}</p>
          </div>
          <button
            onClick={() => { logout(); navigate('/') }}
            title="Sign out"
            className="rounded-md p-1.5 text-muted transition hover:bg-subtle hover:text-ink"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default function AppLayout() {
  const [open, setOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-bg">
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-line md:block">
        <Sidebar />
      </aside>

      {/* Mobile drawer */}
      {open && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black/40" onClick={() => setOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-72 border-r border-line shadow-xl">
            <button onClick={() => setOpen(false)} className="absolute right-3 top-4 rounded-md p-1.5 text-muted hover:bg-subtle" aria-label="Close menu">
              <X size={18} />
            </button>
            <Sidebar onNavigate={() => setOpen(false)} />
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-line bg-surface px-4 py-3 md:hidden">
          <button onClick={() => setOpen(true)} className="rounded-md p-1.5 text-muted hover:bg-subtle" aria-label="Open menu">
            <Menu size={20} />
          </button>
          <Brand to="/dashboard" />
        </header>
        <main className="min-h-0 flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

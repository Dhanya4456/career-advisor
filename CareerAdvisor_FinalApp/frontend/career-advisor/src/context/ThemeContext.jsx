import { createContext, useContext, useEffect, useState } from 'react'

const ThemeContext = createContext()
const KEY = 'pathai-theme'

export function ThemeProvider({ children }) {
  // Light is the default; the choice is remembered once the user toggles it.
  const [theme, setTheme] = useState(() => {
    try { return localStorage.getItem(KEY) || 'light' } catch { return 'light' }
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    try { localStorage.setItem(KEY, theme) } catch { /* ignore */ }
  }, [theme])

  const toggle = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))

  return <ThemeContext.Provider value={{ theme, toggle }}>{children}</ThemeContext.Provider>
}

export const useTheme = () => useContext(ThemeContext)

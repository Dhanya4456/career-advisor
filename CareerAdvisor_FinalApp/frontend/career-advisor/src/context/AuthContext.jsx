import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { api, getToken, setToken } from '../utils/api'

const AuthContext = createContext()

function readStoredUser() {
  try { return JSON.parse(localStorage.getItem('user')) } catch { return null }
}

export function AuthProvider({ children }) {
  // Only treat the user as signed in if we also hold a real backend token.
  const [user, setUser] = useState(() => (getToken() ? readStoredUser() : null))

  const persist = (data) => {
    setToken(data.access_token)
    const u = {
      id: data.user_id,
      name: data.full_name || data.email.split('@')[0],
      email: data.email,
      avatar: null,
    }
    setUser(u)
    localStorage.setItem('user', JSON.stringify(u))
  }

  // POST /api/v1/auth/login
  const login = async (email, password) => {
    persist(await api.post('/auth/login', { email, password }))
  }

  // POST /api/v1/auth/register (backend signs the user in and returns a token)
  const register = async (name, email, password) => {
    persist(await api.post('/auth/register', { email, password, full_name: name }))
  }

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('user')
  }, [])

  // api.js fires this when the backend answers 401 on a protected call
  useEffect(() => {
    window.addEventListener('auth:expired', logout)
    return () => window.removeEventListener('auth:expired', logout)
  }, [logout])

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAuth: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)

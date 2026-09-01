import { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('unilab-token')
    if (token) {
      setUsuario({ username: localStorage.getItem('unilab-user') || 'admin', token })
    }
    setLoading(false)
  }, [])

  const login = async (username, password) => {
    const data = await api.login(username, password)
    const user = { username: data.username, token: data.token }
    localStorage.setItem('unilab-token', data.token)
    localStorage.setItem('unilab-user', data.username)
    setUsuario(user)
    return user
  }

  const logout = async () => {
    try {
      await api.logout()
    } catch (error) {
      console.error('Error en logout:', error)
    }
    localStorage.removeItem('unilab-token')
    localStorage.removeItem('unilab-user')
    setUsuario(null)
  }

  return (
    <AuthContext.Provider value={{ usuario, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

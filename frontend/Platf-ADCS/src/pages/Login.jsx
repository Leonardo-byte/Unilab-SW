import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Lock, User, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'

function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('unilab')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const from = location.state?.from?.pathname || '/'

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await login(username, password)
      navigate(from, { replace: true })
    } catch (err) {
      setError('Credenciales inválidas. Intenta nuevamente.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0c10] flex items-center justify-center font-mono">
      <div className="w-full max-w-md">

        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white tracking-wider">
            UNILAB
          </h1>
          <p className="text-gray-500 text-sm mt-2 tracking-wider">
            Plataforma de Pruebas ADCS
          </p>
        </div>

        <div className="bg-[#14171e] border border-gray-800 rounded-lg p-8">

          <form onSubmit={handleSubmit} className="space-y-6">

            <div>
              <label className="text-gray-400 text-xs font-bold tracking-wider block mb-2">
                USUARIO
              </label>
              <div className="relative">
                <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-10 py-3 text-white font-mono text-sm focus:border-cyan-400 focus:outline-none transition-colors"
                  placeholder="admin"
                  required
                />
              </div>
            </div>

            <div>
              <label className="text-gray-400 text-xs font-bold tracking-wider block mb-2">
                CONTRASEÑA
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#0a0c10] border border-gray-700 rounded px-10 py-3 text-white font-mono text-sm focus:border-cyan-400 focus:outline-none transition-colors"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-400 transition-colors"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="text-red-400 text-xs text-center py-2">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full px-4 py-3 bg-cyan-500 hover:bg-cyan-600 text-black rounded font-bold text-xs tracking-wider transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'AUTENTICANDO...' : 'INICIAR SESIÓN'}
            </button>

          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-500 text-xs">
              Credenciales: admin / unilab
            </p>
          </div>

        </div>
      </div>
    </div>
  )
}

export default Login

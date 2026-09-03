import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { setToken } from '../services/auth'

function Login() {
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()

    setError('')
    setLoading(true)

    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'No se pudo iniciar sesión.',
        )
      }

      setToken(data.access_token)
      navigate('/')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Ocurrió un error al iniciar sesión.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">B</div>

        <span className="eyebrow">BRASALAND DIGITAL</span>
        <h1>Iniciar sesión</h1>
        <p>Ingresá con tu cuenta para acceder al backoffice.</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="nombre@ejemplo.com"
            />
          </div>

          <div>
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading ? 'Ingresando...' : 'Iniciar sesión'}
          </button>
        </form>

        <p className="auth-footer">
          ¿No tenés una cuenta? <Link to="/register">Registrate</Link>
        </p>
      </div>
    </div>
  )
}

export default Login
import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { setToken } from '../services/auth'

function Register() {
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [address, setAddress] = useState('')

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()

    setErrors({})
    setLoading(true)

    try {
      const registerResponse = await fetch('/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          name: name || null,
          phone: phone || null,
          address: address || null,
        }),
      })

      const registerData = await registerResponse.json()

      if (!registerResponse.ok) {
        if (Array.isArray(registerData.detail)) {
          const fieldErrors: Record<string, string> = {}

          registerData.detail.forEach(
            (item: { loc?: string[]; msg?: string }) => {
              const field = item.loc?.at(-1)

              if (field && item.msg) {
                fieldErrors[field] = item.msg
              }
            },
          )

          setErrors(fieldErrors)
          return
        }

        setErrors({
          general:
            typeof registerData.detail === 'string'
              ? registerData.detail
              : 'No se pudo crear la cuenta.',
        })
        return
      }

      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)

      const loginResponse = await fetch('/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      })

      const loginData = await loginResponse.json()

      if (!loginResponse.ok) {
        setErrors({
          general: 'La cuenta fue creada, pero no se pudo iniciar sesión.',
        })
        return
      }

      setToken(loginData.access_token)
      navigate('/')
    } catch {
      setErrors({
        general: 'Ocurrió un error inesperado.',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">B</div>

        <span className="eyebrow">BRASALAND DIGITAL</span>
        <h1>Crear cuenta</h1>
        <p>Registrate para acceder al backoffice.</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="name">Nombre</label>
            <input
              id="name"
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
            {errors.name && <span className="field-error">{errors.name}</span>}
          </div>

          <div>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>

          <div>
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
            {errors.password && (
              <span className="field-error">{errors.password}</span>
            )}
          </div>

          <div>
            <label htmlFor="phone">Teléfono</label>
            <input
              id="phone"
              value={phone}
              onChange={(event) => setPhone(event.target.value)}
            />
            {errors.phone && <span className="field-error">{errors.phone}</span>}
          </div>

          <div>
            <label htmlFor="address">Dirección</label>
            <input
              id="address"
              value={address}
              onChange={(event) => setAddress(event.target.value)}
            />
            {errors.address && (
              <span className="field-error">{errors.address}</span>
            )}
          </div>

          {errors.general && (
            <div className="error-message">{errors.general}</div>
          )}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading ? 'Creando cuenta...' : 'Registrarse'}
          </button>
        </form>

        <p className="auth-footer">
          ¿Ya tenés cuenta? <Link to="/login">Iniciá sesión</Link>
        </p>
      </div>
    </div>
  )
}

export default Register
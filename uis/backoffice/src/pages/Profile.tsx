import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { authFetch, removeToken } from '../services/auth'

type ProfileData = {
  name?: string | null
  phone?: string | null
  address?: string | null
}

type CurrentUser = {
  id: string
  email: string
  role: string
  profile?: ProfileData | null
}

function Profile() {
  const navigate = useNavigate()

  const [user, setUser] = useState<CurrentUser | null>(null)
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [address, setAddress] = useState('')

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const loadProfile = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await authFetch('/auth/me')

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'No se pudo cargar el perfil.')
      }

      const data: CurrentUser = await response.json()

      setUser(data)
      setName(data.profile?.name || '')
      setPhone(data.profile?.phone || '')
      setAddress(data.profile?.address || '')
    } catch (err) {
      setUser(null)
      setError(
        err instanceof Error
          ? err.message
          : 'Ocurrió un error al cargar el perfil.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProfile()
  }, [])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()

    setError('')
    setSuccess('')
    setSaving(true)

    try {
      const response = await authFetch('/profiles/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name || null,
          phone: phone || null,
          address: address || null,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'No se pudo actualizar el perfil.')
      }

      setSuccess('Perfil actualizado correctamente.')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Ocurrió un error al actualizar el perfil.',
      )
    } finally {
      setSaving(false)
    }
  }

  const handleLogout = () => {
    removeToken()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-card">Cargando perfil...</div>
      </div>
    )
  }

  if (!user && error) {
    return (
      <div className="profile-page">
        <div className="profile-card">
          <div className="error-message">{error}</div>

          <button
            type="button"
            className="auth-submit"
            onClick={loadProfile}
          >
            Reintentar
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="profile-page">
      <div className="profile-card">
        <div className="profile-header">
          <div>
            <span className="eyebrow">MI CUENTA</span>
            <h1>Perfil</h1>
            <p>Administrá tus datos personales.</p>
          </div>

          <button
            type="button"
            className="logout-button"
            onClick={handleLogout}
          >
            Cerrar sesión
          </button>
        </div>

        {user && (
          <div className="profile-account-info">
            <div>
              <span>Email</span>
              <strong>{user.email}</strong>
            </div>

            <div>
              <span>Rol</span>
              <strong>{user.role}</strong>
            </div>
          </div>
        )}

        <form className="profile-form" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="name">Nombre</label>
            <input
              id="name"
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
          </div>

          <div>
            <label htmlFor="phone">Teléfono</label>
            <input
              id="phone"
              value={phone}
              onChange={(event) => setPhone(event.target.value)}
            />
          </div>

          <div>
            <label htmlFor="address">Dirección</label>
            <input
              id="address"
              value={address}
              onChange={(event) => setAddress(event.target.value)}
            />
          </div>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <button
            type="submit"
            className="auth-submit"
            disabled={saving}
          >
            {saving ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Profile
const TOKEN_KEY = 'access_token'

export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY)
}

export const setToken = (token: string) => {
  localStorage.setItem(TOKEN_KEY, token)
}

export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY)
}

export const isAuthenticated = () => {
  return Boolean(getToken())
}

export const authFetch = async (
  input: RequestInfo | URL,
  init: RequestInit = {},
) => {
  const token = getToken()

  const headers = new Headers(init.headers)

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(input, {
    ...init,
    headers,
  })

  if (response.status === 401) {
    removeToken()

    if (window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
  }

  return response
}
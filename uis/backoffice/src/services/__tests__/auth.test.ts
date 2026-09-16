import { beforeEach, describe, expect, jest, test } from '@jest/globals'

import {
  authFetch,
  getToken,
  isAuthenticated,
  removeToken,
  setToken,
} from '../auth'

describe('auth utilities', () => {
  beforeEach(() => {
    localStorage.clear()
    jest.restoreAllMocks()
  })

  test('setToken guarda el token y getToken lo recupera', () => {
    setToken('token-prueba')

    expect(getToken()).toBe('token-prueba')
  })

  test('getToken devuelve null cuando no existe un token', () => {
    expect(getToken()).toBeNull()
  })

  test('removeToken elimina el token guardado', () => {
    setToken('token-prueba')

    removeToken()

    expect(getToken()).toBeNull()
  })

  test('isAuthenticated devuelve true cuando existe un token', () => {
    setToken('token-prueba')

    expect(isAuthenticated()).toBe(true)
  })

  test('isAuthenticated devuelve false cuando no existe un token', () => {
    expect(isAuthenticated()).toBe(false)
  })

  test('authFetch agrega Authorization cuando existe un token', async () => {
    setToken('token-prueba')

    const response = { status: 200 } as Response
    const fetchMock = jest.fn<typeof fetch>().mockResolvedValue(response)
    globalThis.fetch = fetchMock as typeof fetch

    await authFetch('/api/protected')

    expect(fetchMock).toHaveBeenCalledTimes(1)

    const [, init] = fetchMock.mock.calls[0]
    const headers = init?.headers as Headers

    expect(headers.get('Authorization')).toBe(
      'Bearer token-prueba',
    )
  })

  test('authFetch no agrega Authorization cuando no hay token', async () => {
    const response = { status: 200 } as Response
    const fetchMock = jest.fn<typeof fetch>().mockResolvedValue(response)
    globalThis.fetch = fetchMock as typeof fetch

    await authFetch('/api/public')

    const [, init] = fetchMock.mock.calls[0]
    const headers = init?.headers as Headers

    expect(headers.has('Authorization')).toBe(false)
  })

  test('authFetch elimina el token ante una respuesta 401', async () => {
    setToken('token-expirado')

    const response = { status: 401 } as Response

    const fetchMock = jest.fn<typeof fetch>().mockResolvedValue(response)
    globalThis.fetch = fetchMock as typeof fetch

    window.history.pushState({}, '', '/login')

    await authFetch('/api/protected')

    expect(getToken()).toBeNull()
  })
})

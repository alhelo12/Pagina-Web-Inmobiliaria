import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { decodeJwtPayload, useAuthStore } from '@/stores/authStore'

vi.mock('@/api/axios', () => ({
  default: {
    post: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
}))

vi.mock('@/api/auth', () => ({
  authApi: {
    me: vi.fn(),
  },
}))

describe('authStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  describe('decodeJwtPayload', () => {
    it('decodifica un JWT válido', () => {
      const payload = decodeJwtPayload(
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJuYW1lIjoiSm9obiBEb2UifQ.dummy'
      )
      expect(payload).toEqual({ sub: '123', name: 'John Doe' })
    })

    it('retorna null para token inválido', () => {
      expect(decodeJwtPayload('invalid')).toBeNull()
      expect(decodeJwtPayload('')).toBeNull()
    })
  })

  describe('logout', () => {
    it('limpia estado y localStorage', async () => {
      const store = useAuthStore()
      store.backendToken = 'token'
      store.role = 'client'
      store.userId = 1
      store.userEmail = 'test@test.com'
      store.isLogged = true
      store.isEmailVerified = true
      localStorage.setItem('backendToken', 'token')
      localStorage.setItem('role', 'client')

      await store.logout()

      expect(store.backendToken).toBeNull()
      expect(store.role).toBeNull()
      expect(store.userId).toBeNull()
      expect(store.userEmail).toBeNull()
      expect(store.isLogged).toBe(false)
      expect(store.isEmailVerified).toBe(false)
      expect(localStorage.getItem('backendToken')).toBeNull()
      expect(localStorage.getItem('role')).toBeNull()
    })
  })

  describe('loadSession', () => {
    it('no carga sesión si no hay datos en localStorage', async () => {
      const store = useAuthStore()
      await store.loadSession()
      expect(store.isLogged).toBe(false)
    })

    it('carga sesión válida desde localStorage', async () => {
      const store = useAuthStore()
      const validPayload = { sub: '1', email: 'test@test.com', role: 'client', exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = 'header.' + btoa(JSON.stringify(validPayload)) + '.signature'
      localStorage.setItem('backendToken', token)
      localStorage.setItem('backendUserId', '1')
      localStorage.setItem('role', 'client')

      await store.loadSession()

      expect(store.isLogged).toBe(true)
      expect(store.userId).toBe(1)
      expect(store.role).toBe('client')
    })

    it('limpia sesión si token expirado', async () => {
      const store = useAuthStore()
      const expiredPayload = { sub: '1', email: 'test@test.com', role: 'client', exp: Math.floor(Date.now() / 1000) - 3600 }
      const token = 'header.' + btoa(JSON.stringify(expiredPayload)) + '.signature'
      localStorage.setItem('backendToken', token)
      localStorage.setItem('backendUserId', '1')
      localStorage.setItem('role', 'client')

      await store.loadSession()

      expect(store.isLogged).toBe(false)
      expect(localStorage.getItem('backendToken')).toBeNull()
    })

    it('limpia sesión si token malformado', async () => {
      const store = useAuthStore()
      localStorage.setItem('backendToken', 'not.a.valid.token')
      localStorage.setItem('backendUserId', '1')
      localStorage.setItem('role', 'client')

      await store.loadSession()

      expect(store.isLogged).toBe(false)
      expect(localStorage.getItem('backendToken')).toBeNull()
    })

    it('maneja payload null sin crash', async () => {
      const store = useAuthStore()
      // token que decodifica a null (malformado)
      localStorage.setItem('backendToken', 'invalid.token.here')
      localStorage.setItem('backendUserId', '1')
      localStorage.setItem('role', 'client')

      await store.loadSession()

      expect(store.isLogged).toBe(false)
    })
  })

  describe('persistSession', () => {
    it('guarda todos los campos en localStorage', () => {
      const store = useAuthStore()
      store.backendToken = 'token123'
      store.role = 'client'
      store.userId = 42
      store.userEmail = 'test@test.com'
      store.isEmailVerified = true

      store.persistSession()

      expect(localStorage.getItem('backendToken')).toBe('token123')
      expect(localStorage.getItem('role')).toBe('client')
      expect(localStorage.getItem('backendUserId')).toBe('42')
      expect(localStorage.getItem('userEmail')).toBe('test@test.com')
      expect(localStorage.getItem('isEmailVerified')).toBe('true')
    })
  })
})

import { defineStore } from 'pinia'

// Decodifica el payload de un JWT sin librería externa
function decodeJwtPayload(token) {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(base64))
  } catch {
    return null
  }
}

// Verifica si el token ya expiró comparando con la hora actual
function isTokenExpired(token) {
  const payload = decodeJwtPayload(token)
  if (!payload || !payload.exp) return true
  // payload.exp está en segundos, Date.now() en milisegundos
  return payload.exp * 1000 < Date.now()
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    role: null,
    isLogged: false,
    token: null,       // ← JWT guardado en memoria
    userId: null,
    userEmail: null
  }),

  getters: {
    // Devuelve el header Authorization listo para usarse en axios/fetch
    authHeaders: (state) => {
      if (!state.token) return {}
      return { Authorization: `Bearer ${state.token}` }
    }
  },

  actions: {
    // Recibe la respuesta completa del backend { access_token, token_type }
    login(accessToken) {
      const payload = decodeJwtPayload(accessToken)
      if (!payload) {
        console.error('Token JWT inválido')
        return
      }

      this.token      = accessToken
      this.role       = payload.role   ?? null
      this.userId     = payload.sub    ?? null
      this.userEmail  = payload.email  ?? null
      this.isLogged   = true

      // Solo guardamos token y role en localStorage (no contraseñas)
      localStorage.setItem('token', accessToken)
      localStorage.setItem('role', this.role)
    },

    logout() {
      this.token      = null
      this.role       = null
      this.userId     = null
      this.userEmail  = null
      this.isLogged   = false

      localStorage.removeItem('token')
      localStorage.removeItem('role')
    },

    // Se llama al iniciar la app para restaurar la sesión guardada
    loadSession() {
      const token = localStorage.getItem('token')
      if (!token) return

      // Si el token ya expiró, limpiamos y no restauramos
      if (isTokenExpired(token)) {
        this.logout()
        return
      }

      const payload = decodeJwtPayload(token)
      this.token     = token
      this.role      = payload?.role  ?? null
      this.userId    = payload?.sub   ?? null
      this.userEmail = payload?.email ?? null
      this.isLogged  = true
    }
  }
})

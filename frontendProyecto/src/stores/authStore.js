import { defineStore } from 'pinia'
import apiClient from '@/api/axios'
import { authApi } from '@/api/auth'

export function decodeJwtPayload(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch { return null }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    role: null,
    isLogged: false,
    backendToken: null,
    userId: null,
    userEmail: null,
    isEmailVerified: false
  }),

  getters: {
    authHeaders: (state) => {
      if (!state.backendToken) return {}
      return { Authorization: `Bearer ${state.backendToken}` }
    }
  },

  actions: {
    async login(email, password) {
      const params = new URLSearchParams()
      params.append('username', email)
      params.append('password', password)
      const { data } = await apiClient.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })

      const payload = decodeJwtPayload(data.access_token)
      if (!payload) throw new Error('Token inválido')

      this.backendToken = data.access_token
      this.role = payload.role || 'client'
      this.userId = Number(payload.sub)
      this.userEmail = payload.email || email
      this.isLogged = true

      // Cargar perfil para obtener is_email_verified
      try {
        const me = await authApi.me()
        this.isEmailVerified = me.data.is_email_verified ?? false
      } catch {
        this.isEmailVerified = false
      }

      this.persistSession()
    },

    async sendVerificationEmail() {
      if (!this.userEmail) throw new Error('Sin email')
      const { data } = await authApi.sendVerification(this.userEmail)
      return data
    },

    async forgotPassword(email) {
      const { data } = await authApi.forgotPassword(email)
      return data
    },

    async resetPassword(token, newPassword) {
      const { data } = await authApi.resetPassword(token, newPassword)
      return data
    },

    persistSession() {
      if (this.backendToken) localStorage.setItem('backendToken', this.backendToken)
      if (this.role) localStorage.setItem('role', this.role)
      if (this.userId) localStorage.setItem('backendUserId', this.userId)
      localStorage.setItem('isEmailVerified', String(this.isEmailVerified))
      if (this.userEmail) localStorage.setItem('userEmail', this.userEmail)
    },

    async logout() {
      this.backendToken = null
      this.role = null
      this.userId = null
      this.userEmail = null
      this.isLogged = false
      this.isEmailVerified = false
      localStorage.removeItem('role')
      localStorage.removeItem('backendToken')
      localStorage.removeItem('backendUserId')
      localStorage.removeItem('isEmailVerified')
      localStorage.removeItem('userEmail')
    },

    async loadSession() {
      const savedEmailVerified = localStorage.getItem('isEmailVerified')
      if (savedEmailVerified) {
        this.isEmailVerified = savedEmailVerified === 'true'
      }

      const savedBackendToken = localStorage.getItem('backendToken')
      const savedUserId = localStorage.getItem('backendUserId')
      const savedRole = localStorage.getItem('role')

      if (savedBackendToken && savedUserId && savedRole) {
        const payload = decodeJwtPayload(savedBackendToken)
        if (!payload) {
          await this.logout()
          return
        }
        if (payload.exp && payload.exp * 1000 < Date.now()) {
          await this.logout()
          return
        }

        this.backendToken = savedBackendToken
        this.role = savedRole
        this.userId = Number(savedUserId)
        this.userEmail = payload.email || localStorage.getItem('userEmail') || null
        this.isLogged = true
      }
    }
  }
})

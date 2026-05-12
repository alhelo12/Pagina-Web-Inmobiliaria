import { defineStore } from 'pinia'
import { supabase } from '@/lib/supabase'
import apiClient from '@/api/axios'

function decodeJwtPayload(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch { return null }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    role: null,
    isLogged: false,
    token: null,
    backendToken: null,
    userId: null,
    userEmail: null,
    authMethod: null,
    isEmailVerified: false,
    isSupabaseUser: false
  }),

  getters: {
    authHeaders: (state) => {
      const token = state.backendToken || state.token
      if (!token) return {}
      return { Authorization: `Bearer ${token}` }
    }
  },

  actions: {
    async register(email, password, fullName = null, phone = null) {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: window.location.origin + '/verificado'
        }
      })
      if (error) throw error

      this.isSupabaseUser = true

      try {
        await apiClient.post('/auth/register/client', {
          full_name: fullName || email.split('@')[0],
          email,
          password,
          phone: phone || null
        })
      } catch {
        console.warn('Backend registration failed, user only exists in Supabase')
      }

      return data
    },

    async login(email, password) {
      const backendError = await this.tryBackendLogin(email, password)
      if (backendError) throw backendError

      await this.checkEmailVerification(email, password)
    },

    async checkEmailVerification(email, password) {
      this.isEmailVerified = false
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })
      if (!error && data?.user) {
        this.isSupabaseUser = true
        this.isEmailVerified = data.user.email_confirmed_at ? true : false
        await supabase.auth.signOut()
      } else if (this.role === 'client' && !this.isSupabaseUser) {
        const { error: signUpError } = await supabase.auth.signUp({
          email,
          password,
          options: { emailRedirectTo: window.location.origin + '/verificado' }
        })
        if (!signUpError) {
          this.isSupabaseUser = true
          this.isEmailVerified = false
        }
      }
      this.persistSession()
    },

    async tryBackendLogin(email, password) {
      try {
        const params = new URLSearchParams()
        params.append('username', email)
        params.append('password', password)
        const { data } = await apiClient.post('/auth/login', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        })

        const payload = decodeJwtPayload(data.access_token)
        if (!payload) throw new Error('Token inválido')

        this.authMethod = 'backend'
        this.token = data.access_token
        this.backendToken = data.access_token
        this.role = payload.role || 'client'
        this.userId = payload.sub
        this.userEmail = payload.email || email
        this.isLogged = true

        this.persistSession()
        return null
      } catch (err) {
        if (err.response?.status === 401) {
          return new Error('Email o contraseña incorrectos')
        }
        return err
      }
    },

    async exchangeToken() {
      try {
        const { data } = await apiClient.post('/auth/exchange', {
          supabase_token: this.token
        })
        this.backendToken = data.access_token
        this.role = data.role
        this.userId = String(data.user_id)
        this.userEmail = data.email
        this.persistSession()
      } catch {
        console.warn('Token exchange failed, using Supabase token directly')
      }
    },

    async resendVerificationEmail(email) {
      const { error } = await supabase.auth.resend({
        type: 'signup',
        email
      })
      if (error) throw error
    },

    persistSession() {
      if (this.backendToken) localStorage.setItem('backendToken', this.backendToken)
      if (this.role) localStorage.setItem('role', this.role)
      if (this.userId) localStorage.setItem('backendUserId', this.userId)
      if (this.authMethod) localStorage.setItem('authMethod', this.authMethod)
      localStorage.setItem('isEmailVerified', String(this.isEmailVerified))
      localStorage.setItem('isSupabaseUser', String(this.isSupabaseUser))
    },

    async logout() {
      const method = this.authMethod
      this.backendToken = null
      this.token = null
      this.role = null
      this.userId = null
      this.userEmail = null
      this.isLogged = false
      this.authMethod = null
      this.isEmailVerified = false
      this.isSupabaseUser = false
      localStorage.removeItem('role')
      localStorage.removeItem('backendToken')
      localStorage.removeItem('backendUserId')
      localStorage.removeItem('authMethod')
      localStorage.removeItem('isEmailVerified')
      localStorage.removeItem('isSupabaseUser')
      if (method === 'supabase') {
        await supabase.auth.signOut()
      }
    },

    async loadSession() {
      const savedEmailVerified = localStorage.getItem('isEmailVerified')
      if (savedEmailVerified) {
        this.isEmailVerified = savedEmailVerified === 'true'
      }
      const savedSupabaseUser = localStorage.getItem('isSupabaseUser')
      if (savedSupabaseUser) {
        this.isSupabaseUser = savedSupabaseUser === 'true'
      }

      const { data } = await supabase.auth.getSession()
      const session = data?.session

      if (session) {
        const user = session.user
        this.authMethod = 'supabase'
        this.token = session.access_token
        this.role = user.user_metadata?.role ?? user.app_metadata?.role ?? 'client'
        this.userId = user.id
        this.userEmail = user.email
        this.isLogged = true

        const savedBackendToken = localStorage.getItem('backendToken')
        const savedUserId = localStorage.getItem('backendUserId')
        if (savedBackendToken && savedUserId) {
          this.backendToken = savedBackendToken
          this.role = localStorage.getItem('role') || this.role
          this.userId = savedUserId
        } else {
          await this.exchangeToken()
        }
        return
      }

      const savedBackendToken = localStorage.getItem('backendToken')
      const savedUserId = localStorage.getItem('backendUserId')
      const savedRole = localStorage.getItem('role')
      const savedAuthMethod = localStorage.getItem('authMethod')

      if (savedBackendToken && savedUserId && savedRole) {
        this.authMethod = savedAuthMethod || 'backend'
        this.token = savedBackendToken
        this.backendToken = savedBackendToken
        this.role = savedRole
        this.userId = savedUserId
        this.isLogged = true
      }
    },

    async forgotPassword(email) {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: window.location.origin + '/nueva-contrasena'
      })
      if (error) throw error
    },

    async updatePassword(newPassword) {
      const { error } = await supabase.auth.updateUser({
        password: newPassword
      })
      if (error) throw error
    }
  }
})

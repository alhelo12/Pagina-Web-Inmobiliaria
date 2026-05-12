import { defineStore } from 'pinia'
import { supabase } from '@/lib/supabase'
import apiClient from '@/api/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    role: null,
    isLogged: false,
    token: null,
    backendToken: null,
    userId: null,
    userEmail: null
  }),

  getters: {
    authHeaders: (state) => {
      const token = state.backendToken || state.token
      if (!token) return {}
      return { Authorization: `Bearer ${token}` }
    }
  },

  actions: {
    async register(email, password) {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: window.location.origin + '/verificado'
        }
      })
      if (error) throw error
      return data
    },

    async login(email, password) {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) {
        if (error.message?.toLowerCase().includes('email not confirmed')) {
          throw new Error('Debes verificar tu correo antes de iniciar sesión. Revisa tu bandeja de entrada.')
        }
        throw error
      }

      const user = data.user
      const session = data.session

      this.role = user.user_metadata?.role ?? user.app_metadata?.role ?? 'client'
      this.token = session.access_token
      this.userId = user.id
      this.userEmail = user.email
      this.isLogged = true

      localStorage.setItem('role', this.role)

      await this.exchangeToken()
      return data
    },

    async exchangeToken() {
      try {
        const { data } = await apiClient.post('/auth/exchange', {
          supabase_token: this.token
        })
        this.backendToken = data.access_token
      } catch {
        console.warn('Token exchange failed, using Supabase token directly')
      }
    },

    async logout() {
      this.backendToken = null
      this.token = null
      this.role = null
      this.userId = null
      this.userEmail = null
      this.isLogged = false
      localStorage.removeItem('role')
      await supabase.auth.signOut()
    },

    async loadSession() {
      const { data } = await supabase.auth.getSession()
      const session = data?.session
      if (!session) return

      const user = session.user
      this.token = session.access_token
      this.role = user.user_metadata?.role ?? user.app_metadata?.role ?? 'client'
      this.userId = user.id
      this.userEmail = user.email
      this.isLogged = true

      if (!this.backendToken) {
        await this.exchangeToken()
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


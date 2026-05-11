import { defineStore } from 'pinia'
import { supabase } from '@/lib/supabase'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    role: null,
    isLogged: false,
    token: null,
    userId: null,
    userEmail: null
  }),

  getters: {
    authHeaders: (state) => {
      if (!state.token) return {}
      return { Authorization: `Bearer ${state.token}` }
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
      return data
    },

    async logout() {
      await supabase.auth.signOut()
      this.token = null
      this.role = null
      this.userId = null
      this.userEmail = null
      this.isLogged = false
      localStorage.removeItem('role')
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


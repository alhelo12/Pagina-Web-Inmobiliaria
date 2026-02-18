import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    role: null,
    isLogged: false
  }),

  actions: {
    login(role) {
      this.role = role
      this.isLogged = true

      localStorage.setItem('role', role)
      localStorage.setItem('isLogged', 'true')
    },

    logout() {
      this.role = null
      this.isLogged = false

      localStorage.removeItem('role')
      localStorage.removeItem('isLogged')
    },

    loadSession() {
      const role = localStorage.getItem('role')
      const isLogged = localStorage.getItem('isLogged') === 'true'

      if (role && isLogged) {
        this.role = role
        this.isLogged = true
      }
    }
  }
})

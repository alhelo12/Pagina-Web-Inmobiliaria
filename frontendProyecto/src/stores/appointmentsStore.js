import { defineStore } from 'pinia'
import { appointmentsApi } from '@/api/appointments'
import { useAuthStore } from '@/stores/authStore'

export const useAppointmentsStore = defineStore('appointments', {
  state: () => ({
    appointments: [],
    total: 0,
    loading: false,
    error: null
  }),

  getters: {
    pendingAppointments: (state) =>
      state.appointments.filter(a => a.status === 'pending').length,

    confirmedAppointments: (state) =>
      state.appointments.filter(a => a.status === 'confirmed').length,

    activeAppointments: (state) =>
      state.appointments.filter(a => ['pending', 'confirmed'].includes(a.status)).length,

    upcomingAppointments: (state) => {
      const now = new Date()
      return state.appointments.filter(a => {
        const date = new Date(a.scheduled_date)
        return date >= now && ['pending', 'confirmed'].includes(a.status)
      }).length
    }
  },

  actions: {
    async fetchAppointments(params = {}) {
      this.loading = true
      this.error = null
      try {
        const { data } = await appointmentsApi.getByClient(params)
        this.appointments = data.appointments ?? data.items ?? data
        this.total = data.total ?? this.appointments.length
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar citas'
      } finally {
        this.loading = false
      }
    },

    async fetchUpcoming(daysAhead = 7) {
      this.loading = true
      this.error = null
      try {
        const auth = useAuthStore()
        const { data } = await appointmentsApi.getByClient({
          skip: 0,
          limit: 50,
          status_filter: undefined
        })
        const all = data.appointments ?? data.items ?? data
        const now = new Date()
        const cutoff = new Date(now.getTime() + daysAhead * 86400000)
        this.appointments = all.filter(a => {
          const date = new Date(a.scheduled_date)
          return date >= now && date <= cutoff &&
            ['pending', 'confirmed'].includes(a.status)
        })
        this.total = this.appointments.length
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar citas'
      } finally {
        this.loading = false
      }
    },

    clear() {
      this.appointments = []
      this.total = 0
      this.error = null
    }
  }
})
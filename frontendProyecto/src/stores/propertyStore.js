import { defineStore } from 'pinia'
import { propertiesApi } from '@/api/properties'

export const usePropertyStore = defineStore('property', {
  state: () => ({
    properties: [],
    total:      0,
    loading:    false,
    error:      null,
    advisorStats: null,
    availableProperties: []
  }),

  getters: {
    approved: (state) => state.properties.filter(p => p.status === 'approved'),
    pending:  (state) => state.properties.filter(p => p.status === 'pending')
  },

  actions: {
    async fetchProperties(params = {}) {
      this.loading = true
      this.error   = null
      try {
        const { data } = await propertiesApi.getAll(params)
        this.properties = data.properties ?? data.items ?? data
        this.total      = data.total ?? this.properties.length
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar propiedades'
      } finally {
        this.loading = false
      }
    },

    async fetchPending() {
      this.loading = true
      this.error   = null
      try {
        const { data } = await propertiesApi.getPending()
        this.properties = data.properties ?? data.items ?? data
        this.total      = data.total ?? this.properties.length
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar pendientes'
      } finally {
        this.loading = false
      }
    },

    async fetchByAdvisor() {
      this.loading = true
      this.error   = null
      try {
        const { data } = await propertiesApi.getByAdvisor()
        this.properties = data.properties ?? data.items ?? data
        this.total      = data.total ?? this.properties.length
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar propiedades'
      } finally {
        this.loading = false
      }
    },

    async fetchAvailable() {
      this.loading = true
      this.error   = null
      try {
        const { data } = await propertiesApi.getAvailable()
        this.availableProperties = data.properties ?? data.items ?? data
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar disponibles'
      } finally {
        this.loading = false
      }
    },

    async fetchAdvisorStats() {
      try {
        const { data } = await propertiesApi.getSummaryByAdvisor()
        this.advisorStats = data
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar estadísticas'
      }
    },

    async takeProperty(id) {
      const { data } = await propertiesApi.takeProperty(id)
      this._updateLocal(data)
      this.availableProperties = this.availableProperties.filter(p => p.id !== id)
    },

    async returnProperty(id) {
      const { data } = await propertiesApi.returnProperty(id)
      this._updateLocal(data)
    },

    async approve(id) {
      const { data } = await propertiesApi.approve(id)
      this._updateLocal(data)
    },

    async reject(id) {
      const { data } = await propertiesApi.reject(id)
      this._updateLocal(data)
    },

    async markSold(id) {
      const { data } = await propertiesApi.markSold(id)
      this._updateLocal(data)
    },

    async remove(id) {
      await propertiesApi.remove(id)
      this.properties = this.properties.filter(p => p.id !== id)
      this.total = Math.max(0, this.total - 1)
    },

    _updateLocal(updated) {
      const idx = this.properties.findIndex(p => p.id === updated.id)
      if (idx !== -1) this.properties[idx] = updated
    }
  }
})

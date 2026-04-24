/**
 * Store: Propiedades
 * Maneja la lista pública, filtros y acciones de asesor/admin.
 */
import { defineStore } from 'pinia'
import { propertiesApi } from '@/api/properties'

export const usePropertyStore = defineStore('property', {
  state: () => ({
    properties:  [],   // lista actual (filtrada o completa)
    total:       0,
    loading:     false,
    error:       null
  }),

  getters: {
    approved: (state) => state.properties.filter(p => p.status === 'approved'),
    pending:  (state) => state.properties.filter(p => p.status === 'pending')
  },

  actions: {
    /** Carga propiedades con filtros opcionales */
    async fetchProperties(params = {}) {
      this.loading = true
      this.error   = null
      try {
        const { data } = await propertiesApi.getAll(params)
        // El backend devuelve { items, total } o un array directo
        this.properties = data.items ?? data
        this.total      = data.total ?? this.properties.length
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar propiedades'
      } finally {
        this.loading = false
      }
    },

    /** Carga propiedades pendientes (asesor/admin) */
    async fetchPending() {
      this.loading = true
      this.error   = null
      try {
        const { data } = await propertiesApi.getPending()
        this.properties = data.items ?? data
        this.total      = data.total ?? this.properties.length
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar pendientes'
      } finally {
        this.loading = false
      }
    },

    /** Aprobar una propiedad y actualizar el estado local */
    async approve(id) {
      const { data } = await propertiesApi.approve(id)
      this._updateLocal(data)
    },

    /** Rechazar una propiedad */
    async reject(id) {
      const { data } = await propertiesApi.reject(id)
      this._updateLocal(data)
    },

    /** Marcar como vendida */
    async markSold(id) {
      const { data } = await propertiesApi.markSold(id)
      this._updateLocal(data)
    },

    /** Eliminar una propiedad */
    async remove(id) {
      await propertiesApi.remove(id)
      this.properties = this.properties.filter(p => p.id !== id)
      this.total = Math.max(0, this.total - 1)
    },

    /** Actualiza el objeto en la lista local sin recargar todo */
    _updateLocal(updated) {
      const idx = this.properties.findIndex(p => p.id === updated.id)
      if (idx !== -1) this.properties[idx] = updated
    }
  }
})

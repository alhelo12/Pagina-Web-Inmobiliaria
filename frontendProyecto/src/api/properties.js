/**
 * API: Propiedades
 */
import api from './axios'

export const propertiesApi = {
  /** Lista paginada con filtros opcionales */
  getAll(params = {}) {
    return api.get('/properties', { params })
  },

  /** Detalle de una propiedad */
  getById(id) {
    return api.get(`/properties/${id}`)
  },

  /** Búsqueda avanzada */
  search(filters) {
    return api.post('/properties/search', filters)
  },

  /** Crear propiedad (cliente autenticado) */
  create(data) {
    return api.post('/properties', data)
  },

  /** Actualizar propiedad */
  update(id, data) {
    return api.put(`/properties/${id}`, data)
  },

  /** Eliminar propiedad */
  remove(id) {
    return api.delete(`/properties/${id}`)
  },

  /** Aprobar propiedad (asesor/admin) */
  approve(id) {
    return api.patch(`/properties/${id}/approve`)
  },

  /** Rechazar propiedad (asesor/admin) */
  reject(id) {
    return api.patch(`/properties/${id}/reject`)
  },

  /** Marcar como vendida (asesor/admin) */
  markSold(id) {
    return api.patch(`/properties/${id}/mark-sold`)
  },

  /** Propiedades pendientes (para el asesor) */
  getPending() {
    return api.get('/properties/pending/list')
  },

  /** Resumen de estadísticas */
  getSummary() {
    return api.get('/properties/stats/summary')
  }
}

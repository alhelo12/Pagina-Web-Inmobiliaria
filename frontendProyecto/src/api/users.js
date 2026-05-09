/**
 * API: Usuarios (administración)
 */
import api from './axios'

export const usersApi = {
  /** Lista de usuarios (admin) */
  getAll(params = {}) {
    return api.get('/users', { params })
  },

  /** Detalle de usuario */
  getById(id) {
    return api.get(`/users/${id}`)
  },

  /** Actualizar usuario */
  update(id, data) {
    return api.put(`/users/${id}`, data)
  },

  /** Eliminar usuario */
  remove(id) {
    return api.delete(`/users/${id}`)
  },

  /** Activar usuario */
  activate(id) {
    return api.patch(`/users/${id}/activate`)
  },

  /** Desactivar usuario */
  deactivate(id) {
    return api.patch(`/users/${id}/deactivate`)
  },

  /** Stats resumidos para dashboard */
  getStats() {
    return api.get('/users/stats/summary')
  },

  /** Actividad reciente para dashboard */
  getRecentActivity(params = {}) {
    return api.get('/users/recent-activity', { params })
  }
}

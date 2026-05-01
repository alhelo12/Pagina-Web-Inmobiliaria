/**
 * API: Favoritos
 */
import api from './axios'

export const favoritesApi = {
  /** Lista de favoritos del usuario actual */
  getAll(userId) {
    return api.get('/favorites', { params: { user_id: userId } })
  },

  /** Agregar o quitar favorito (toggle) */
  toggle(propertyId, userId) {
    return api.post(`/favorites/toggle/${propertyId}`, null, { params: { user_id: userId } })
  },

  /** Verificar si una propiedad es favorita */
  check(propertyId, userId) {
    return api.get(`/favorites/check/${propertyId}`, { params: { user_id: userId } })
  },

  /** Verificar múltiples propiedades de una vez */
  checkMultiple(propertyIds, userId) {
    return api.post('/favorites/check-multiple', propertyIds, { params: { user_id: userId } })
  },

  /** Eliminar favorito por ID de favorito */
  remove(favoriteId) {
    return api.delete(`/favorites/${favoriteId}`)
  },

  /** Conteo publico de favoritos por propiedad */
  getPropertyCount(propertyId) {
    return api.get(`/favorites/property/${propertyId}/count`)
  }
}

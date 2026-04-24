/**
 * API: Favoritos
 */
import api from './axios'

export const favoritesApi = {
  /** Lista de favoritos del usuario actual */
  getAll() {
    return api.get('/favorites')
  },

  /** Agregar o quitar favorito (toggle) */
  toggle(propertyId) {
    return api.post(`/favorites/toggle/${propertyId}`)
  },

  /** Verificar si una propiedad es favorita */
  check(propertyId) {
    return api.get(`/favorites/check/${propertyId}`)
  },

  /** Verificar múltiples propiedades de una vez */
  checkMultiple(propertyIds) {
    return api.post('/favorites/check-multiple', { property_ids: propertyIds })
  },

  /** Eliminar favorito por ID de favorito */
  remove(favoriteId) {
    return api.delete(`/favorites/${favoriteId}`)
  }
}

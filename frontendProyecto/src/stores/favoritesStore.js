/**
 * Store: Favoritos
 * Usa el endpoint /favorites/toggle y mantiene un Set de IDs en memoria
 * para saber instantáneamente si una propiedad está marcada o no.
 */
import { defineStore } from 'pinia'
import { favoritesApi } from '@/api/favorites'

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    favorites:   [],          // lista completa de objetos favoritos
    favoriteIds: new Set(),   // Set<number> para consultas O(1)
    loading:     false,
    error:       null
  }),

  getters: {
    isFavorite: (state) => (propertyId) => state.favoriteIds.has(propertyId)
  },

  actions: {
    /** Carga todos los favoritos del usuario autenticado */
    async fetchFavorites() {
      this.loading = true
      this.error   = null
      try {
        const { data } = await favoritesApi.getAll()
        this.favorites   = data.items ?? data
        this.favoriteIds = new Set(this.favorites.map(f => f.property_id ?? f.property?.id))
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar favoritos'
      } finally {
        this.loading = false
      }
    },

    /** Alterna favorito (agrega o quita) usando el endpoint /toggle */
    async toggleFavorite(propertyId) {
      try {
        const { data } = await favoritesApi.toggle(propertyId)
        // El backend devuelve { action: 'added'|'removed', ... }
        if (data.action === 'added') {
          this.favoriteIds.add(propertyId)
          if (data.favorite) this.favorites.push(data.favorite)
        } else {
          this.favoriteIds.delete(propertyId)
          this.favorites = this.favorites.filter(
            f => (f.property_id ?? f.property?.id) !== propertyId
          )
        }
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al actualizar favorito'
        throw err  // re-throw para que el componente pueda mostrarlo
      }
    },

    /** Limpia los favoritos al cerrar sesión */
    clear() {
      this.favorites   = []
      this.favoriteIds = new Set()
      this.error       = null
    }
  }
})

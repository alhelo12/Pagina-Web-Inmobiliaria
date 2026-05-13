/**
 * Store: Favoritos
 * Usa el endpoint /favorites/toggle y mantiene un Set de IDs en memoria
 * para saber instantaneamente si una propiedad esta marcada o no.
 */
import { defineStore } from 'pinia'
import { favoritesApi } from '@/api/favorites'
import { useAuthStore } from '@/stores/authStore'

const favoriteIdOf = (favorite) => Number(favorite?.property_id ?? favorite?.property?.id ?? favorite?.favorited_property?.id)

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    favorites: [],
    favoriteIds: new Set(),
    loading: false,
    error: null
  }),

  getters: {
    isFavorite: (state) => (propertyId) => state.favoriteIds.has(Number(propertyId))
  },

  actions: {
    async fetchFavorites() {
      const auth = useAuthStore()
      if (!auth.isLogged || !auth.userId) return

      this.loading = true
      this.error = null
      try {
        const { data } = await favoritesApi.getAll(auth.userId)
        this.favorites = data.favorites ?? data.items ?? data
        this.favoriteIds = new Set(this.favorites.map(favoriteIdOf).filter(Boolean))
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar favoritos'
      } finally {
        this.loading = false
      }
    },

    async toggleFavorite(propertyId) {
      const auth = useAuthStore()
      if (!auth.isLogged || !auth.userId) return

      const id = Number(propertyId)
      const previousIds = new Set(this.favoriteIds)
      const previousFavorites = [...this.favorites]
      const nextIds = new Set(this.favoriteIds)

      if (nextIds.has(id)) nextIds.delete(id)
      else nextIds.add(id)
      this.favoriteIds = nextIds

      try {
        const { data } = await favoritesApi.toggle(id, auth.userId)
        const isFavorited = data.is_favorited ?? data.is_favorite ?? data.action === 'added'

        if (isFavorited) {
          this.favoriteIds = new Set([...this.favoriteIds, id])
          if (data.favorite && !this.favorites.some((fav) => favoriteIdOf(fav) === id)) {
            this.favorites = [...this.favorites, data.favorite]
          }
          return data
        }

        const confirmedIds = new Set(this.favoriteIds)
        confirmedIds.delete(id)
        this.favoriteIds = confirmedIds
        this.favorites = this.favorites.filter((fav) => favoriteIdOf(fav) !== id)
        return data
      } catch (err) {
        console.warn('[Favoritos] Error al sincronizar con el servidor:', err.response?.data?.detail || err.message)
      }
    },

    clear() {
      this.favorites = []
      this.favoriteIds = new Set()
      this.error = null
    }
  }
})

import { defineStore } from 'pinia'

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    favorites: JSON.parse(localStorage.getItem('favorites')) || []
  }),

  getters: {
    isFavorite: (state) => (id) =>
      state.favorites.some(p => p.id === id)
  },

  actions: {
    toggleFavorite(property) {
      const index = this.favorites.findIndex(p => p.id === property.id)

      if (index === -1) {
        this.favorites.push(property)
      } else {
        this.favorites.splice(index, 1)
      }

      // 🔥 guardar en localStorage
      localStorage.setItem('favorites', JSON.stringify(this.favorites))
    }
  }
})

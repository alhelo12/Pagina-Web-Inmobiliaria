<script setup>
import { useFavoritesStore } from '@/stores/favoritesStore'
import PropertyCard from '@/components/PropertyCard.vue'

const favStore = useFavoritesStore()
</script>

<template>
  <section class="favorites">
    <h1>Mis Favoritos ❤️</h1>

    <div v-if="favStore.favorites.length" class="grid">
      <PropertyCard
        v-for="p in favStore.favorites"
        :key="p.id"
        v-bind="p"
      />
    </div>

    <p v-else class="empty">
      Aún no tienes propiedades favoritas.
    </p>
  </section>
</template>

<style scoped>
.favorites {
  padding: 60px 20px;
  max-width: 1200px;
  margin: auto;
  text-align: center;
}

.grid {
  margin-top: 30px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.empty {
  margin-top: 40px;
  color: #777;
}
</style>

<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useFavoritesStore } from '@/stores/favoritesStore'
import PropertyCard from '@/components/PropertyCard.vue'

const favStore = useFavoritesStore()

onMounted(() => favStore.fetchFavorites())
</script>

<template>
  <section class="favorites">
    <h1>Mis Favoritos ❤️</h1>

    <div v-if="favStore.loading" class="state">
      <div class="spinner"></div>
    </div>

    <div v-else-if="favStore.error" class="state error-msg">
      {{ favStore.error }}
    </div>

    <div v-else-if="!favStore.favorites.length" class="state">
      <p>Aún no tienes propiedades favoritas.</p>
      <RouterLink to="/propiedades" class="btn">Ver propiedades</RouterLink>
    </div>

    <div v-else class="grid">
      <RouterLink
        v-for="fav in favStore.favorites"
        :key="fav.id"
        :to="`/propiedades/${fav.property?.id ?? fav.property_id}`"
        class="card-link"
      >
        <PropertyCard
          :id="fav.property?.id ?? fav.property_id"
          :title="fav.property?.title"
          :price="fav.property?.price"
          :city="fav.property?.city"
          :type="fav.property?.property_type"
          :image="fav.property?.images?.[0]?.image_url ?? 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c'"
        />
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.favorites {
  padding: 60px 20px; max-width: 1200px;
  margin: auto; text-align: center;
  font-family: 'Poppins', sans-serif;
}

h1 { font-size: 32px; margin-bottom: 40px; }

.state {
  display: flex; flex-direction: column; align-items: center;
  gap: 16px; padding: 60px 20px; color: #666;
}
.error-msg { color: #991b1b; }

.spinner {
  width: 40px; height: 40px;
  border: 3px solid #f3f3f3; border-top-color: #f59e0b;
  border-radius: 50%; animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.btn {
  display: inline-block; margin-top: 8px;
  background: #f59e0b; color: white;
  padding: 10px 24px; border-radius: 8px; font-weight: 600;
  text-decoration: none;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px; text-align: left;
}
.card-link { text-decoration: none; color: inherit; }

@media (max-width: 1024px) { .grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px)  { .grid { grid-template-columns: 1fr; } }
</style>

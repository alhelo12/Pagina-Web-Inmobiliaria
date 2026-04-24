<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import PropertyCard from '@/components/PropertyCard.vue'
import { propertiesApi } from '@/api/properties'

const properties = ref([])
const loading    = ref(true)

onMounted(async () => {
  try {
    const { data } = await propertiesApi.getAll({ status: 'approved', limit: 3 })
    const all = data.items ?? data
    // Mostramos máx 3 aleatoriamente
    properties.value = [...all].sort(() => Math.random() - 0.5).slice(0, 3)
  } catch {
    // En caso de error no mostramos nada; el home no debe romperse
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section v-if="loading || properties.length" class="featured">
    <h2>Propiedades disponibles</h2>

    <div v-if="loading" class="skeleton-grid">
      <div v-for="n in 3" :key="n" class="skeleton-card"></div>
    </div>

    <div v-else class="featured-grid">
      <RouterLink
        v-for="p in properties"
        :key="p.id"
        :to="`/propiedades/${p.id}`"
        class="card-link"
      >
        <PropertyCard
          :id="p.id"
          :title="p.title"
          :price="p.price"
          :city="p.city"
          :type="p.property_type"
          :image="p.images?.[0]?.image_url ?? 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c'"
        />
      </RouterLink>
    </div>

    <div class="ver-mas">
      <RouterLink to="/propiedades" class="btn-ver-mas">
        Ver todas las propiedades →
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.featured {
  padding: 80px 20px; max-width: 1200px;
  margin: auto; text-align: center;
}

h2 { font-size: 30px; margin-bottom: 40px; color: #0f2a44; }

/* GRID real */
.featured-grid {
  display: grid; grid-template-columns: 1fr;
  gap: 24px; margin-bottom: 40px;
}
.card-link { text-decoration: none; color: inherit; }

/* SKELETON */
.skeleton-grid { display: grid; grid-template-columns: 1fr; gap: 24px; margin-bottom: 40px; }
.skeleton-card {
  height: 320px; border-radius: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
}
@keyframes shimmer { to { background-position: -400% 0; } }

.ver-mas { margin-top: 20px; }
.btn-ver-mas {
  display: inline-block; padding: 12px 28px;
  background: #0f2a44; color: white;
  border-radius: 8px; font-weight: 600;
  text-decoration: none; transition: background .2s;
}
.btn-ver-mas:hover { background: #1e3a5f; }

@media (min-width: 768px) {
  .featured-grid { grid-template-columns: repeat(3, 1fr); }
  .skeleton-grid  { grid-template-columns: repeat(3, 1fr); }
}
</style>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import PropertyCard from '@/components/PropertyCard.vue'
import { propertiesApi } from '@/api/properties'
import { getPropertyImage } from '@/utils/propertyImages'

const properties = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await propertiesApi.getAll({ status: 'approved', limit: 3 })
    const all = data.properties ?? data.items ?? data
    properties.value = [...all].sort(() => Math.random() - 0.5).slice(0, 3)
  } catch {
    // El home se mantiene presentable aunque la API no responda.
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section v-if="loading || properties.length" class="featured">
    <div class="section-heading">
      <span>Recent Projects</span>
      <h2>Propiedades destacadas</h2>
    </div>

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
          :image="getPropertyImage(p)"
        />
      </RouterLink>
    </div>

    <div class="ver-mas">
      <RouterLink to="/propiedades" class="btn-ver-mas">
        Ver todas las propiedades
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.featured {
  padding: 80px 24px;
  max-width: 1180px;
  margin: auto;
}

.section-heading {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 34px;
  border-bottom: 1px solid rgba(7, 23, 45, .14);
  padding-bottom: 18px;
}

.section-heading span {
  color: #d6a848;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: .16em;
  text-transform: uppercase;
}

h2 {
  font-family: Georgia, 'Times New Roman', serif;
  color: #07172d;
  font-size: clamp(32px, 4vw, 44px);
}

.featured-grid,
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 38px;
}

.card-link {
  text-decoration: none;
  color: inherit;
}

.skeleton-card {
  height: 340px;
  border-radius: 10px;
  background: linear-gradient(90deg, #efe8dc 25%, #fffaf1 50%, #efe8dc 75%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
}

@keyframes shimmer { to { background-position: -400% 0; } }

.ver-mas {
  text-align: center;
}

.btn-ver-mas {
  display: inline-flex;
  min-height: 46px;
  align-items: center;
  padding: 0 24px;
  background: #07172d;
  color: white;
  border-radius: 8px;
  font-weight: 900;
  box-shadow: var(--shadow-soft);
  transition: transform .2s ease, background .2s ease;
}

.btn-ver-mas:hover {
  background: #102e4f;
  transform: translateY(-2px);
}

@media (max-width: 900px) {
  .featured-grid,
  .skeleton-grid {
    grid-template-columns: 1fr;
  }
  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import FiltersBar from '@/components/properties/FiltersBar.vue'
import PropertyCard from '@/components/PropertyCard.vue'
import { propertiesApi } from '@/api/properties'
import { useAuthStore } from '@/stores/authStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { getPropertyImage } from '@/utils/propertyImages'

const properties = ref([])
const loading    = ref(false)
const error      = ref('')
const auth = useAuthStore()
const favStore = useFavoritesStore()

const load = async (filters = {}) => {
  loading.value = true
  error.value   = ''
  try {
    const { data } = await propertiesApi.getAll({ status: 'approved', ...filters })
    properties.value = data.properties ?? data.items ?? data
  } catch {
    error.value = 'No se pudieron cargar las propiedades'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await load()
  if (auth.isLogged && auth.role === 'client') {
    await favStore.fetchFavorites()
  }
})
</script>

<template>
  <main class="properties-page">
    <header class="properties-header reveal">
      <p class="eyebrow">PROPIEDADES</p>
      <h1>Encuentra tu hogar ideal</h1>
      <p class="subtitle">Descubre nuestra selección de propiedades disponibles</p>
    </header>

    <section class="properties-container">
      <FiltersBar @filter="load" />

      <div v-if="loading" class="state reveal">
        <div class="spinner"></div>
        <p>Cargando propiedades...</p>
      </div>

      <div v-else-if="error" class="state error-state reveal">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="load()">Reintentar</button>
      </div>

      <div v-else-if="!properties.length" class="state empty-state reveal">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <p class="empty-title">No hay propiedades disponibles</p>
        <p class="empty-subtitle">Intenta ajustar los filtros para ver más resultados</p>
      </div>

      <div v-else class="grid reveal">
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
          :transactionType="p.transaction_type"
          :bedrooms="p.bedrooms"
          :bathrooms="p.bathrooms"
          :squareMeters="p.square_meters"
          :images="p.images || []"
          :showCta="true"
        />
        </RouterLink>
      </div>
    </section>
  </main>
</template>

<style scoped>


.properties-page {
  background: #f5f2ec;
  min-height: 100vh;
  font-family: 'Poppins', sans-serif;
}

.properties-header {
  padding: 50px 20px 40px;
  text-align: center;
}

.eyebrow {
  color: #d8a54d;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.properties-header h1 {
  font-size: 34px;
  font-weight: 600;
  color: #07182c;
  margin: 0 0 12px;
}

.subtitle {
  color: #666;
  font-size: 15px;
  margin: 0;
}

.properties-container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 40px 70px;
}

.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top-color: #d8a54d;
  border-radius: 50%;
  animation: spin .8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.error-state {
  color: #991b1b;
}

.error-state svg {
  color: #991b1b;
}

.retry-btn {
  padding: 10px 24px;
  background: #d8a54d;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  transition: background .2s, transform .2s;
}

.retry-btn:hover {
  background: #c4943f;
  transform: translateY(-2px);
}

.empty-state svg {
  color: #d8a54d;
  opacity: 0.6;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #07182c;
  margin: 0;
}

.empty-subtitle {
  font-size: 14px;
  margin: 0;
  color: #888;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
  margin-top: 10px;
}

.card-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.reveal {
  animation: fadeUp .7s ease both;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1024px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 640px) {
  .properties-header {
    padding: 40px 20px 30px;
  }

  .properties-header h1 {
    font-size: 26px;
  }

  .properties-container {
    padding: 0 20px 50px;
  }

  .grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}
</style>
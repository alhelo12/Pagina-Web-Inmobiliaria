<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import FiltersBar from '@/components/properties/FiltersBar.vue'
import PropertyCard from '@/components/PropertyCard.vue'
import { propertiesApi } from '@/api/properties'
import { useAuthStore } from '@/stores/authStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { getPropertyImage } from '@/utils/propertyImages'

const route = useRoute()
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
  } catch (err) {
    console.error('[PropertiesView] Error al cargar propiedades:', err?.response?.status ?? err?.message)
    error.value = 'No se pudieron cargar las propiedades'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await load(route.query)
  if (auth.isLogged && auth.role === 'client') {
    await favStore.fetchFavorites()
  }
})
</script>

<template>
  <div class="properties-page">
    <header class="properties-header reveal">
      <p class="eyebrow-label">Catálogo — Jakeda</p>
      <h1 class="serif-display">Propiedades singulares</h1>
      <p class="subtitle">Una selección curada de casas, departamentos y terrenos</p>
      <div class="title-rule" aria-hidden="true"><span></span></div>
    </header>

    <section class="properties-container">
      <FiltersBar @filter="load" />

      <div v-if="loading" class="state reveal">
        <div class="spinner"></div>
        <p>Cargando propiedades...</p>
      </div>

      <div v-else-if="error" class="state error-state reveal" role="alert">
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
        <p class="empty-title serif-display">Nada por aquí, todavía</p>
        <p class="empty-subtitle">Ajusta los filtros para ver más resultados</p>
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
  </div>
</template>

<style scoped>
.properties-page {
  background: var(--color-ivory);
  color: var(--color-ink);
  min-height: 100vh;
  font-family: var(--sans);
}

.properties-header {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 64px var(--container-pad) 10px;
  text-align: left;
}

.properties-header h1 {
  margin: 10px 0 12px;
  font-size: clamp(40px, 5.4vw, 68px);
  color: var(--color-petrol);
}

.subtitle {
  margin: 0;
  color: var(--color-muted);
  font-size: 15px;
  font-family: var(--serif);
  font-style: italic;
  font-size: 19px;
}

.title-rule {
  display: flex;
  justify-content: flex-start;
  margin: 26px 0 0;
  border-top: 1px solid var(--color-line);
  max-width: 720px;
  position: relative;
}

.title-rule span {
  position: absolute;
  top: -1px;
  width: 72px;
  height: 2px;
  background: var(--color-brass);
}

.properties-container {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 18px var(--container-pad) 80px;
}

.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 70px 20px;
  color: var(--color-muted);
  gap: 16px;
  border-top: 1px solid var(--color-line);
  margin-top: 26px;
}

.spinner {
  width: 38px;
  height: 38px;
  border: 2px solid var(--color-line);
  border-top-color: var(--color-brass-deep);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.error-state { color: var(--color-danger); }

.retry-btn {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 13px 28px;
  background: var(--color-petrol);
  color: #fff;
  border: 1px solid var(--color-petrol);
  font-size: 12px;
  letter-spacing: .14em;
  text-transform: uppercase;
  font-weight: 600;
  cursor: pointer;
  transition: background .2s ease;
}

.retry-btn:hover { background: var(--color-ink); }

.empty-state svg {
  color: var(--color-brass-deep);
  opacity: .7;
}

.empty-title {
  font-size: 28px;
  color: var(--color-petrol);
  margin: 0;
}

.empty-subtitle {
  font-size: 14px;
  margin: 0;
  color: var(--color-muted);
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
  margin-top: 34px;
}

.card-link {
  text-decoration: none;
  color: inherit;
  display: block;
  min-width: 0;
}

.reveal {
  animation: fadeUp .7s ease both;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 1024px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 640px) {
  .properties-header { padding: 48px 20px 8px; }
  .properties-container { padding: 14px 20px 56px; }
  .grid { grid-template-columns: 1fr; gap: 22px; }
}
</style>

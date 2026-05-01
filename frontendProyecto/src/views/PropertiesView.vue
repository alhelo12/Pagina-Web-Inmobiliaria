<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import FiltersBar from '@/components/properties/FiltersBar.vue'
import PropertyCard from '@/components/PropertyCard.vue'
import { propertiesApi } from '@/api/properties'
import { useAuthStore } from '@/stores/authStore'
import { useFavoritesStore } from '@/stores/favoritesStore'

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
  <section class="properties">
    <h1>Propiedades</h1>
    <p class="subtitle">Descubre nuestra selección de propiedades disponibles</p>

    <FiltersBar @filter="load" />

    <!-- ESTADO DE CARGA -->
    <div v-if="loading" class="state">
      <div class="spinner"></div>
      <p>Cargando propiedades...</p>
    </div>

    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <div v-else-if="!properties.length" class="state">
      No hay propiedades disponibles con esos filtros.
    </div>

    <!-- GRID -->
    <div v-else class="grid">
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
  </section>
</template>

<style scoped>
.properties {
  padding: 60px 40px;
  font-family: 'Poppins', sans-serif;
}

h1       { text-align: center; font-size: 34px; font-weight: 600; }
.subtitle { text-align: center; color: #666; font-size: 15px; margin-bottom: 40px; }

/* ESTADO */
.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  color: #666;
  gap: 16px;
}
.error-msg { color: #991b1b; }

.spinner {
  width: 40px; height: 40px;
  border: 3px solid #f3f3f3;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* GRID */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}

.card-link { text-decoration: none; color: inherit; display: block; }

@media (max-width: 1024px) { .grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px)  {
  .properties { padding: 40px 20px; }
  h1 { font-size: 26px; }
  .grid { grid-template-columns: 1fr; }
}
</style>

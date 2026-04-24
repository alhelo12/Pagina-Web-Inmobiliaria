<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { propertiesApi } from '@/api/properties'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useAuthStore } from '@/stores/authStore'

const route    = useRoute()
const favStore = useFavoritesStore()
const auth     = useAuthStore()

const property   = ref(null)
const loading    = ref(true)
const error      = ref('')
const activeImg  = ref(0)
const toggling   = ref(false)

onMounted(async () => {
  try {
    const { data } = await propertiesApi.getById(route.params.id)
    property.value = data
  } catch {
    error.value = 'Propiedad no encontrada'
  } finally {
    loading.value = false
  }
})

const toggleFav = async () => {
  if (!auth.isLogged) return
  toggling.value = true
  try {
    await favStore.toggleFavorite(property.value.id)
  } finally {
    toggling.value = false
  }
}

const typeLabel = { house: 'Casa', apartment: 'Departamento', land: 'Terreno', commercial: 'Local' }
const txLabel   = { sale: 'Venta', rent: 'Renta' }
</script>

<template>
  <!-- CARGA -->
  <div v-if="loading" class="state">
    <div class="spinner"></div>
  </div>

  <!-- ERROR -->
  <p v-else-if="error" class="state error-msg">{{ error }}</p>

  <!-- DETALLE -->
  <section v-else class="detail">

    <!-- GALERÍA -->
    <div class="gallery">
      <img
        :src="property.images?.[activeImg]?.image_url ?? 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c'"
        :alt="property.title"
        class="main-img"
      />
      <div v-if="property.images?.length > 1" class="thumbs">
        <img
          v-for="(img, i) in property.images"
          :key="img.id"
          :src="img.image_url"
          :class="['thumb', { active: activeImg === i }]"
          @click="activeImg = i"
        />
      </div>
    </div>

    <!-- INFO -->
    <div class="info">
      <!-- BADGES -->
      <div class="badges">
        <span class="badge type">{{ typeLabel[property.property_type] ?? property.property_type }}</span>
        <span class="badge tx">{{ txLabel[property.transaction_type] ?? property.transaction_type }}</span>
      </div>

      <h1>{{ property.title }}</h1>
      <p class="location">📍 {{ property.address }}, {{ property.city }}</p>

      <div class="price">${{ Number(property.price).toLocaleString('es-MX') }} MXN</div>

      <p class="description">{{ property.description }}</p>

      <!-- CARACTERÍSTICAS -->
      <div class="features">
        <div class="feat" v-if="property.bedrooms">
          <span class="feat-icon">🛏</span>
          <span>{{ property.bedrooms }} Recámaras</span>
        </div>
        <div class="feat" v-if="property.bathrooms">
          <span class="feat-icon">🛁</span>
          <span>{{ property.bathrooms }} Baños</span>
        </div>
        <div class="feat" v-if="property.square_meters">
          <span class="feat-icon">📐</span>
          <span>{{ property.square_meters }} m²</span>
        </div>
      </div>

      <!-- ACCIONES -->
      <div class="actions">
        <RouterLink to="/contacto" class="btn-primary">
          Contactar asesor
        </RouterLink>

        <button
          v-if="auth.isLogged && auth.role === 'client'"
          class="btn-fav"
          :class="{ active: favStore.isFavorite(property.id) }"
          :disabled="toggling"
          @click="toggleFav"
        >
          {{ favStore.isFavorite(property.id) ? '❤️ Guardado' : '🤍 Guardar' }}
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* STATE */
.state {
  display: flex; justify-content: center; align-items: center;
  padding: 80px; color: #666;
}
.error-msg { color: #991b1b; }
.spinner {
  width: 48px; height: 48px;
  border: 3px solid #f3f3f3; border-top-color: #f59e0b;
  border-radius: 50%; animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* LAYOUT */
.detail {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 40px;
  padding: 60px 40px;
  max-width: 1200px;
  margin: auto;
}

/* GALERÍA */
.main-img  { width: 100%; border-radius: 16px; object-fit: cover; max-height: 460px; }
.thumbs    { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.thumb     { width: 80px; height: 60px; object-fit: cover; border-radius: 8px; cursor: pointer; opacity: .6; transition: opacity .2s; }
.thumb.active { opacity: 1; outline: 2px solid #f59e0b; }

/* BADGES */
.badges { display: flex; gap: 8px; margin-bottom: 12px; }
.badge  { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge.type { background: #e0f2fe; color: #0369a1; }
.badge.tx   { background: #fef3c7; color: #92400e; }

/* INFO */
.info h1     { font-size: 30px; margin-bottom: 8px; }
.location    { color: #777; margin-bottom: 16px; }
.price       { font-size: 28px; font-weight: 700; color: #0d2c54; margin-bottom: 20px; }
.description { line-height: 1.7; color: #555; margin-bottom: 24px; }

/* FEATURES */
.features { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 32px; }
.feat      { display: flex; align-items: center; gap: 6px; font-size: 15px; font-weight: 500; }
.feat-icon { font-size: 20px; }

/* ACCIONES */
.actions { display: flex; gap: 12px; flex-wrap: wrap; }

.btn-primary {
  display: inline-block;
  background: #f59e0b; color: white;
  padding: 12px 24px; border-radius: 10px;
  font-size: 15px; font-weight: 600;
  text-decoration: none; transition: background .2s;
}
.btn-primary:hover { background: #e6951c; }

.btn-fav {
  padding: 12px 20px; border-radius: 10px;
  border: 2px solid #e5e7eb; background: white;
  font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all .2s;
}
.btn-fav.active  { border-color: #ef4444; color: #ef4444; }
.btn-fav:hover   { border-color: #f59e0b; }
.btn-fav:disabled { opacity: .6; cursor: not-allowed; }

@media (max-width: 900px) {
  .detail { grid-template-columns: 1fr; padding: 40px 20px; }
}
</style>

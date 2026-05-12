<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { propertiesApi } from '@/api/properties'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useAuthStore } from '@/stores/authStore'
import { FALLBACK_PROPERTY_IMAGE, normalizeImageUrl } from '@/utils/propertyImages'
import AppIcon from '@/components/shared/AppIcon.vue'

const route    = useRoute()
const favStore = useFavoritesStore()
const auth     = useAuthStore()

const property  = ref(null)
const loading   = ref(true)
const error     = ref('')
const activeImg = ref(0)
const toggling  = ref(false)
const isAnimating = ref(false)
const lightboxOpen = ref(false)

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

const images = computed(() => {
  if (!property.value?.images?.length) {
    return [{ id: 0, image_url: FALLBACK_PROPERTY_IMAGE }]
  }
  return property.value.images.map((img) => ({
    ...img,
    image_url: normalizeImageUrl(img.image_url)
  }))
})

const goTo = (index) => {
  if (isAnimating.value) return
  isAnimating.value = true
  activeImg.value = (index + images.value.length) % images.value.length
  setTimeout(() => { isAnimating.value = false }, 400)
}

const prev = () => goTo(activeImg.value - 1)
const next = () => goTo(activeImg.value + 1)

// Keyboard navigation
const onKey = (e) => {
  if (lightboxOpen.value) {
    if (e.key === 'ArrowLeft') prev()
    if (e.key === 'ArrowRight') next()
    if (e.key === 'Escape') lightboxOpen.value = false
  } else {
    if (e.key === 'ArrowLeft') prev()
    if (e.key === 'ArrowRight') next()
  }
}
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => window.removeEventListener('keydown', onKey))

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
const txLabel   = { sale: 'En Venta', rent: 'En Renta' }
</script>

<template>
  <!-- CARGA -->
  <div v-if="loading" class="state">
    <div class="spinner"></div>
    <p>Cargando propiedad...</p>
  </div>

  <!-- ERROR -->
  <div v-else-if="error" class="state">
    <p class="error-msg">{{ error }}</p>
    <RouterLink to="/propiedades" class="btn-back">← Volver a propiedades</RouterLink>
  </div>

  <!-- DETALLE -->
  <div v-else class="detail-page">

    <!-- HERO CON CARRUSEL -->
    <div class="carousel-section">

      <!-- Imagen principal -->
      <div class="carousel-main">
        <img
          :key="activeImg"
          :src="images[activeImg]?.image_url"
          :alt="property.title"
          class="carousel-img"
          style="cursor:zoom-in"
          @click="lightboxOpen = true"
        />

        <!-- Hint ver en grande -->
        <div class="zoom-hint" @click="lightboxOpen = true">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
          Ver en grande
        </div>

        <!-- Overlay degradado -->
        <div class="carousel-overlay"></div>

        <!-- Contador -->
        <div class="img-counter">{{ activeImg + 1 }} / {{ images.length }}</div>

        <!-- Flechas -->
        <button v-if="images.length > 1" class="arrow arrow-left" @click="prev" aria-label="Anterior">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <button v-if="images.length > 1" class="arrow arrow-right" @click="next" aria-label="Siguiente">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>

        <!-- Título sobre la imagen -->
        <div class="carousel-title-box">
          <div class="badges">
            <span class="badge type">{{ typeLabel[property.property_type] ?? property.property_type }}</span>
            <span class="badge tx">{{ txLabel[property.transaction_type] ?? property.transaction_type }}</span>
          </div>
          <h1>{{ property.title }}</h1>
          <p class="carousel-location">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            {{ property.address }}, {{ property.city }}
          </p>
        </div>
      </div>

      <!-- Miniaturas -->
      <div v-if="images.length > 1" class="thumbs-row">
        <button
          v-for="(img, i) in images"
          :key="img.id"
          :class="['thumb-btn', { active: activeImg === i }]"
          @click="goTo(i)"
        >
          <img :src="img.image_url" :alt="`Imagen ${i + 1}`" />
          <div class="thumb-overlay"></div>
        </button>
      </div>

    </div>

    <!-- CONTENIDO PRINCIPAL -->
    <div class="content-grid">

      <!-- INFO IZQUIERDA -->
      <div class="info-col">

        <div class="price-row">
          <div class="price">${{ Number(property.price).toLocaleString('es-MX') }} <span>MXN</span></div>
          <button
            v-if="auth.isLogged && auth.role === 'client'"
            class="btn-fav"
            :class="{ active: favStore.isFavorite(property.id) }"
            :disabled="toggling"
            @click="toggleFav"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" :fill="favStore.isFavorite(property.id) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
            {{ favStore.isFavorite(property.id) ? 'Guardado' : 'Guardar' }}
          </button>
        </div>

        <!-- Características -->
        <div class="features-grid">
          <div class="feat-card" v-if="property.bedrooms">
            <div class="feat-icon">🛏</div>
            <div class="feat-info">
              <span class="feat-val">{{ property.bedrooms }}</span>
              <span class="feat-label">Recámaras</span>
            </div>
          </div>
          <div class="feat-card" v-if="property.bathrooms">
            <div class="feat-icon">🛁</div>
            <div class="feat-info">
              <span class="feat-val">{{ property.bathrooms }}</span>
              <span class="feat-label">Baños</span>
            </div>
          </div>
          <div class="feat-card" v-if="property.square_meters">
            <div class="feat-icon">📐</div>
            <div class="feat-info">
              <span class="feat-val">{{ property.square_meters }}</span>
              <span class="feat-label">m²</span>
            </div>
          </div>
        </div>

        <!-- Descripción -->
        <div class="section-block">
          <h2 class="section-title">Descripción</h2>
          <p class="description">{{ property.description }}</p>
        </div>

        <!-- Ubicación -->
        <div class="section-block">
          <h2 class="section-title">Ubicación</h2>
          <div class="location-card">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            <span>{{ property.address }}, {{ property.city }}</span>
          </div>
        </div>

      </div>

      <!-- SIDEBAR DERECHA -->
      <div class="sidebar-col">
        <div class="contact-card">
          <h3>¿Te interesa esta propiedad?</h3>
          <p>Contáctanos y un asesor te atenderá a la brevedad.</p>
          <RouterLink to="/contacto" class="btn-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.44 2 2 0 0 1 3.58 1.25h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.8a16 16 0 0 0 6 6l.92-.92a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21.73 16.92z"/></svg>
            Contactar asesor
          </RouterLink>
          <RouterLink to="/propiedades" class="btn-secondary">
            ← Ver más propiedades
          </RouterLink>
        </div>
      </div>

    </div>

    <!-- LIGHTBOX -->
    <Teleport to="body">
      <Transition name="lb">
        <div v-if="lightboxOpen" class="lb-backdrop" @click.self="lightboxOpen = false">
          <div class="lb-panel">
            <div class="lb-header">
              <span class="lb-counter">{{ activeImg + 1 }} / {{ images.length }}</span>
              <span class="lb-label">{{ images[activeImg]?.label || property.title }}</span>
              <button class="lb-close" @click="lightboxOpen = false"><AppIcon name="x" :size="20" /></button>
            </div>
            <div class="lb-img-wrap">
              <button v-if="images.length > 1" class="lb-arrow lb-prev" @click.stop="prev">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
              </button>
              <Transition name="img-fade" mode="out-in">
                <img :key="activeImg" :src="images[activeImg]?.image_url" :alt="images[activeImg]?.label || property.title" class="lb-img" />
              </Transition>
              <button v-if="images.length > 1" class="lb-arrow lb-next" @click.stop="next">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="9 18 15 12 9 6"/></svg>
              </button>
            </div>
            <div v-if="images.length > 1" class="lb-thumbs">
              <button
                v-for="(img, i) in images"
                :key="i"
                :class="['lb-thumb', { active: activeImg === i }]"
                @click.stop="goTo(i)"
              >
                <img :src="img.image_url" :alt="`thumb-${i}`" />
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<style scoped>


* { box-sizing: border-box; }

.detail-page {
  font-family: 'Poppins', sans-serif;
  background: #f5f2ec;
  min-height: 100vh;
}

/* ── STATE ── */
.state {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 16px; padding: 100px 20px;
  color: #666; font-family: 'Poppins', sans-serif;
}
.error-msg { color: #991b1b; font-size: 16px; }
.spinner {
  width: 48px; height: 48px;
  border: 3px solid #e5e5e5;
  border-top-color: #d4a34a;
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── CARRUSEL ── */
.carousel-section {
  width: 100%;
  background: #07172d;
}

.carousel-main {
  position: relative;
  width: 100%;
  height: 520px;
  overflow: hidden;
}

.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0.6; transform: scale(1.02); }
  to   { opacity: 1;   transform: scale(1); }
}

.carousel-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(7,23,45,0.15) 0%,
    rgba(7,23,45,0.0) 40%,
    rgba(7,23,45,0.75) 100%
  );
}

/* Contador */
.img-counter {
  position: absolute;
  top: 20px; right: 20px;
  background: rgba(0,0,0,0.5);
  color: white;
  font-size: 13px;
  font-weight: 500;
  padding: 5px 12px;
  border-radius: 20px;
  backdrop-filter: blur(4px);
}

/* Flechas */
.arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 48px; height: 48px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s, transform 0.2s;
  z-index: 10;
}
.arrow:hover {
  background: rgba(255,255,255,0.28);
  transform: translateY(-50%) scale(1.08);
}
.arrow-left  { left: 24px; }
.arrow-right { right: 24px; }

/* Título sobre imagen */
.carousel-title-box {
  position: absolute;
  bottom: 32px; left: 40px; right: 140px;
  z-index: 5;
}

.badges { display: flex; gap: 8px; margin-bottom: 10px; }
.badge  {
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 11px; font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}
.badge.type { background: rgba(255,255,255,0.2); color: white; backdrop-filter: blur(4px); border: 1px solid rgba(255,255,255,0.3); }
.badge.tx   { background: #d4a34a; color: #07172d; }

.carousel-title-box h1 {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin: 0 0 8px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.3);
  line-height: 1.2;
}

.carousel-location {
  display: flex; align-items: center; gap: 6px;
  color: rgba(255,255,255,0.85);
  font-size: 14px;
  margin: 0;
}

/* Miniaturas */
.thumbs-row {
  display: flex;
  gap: 6px;
  padding: 10px 40px;
  background: #07172d;
  overflow-x: auto;
  scrollbar-width: thin;
  scrollbar-color: #d4a34a #07172d;
}

.thumb-btn {
  flex-shrink: 0;
  width: 110px; height: 72px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid transparent;
  cursor: pointer;
  padding: 0;
  position: relative;
  transition: border-color 0.2s, transform 0.2s;
}

.thumb-btn img {
  width: 100%; height: 100%;
  object-fit: cover;
}

.thumb-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.35);
  transition: opacity 0.2s;
}

.thumb-btn.active {
  border-color: #d4a34a;
  transform: scale(1.05);
}
.thumb-btn.active .thumb-overlay { opacity: 0; }
.thumb-btn:hover .thumb-overlay   { opacity: 0; }

/* ── CONTENIDO ── */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 32px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 40px 60px;
}

/* PRECIO */
.price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 28px;
}

.price {
  font-size: 32px;
  font-weight: 700;
  color: #07172d;
}
.price span {
  font-size: 18px;
  font-weight: 400;
  color: #888;
}

/* Características */
.features-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 36px;
}

.feat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  border: 1px solid #e8e4dc;
  border-radius: 12px;
  padding: 14px 20px;
  flex: 1;
  min-width: 110px;
}

.feat-icon { font-size: 22px; }
.feat-info { display: flex; flex-direction: column; }
.feat-val   { font-size: 20px; font-weight: 700; color: #07172d; line-height: 1; }
.feat-label { font-size: 12px; color: #888; margin-top: 2px; }

/* Secciones */
.section-block { margin-bottom: 32px; }

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: #07172d;
  margin: 0 0 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e8e4dc;
}

.description {
  font-size: 15px;
  line-height: 1.8;
  color: #555;
  margin: 0;
}

.location-card {
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
  border: 1px solid #e8e4dc;
  border-radius: 10px;
  padding: 14px 18px;
  font-size: 14px;
  color: #444;
}
.location-card svg { color: #d4a34a; flex-shrink: 0; }

/* ── SIDEBAR ── */
.contact-card {
  background: white;
  border: 1px solid #e8e4dc;
  border-radius: 16px;
  padding: 28px 24px;
  position: sticky;
  top: 24px;
}

.contact-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: #07172d;
  margin: 0 0 8px;
}

.contact-card p {
  font-size: 14px;
  color: #777;
  line-height: 1.6;
  margin: 0 0 24px;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  background: #d4a34a;
  color: #07172d;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.2s, box-shadow 0.2s;
  margin-bottom: 10px;
}
.btn-primary:hover {
  background: #c49238;
  box-shadow: 0 4px 14px rgba(212,163,74,0.35);
}

.btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 12px;
  background: transparent;
  color: #07172d;
  border: 1.5px solid #ddd;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  text-decoration: none;
  transition: border-color 0.2s, background 0.2s;
}
.btn-secondary:hover {
  border-color: #07172d;
  background: #f5f2ec;
}

/* Favorito */
.btn-fav {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: 10px;
  border: 1.5px solid #e5e7eb;
  background: white;
  font-size: 14px;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  color: #888;
  transition: all 0.2s;
}
.btn-fav.active { border-color: #ef4444; color: #ef4444; }
.btn-fav:hover  { border-color: #d4a34a; color: #d4a34a; }
.btn-fav:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-back {
  color: #07172d;
  text-decoration: none;
  font-size: 14px;
  font-family: 'Poppins', sans-serif;
}

/* ── RESPONSIVE ── */
@media (max-width: 900px) {
  .carousel-main { height: 340px; }
  .carousel-title-box { left: 20px; right: 80px; bottom: 20px; }
  .carousel-title-box h1 { font-size: 22px; }
  .thumbs-row { padding: 8px 16px; }
  .content-grid { grid-template-columns: 1fr; padding: 28px 20px 48px; }
  .contact-card { position: static; }
  .arrow-left { left: 12px; }
  .arrow-right { right: 12px; }
}

@media (max-width: 480px) {
  .carousel-main { height: 260px; }
  .carousel-title-box { left: 16px; right: 16px; bottom: 16px; }
  .carousel-title-box h1 { font-size: 18px; }
  .thumb-btn { width: 80px; height: 54px; }
  .price { font-size: 22px; }
  .price span { font-size: 14px; }
  .content-grid { padding: 20px 14px 36px; }
  .feat-card { min-width: 100%; }
  .contact-card { padding: 20px 16px; }
  .btn-primary { font-size: 14px; padding: 12px; }
  .btn-fav { width: 100%; justify-content: center; }
}

/* ── ZOOM HINT ── */
.zoom-hint {
  position: absolute;
  bottom: 100px;
  right: 20px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(0,0,0,0.5);
  color: white;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: background 0.2s;
}
.zoom-hint:hover { background: rgba(212,163,74,0.8); }

/* ── LIGHTBOX ── */
.lb-backdrop {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(7,23,45,0.94);
  display: flex; align-items: center; justify-content: center;
  padding: 20px; backdrop-filter: blur(8px);
}
.lb-panel { width: 100%; max-width: 960px; display: flex; flex-direction: column; gap: 12px; max-height: 92vh; }
.lb-header { display: flex; align-items: center; gap: 12px; color: white; }
.lb-panel { width: 100%; max-width: 960px; display: flex; flex-direction: column; gap: 12px; max-height: 92vh; font-family: 'Poppins', sans-serif; }
.lb-label { font-size: 14px; color: rgba(255,255,255,0.7); flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.lb-close { width: 36px; height: 36px; border: none; border-radius: 50%; background: rgba(255,255,255,0.12); color: white; font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: background 0.2s; }
.lb-close:hover { background: rgba(255,255,255,0.25); }
.lb-img-wrap { position: relative; display: flex; align-items: center; justify-content: center; border-radius: 14px; overflow: hidden; background: rgba(0,0,0,0.3); max-height: 68vh; }
.lb-img { width: 100%; max-height: 68vh; object-fit: contain; display: block; }
.lb-arrow { position: absolute; top: 50%; transform: translateY(-50%); z-index: 10; width: 44px; height: 44px; border: none; border-radius: 50%; background: rgba(255,255,255,0.15); backdrop-filter: blur(4px); color: white; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s, transform 0.2s; }
.lb-arrow:hover { background: rgba(212,163,74,0.75); transform: translateY(-50%) scale(1.08); }
.lb-prev { left: 14px; }
.lb-next { right: 14px; }
.lb-thumbs { display: flex; gap: 8px; overflow-x: auto; padding: 4px 2px; scrollbar-width: thin; scrollbar-color: #d4a34a transparent; }
.lb-thumb { flex-shrink: 0; width: 72px; height: 50px; border-radius: 8px; overflow: hidden; border: 2px solid transparent; cursor: pointer; padding: 0; background: none; opacity: 0.55; transition: opacity 0.2s, border-color 0.2s, transform 0.2s; }
.lb-thumb img { width: 100%; height: 100%; object-fit: cover; }
.lb-thumb.active { border-color: #d4a34a; opacity: 1; transform: scale(1.06); }
.lb-thumb:hover { opacity: 0.85; }
.lb-enter-active, .lb-leave-active { transition: opacity 0.25s ease; }
.lb-enter-from, .lb-leave-to { opacity: 0; }
.img-fade-enter-active, .img-fade-leave-active { transition: opacity 0.18s ease; }
.img-fade-enter-from, .img-fade-leave-to { opacity: 0; }
@media (max-width: 600px) {
  .lb-thumb { width: 56px; height: 40px; }
  .lb-arrow { width: 36px; height: 36px; }
  .zoom-hint { display: none; }
}

</style>
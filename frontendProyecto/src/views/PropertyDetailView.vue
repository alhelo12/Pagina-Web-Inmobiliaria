<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import L from 'leaflet'
import { propertiesApi } from '@/api/properties'
import apiClient from '@/api/axios'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useAuthStore } from '@/stores/authStore'
import { FALLBACK_PROPERTY_IMAGE, normalizeImageUrl } from '@/utils/propertyImages'

const route = useRoute()
const router = useRouter()
const favStore = useFavoritesStore()
const auth = useAuthStore()

const property = ref(null)
const loading = ref(true)
const error = ref('')
const activeImg = ref(0)
const activeGallery = ref('general')
const toggling = ref(false)
const lightboxOpen = ref(false)
const mapEl = ref(null)
const contactStatus = ref('idle')
const contactMessage = ref('')

let autoplayTimer = null
let mapInstance = null
let mapMarker = null

const typeLabel = { house: 'Casa', apartment: 'Departamento', land: 'Terreno', commercial: 'Local' }
const txLabel = { sale: 'En Venta', rent: 'En Renta' }

const normalizeImages = (items = []) =>
  items.map((img) => ({
    ...img,
    image_url: normalizeImageUrl(img.image_url),
    label: img.label?.trim() || ''
  }))

const allImages = computed(() => normalizeImages(property.value?.images ?? []))

const generalImages = computed(() => {
  const selected = allImages.value.filter((img) => (img.image_type ?? 'general') === 'general' || img.is_main)
  return selected.length ? selected : [{ id: 'fallback', image_url: FALLBACK_PROPERTY_IMAGE, image_type: 'general' }]
})

const bedroomImages = computed(() => allImages.value.filter((img) => img.image_type === 'bedroom'))
const bathroomImages = computed(() => allImages.value.filter((img) => img.image_type === 'bathroom'))

const extraGroups = computed(() => {
  const groups = new Map()
  allImages.value.filter((img) => img.is_extra || img.image_type === 'extra').forEach((img) => {
    const label = img.label || 'Extra'
    if (!groups.has(label)) groups.set(label, [])
    groups.get(label).push(img)
  })
  return Array.from(groups, ([label, images]) => ({
    key: `extra:${label}`,
    label,
    images
  }))
})

const galleryTabs = computed(() => {
  const tabs = [
    {
      key: 'general',
      label: 'Fachada',
      count: generalImages.value.length,
      images: generalImages.value,
      value: property.value?.square_meters ? `${property.value.square_meters} m2` : 'Fotos'
    }
  ]

  if (property.value?.bedrooms) {
    tabs.push({
      key: 'bedrooms',
      label: 'Recamaras',
      count: bedroomImages.value.length,
      images: bedroomImages.value,
      value: property.value.bedrooms
    })
  }

  if (property.value?.bathrooms) {
    tabs.push({
      key: 'bathrooms',
      label: 'baños',
      count: bathroomImages.value.length,
      images: bathroomImages.value,
      value: property.value.bathrooms
    })
  }

  extraGroups.value.forEach((group) => {
    tabs.push({
      key: group.key,
      label: group.label,
      count: group.images.length,
      images: group.images,
      value: group.images.length
    })
  })

  return tabs
})

const currentTab = computed(() =>
  galleryTabs.value.find((tab) => tab.key === activeGallery.value) ?? galleryTabs.value[0]
)

const images = computed(() => {
  const selected = currentTab.value?.images ?? []
  return selected.length ? selected : generalImages.value
})

const selectedLabel = computed(() => currentTab.value?.label ?? 'Fachada')
const hasCoords = computed(() => {
  const lat = Number(property.value?.latitude)
  const lng = Number(property.value?.longitude)
  return Number.isFinite(lat) && Number.isFinite(lng)
})

const mapLink = computed(() => {
  if (!hasCoords.value) return ''
  const lat = Number(property.value.latitude)
  const lng = Number(property.value.longitude)
  return `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`
})

const resetAutoplay = () => {
  window.clearInterval(autoplayTimer)
  autoplayTimer = null

  if (generalImages.value.length > 1 && !lightboxOpen.value) {
    autoplayTimer = window.setInterval(() => {
      activeImg.value = (activeImg.value + 1) % generalImages.value.length
    }, 5000)
  }
}

const goTo = (index) => {
  activeImg.value = (index + images.value.length) % images.value.length
  resetAutoplay()
}

const prev = () => goTo(activeImg.value - 1)
const next = () => goTo(activeImg.value + 1)

const heroGoTo = (index) => {
  activeImg.value = (index + generalImages.value.length) % generalImages.value.length
  resetAutoplay()
}
const heroPrev = () => heroGoTo(activeImg.value - 1)
const heroNext = () => heroGoTo(activeImg.value + 1)

const selectGallery = (key) => {
  activeGallery.value = key
  activeImg.value = 0
  resetAutoplay()
}

const openLightbox = (index = activeImg.value) => {
  activeImg.value = index
  lightboxOpen.value = true
  resetAutoplay()
}

const closeLightbox = () => {
  lightboxOpen.value = false
  resetAutoplay()
}

const handleContactAdvisor = async () => {
  if (!auth.isLogged) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }

  if (auth.isEmailVerified === false) {
    router.push('/verificado')
    return
  }

  const advisorId = property.value?.advisor_id
  if (!advisorId) {
    router.push('/contacto')
    return
  }

  contactStatus.value = 'starting'
  contactMessage.value = ''

  try {
    await apiClient.post('/messages/start', {
      advisor_id: advisorId,
      property_id: property.value.id,
      content: `Hola, me interesa la propiedad "${property.value.title}". Me gustaria obtener mas informacion.`
    })
    contactStatus.value = 'success'
    contactMessage.value = 'Conversacion iniciada correctamente'
    setTimeout(() => {
      router.push('/client/mensajes')
    }, 800)
  } catch (err) {
    contactStatus.value = 'error'
    contactMessage.value = err.response?.data?.detail || 'No se pudo iniciar la conversacion'
    setTimeout(() => {
      contactStatus.value = 'idle'
      contactMessage.value = ''
    }, 3000)
  }
}

const onKey = (e) => {
  if (e.key === 'ArrowLeft') prev()
  if (e.key === 'ArrowRight') next()
  if (e.key === 'Escape') closeLightbox()
}

const destroyMap = () => {
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
    mapMarker = null
  }
}

const initMap = async () => {
  await nextTick()
  if (!mapEl.value || !hasCoords.value) return

  destroyMap()
  const lat = Number(property.value.latitude)
  const lng = Number(property.value.longitude)
  mapInstance = L.map(mapEl.value, {
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    boxZoom: false,
    keyboard: false,
    zoomControl: true
  }).setView([lat, lng], 16)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
  }).addTo(mapInstance)

  mapMarker = L.marker([lat, lng]).addTo(mapInstance)
  setTimeout(() => mapInstance?.invalidateSize(), 120)
}

const toggleFav = async () => {
  if (!auth.isLogged || !property.value) return
  toggling.value = true
  try {
    await favStore.toggleFavorite(property.value.id)
  } finally {
    toggling.value = false
  }
}

watch(images, () => {
  activeImg.value = 0
  resetAutoplay()
})

watch(lightboxOpen, resetAutoplay)

onMounted(async () => {
  window.addEventListener('keydown', onKey)
  try {
    const { data } = await propertiesApi.getById(route.params.id)
    property.value = data
    loading.value = false
    await initMap()
    resetAutoplay()
  } catch {
    error.value = 'Propiedad no encontrada'
    loading.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  window.clearInterval(autoplayTimer)
  destroyMap()
})
</script>

<template>
  <div v-if="loading" class="state">
    <div class="spinner"></div>
    <p>Cargando propiedad...</p>
  </div>

  <div v-else-if="error" class="state">
    <p class="error-msg">{{ error }}</p>
    <RouterLink to="/propiedades" class="back-link">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m7 7-7-7 7-7"/></svg>
      Volver a propiedades
    </RouterLink>
  </div>

  <main v-else class="detail-page">
    <section class="hero">
      <div class="hero-media">
        <Transition name="image-fade" mode="out-in">
          <img
            :key="generalImages[activeImg]?.image_url"
            :src="generalImages[activeImg]?.image_url"
            :alt="generalImages[activeImg]?.label || property.title"
            class="hero-img"
            @click="openLightbox()"
          />
        </Transition>

        <div class="hero-shade"></div>

        <div class="hero-actions">
          <span class="counter">{{ activeImg + 1 }} / {{ generalImages.length }}</span>
          <button class="icon-btn" type="button" aria-label="Ver foto en grande" @click="openLightbox()">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
          </button>
        </div>

        <button v-if="generalImages.length > 1" class="nav-btn nav-prev" type="button" aria-label="Foto anterior" @click="heroPrev">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <button v-if="generalImages.length > 1" class="nav-btn nav-next" type="button" aria-label="Foto siguiente" @click="heroNext">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>
        </button>

        <div class="hero-copy">
          <div class="badges">
            <span>{{ typeLabel[property.property_type] ?? property.property_type }}</span>
            <span class="gold">{{ txLabel[property.transaction_type] ?? property.transaction_type }}</span>
          </div>
          <h1>{{ property.title }}</h1>
          <p>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 10c0 5.5-8 11-8 11s-8-5.5-8-11a8 8 0 1 1 16 0Z"/><path d="M12 10.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z"/></svg>
            {{ property.address }}, {{ property.city }}
          </p>
        </div>
      </div>

      <div class="thumb-strip" aria-label="Fotos generales">
        <button
          v-for="(img, index) in generalImages"
          :key="img.id ?? index"
          :class="['thumb', { active: activeGallery === 'general' && activeImg === index }]"
          type="button"
          @click="selectGallery('general'); goTo(index)"
        >
          <img :src="img.image_url" :alt="`Foto general ${index + 1}`" />
        </button>
      </div>
    </section>

    <section class="content">
      <div class="main-col">
        <div class="summary-card">
          <div>
            <span class="eyebrow">Precio</span>
            <strong class="price">${{ Number(property.price).toLocaleString('es-MX') }} <small>MXN</small></strong>
          </div>
          <button
            v-if="auth.isLogged && auth.role === 'client'"
            :class="['favorite-btn', { active: favStore.isFavorite(property.id) }]"
            type="button"
            :disabled="toggling"
            @click="toggleFav"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true" :fill="favStore.isFavorite(property.id) ? 'currentColor' : 'none'"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 1 0-7.8 7.8L12 21.2l8.8-8.8a5.5 5.5 0 0 0 0-7.8Z"/></svg>
            {{ favStore.isFavorite(property.id) ? 'Guardado' : 'Guardar' }}
          </button>
        </div>

        <div class="feature-grid">
          <button
            v-for="tab in galleryTabs"
            :key="tab.key"
            :class="['feature-card', { active: activeGallery === tab.key }]"
            type="button"
            @click="selectGallery(tab.key)"
          >
            <span class="feature-icon">
              <svg v-if="tab.key === 'general'" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 21v-7h6v7"/></svg>
              <svg v-else-if="tab.key === 'bedrooms'" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 11V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v6M4 21v-8h16v8M2 13h20M7 11V8h4v3M13 11V8h4v3"/></svg>
              <svg v-else-if="tab.key === 'bathrooms'" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 12V5a3 3 0 0 1 6 0M5 12h16v2a6 6 0 0 1-6 6H9a6 6 0 0 1-6-6v-2h2ZM8 20v2M16 20v2"/></svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.4 5 5.6.8-4 3.9.9 5.5-4.9-2.6-4.9 2.6.9-5.5-4-3.9 5.6-.8L12 3Z"/></svg>
            </span>
            <span class="feature-value">{{ tab.value }}</span>
            <span class="feature-label">{{ tab.label }}</span>
            <small>{{ tab.count ? `${tab.count} foto(s)` : 'Sin fotos' }}</small>
          </button>
        </div>

        <div v-if="activeGallery !== 'general'" class="section-card gallery-card">
          <div class="section-head">
            <div>
              <span class="eyebrow">Galeria</span>
              <h2>{{ selectedLabel }}</h2>
            </div>
          </div>
          <div v-if="currentTab?.count" class="section-gallery">
            <button v-for="(img, index) in images" :key="img.id ?? index" type="button" @click="openLightbox(index)">
              <img :src="img.image_url" :alt="img.label || selectedLabel" />
            </button>
          </div>
          <p v-else class="empty-note">No hay fotos registradas para este apartado.</p>
        </div>

        <div class="section-card">
          <div class="section-head">
            <div>
              <span class="eyebrow">Detalle</span>
              <h2>Descripcion</h2>
            </div>
          </div>
          <p class="description">{{ property.description }}</p>
        </div>

        <div class="section-card">
          <div class="section-head">
            <div>
              <span class="eyebrow">Mapa</span>
              <h2>Ubicacion</h2>
            </div>
            <a v-if="mapLink" :href="mapLink" target="_blank" rel="noreferrer" class="map-link">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14 21 3"/></svg>
              Abrir mapa
            </a>
          </div>
          <div class="address-card">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 10c0 5.5-8 11-8 11s-8-5.5-8-11a8 8 0 1 1 16 0Z"/><path d="M12 10.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z"/></svg>
            <span>{{ property.address }}, {{ property.city }}</span>
          </div>
          <div v-if="hasCoords" ref="mapEl" class="map-box"></div>
          <p v-else class="empty-note">Esta propiedad no tiene coordenadas registradas.</p>
        </div>
      </div>

      <aside class="side-col">
        <div class="contact-card">
          <span class="eyebrow">Atencion</span>
          <h2>Te interesa esta propiedad?</h2>
          <p>Un asesor puede ayudarte a revisar disponibilidad, agenda y detalles de la visita.</p>
          <button
            v-if="contactStatus === 'idle'"
            class="primary-link contact-btn-action"
            @click="handleContactAdvisor"
            :aria-label="property?.advisor_id ? 'Iniciar chat con el asesor' : 'Ir a pagina de contacto'"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.9.7 2.8a2 2 0 0 1-.5 2.1l-1.2 1.2a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.8 2.1Z"/></svg>
            <span>{{ property?.advisor_id ? 'Contactar asesor' : 'Contactar' }}</span>
          </button>
          <button v-else-if="contactStatus === 'starting'" class="primary-link contact-btn-action" disabled aria-label="Iniciando conversacion">
            <svg class="spin-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" stroke-dasharray="31.4 31.4"/></svg>
            <span>Iniciando conversacion...</span>
          </button>
          <button v-else-if="contactStatus === 'success'" class="primary-link contact-btn-action success" disabled aria-label="Conversacion iniciada">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span>Redirigiendo al chat...</span>
          </button>
          <button v-else-if="contactStatus === 'error'" class="primary-link contact-btn-action error" @click="contactStatus = 'idle'; contactMessage = ''" aria-label="Reintentar">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 9v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>
            <span>{{ contactMessage || 'Error. Reintentar' }}</span>
          </button>
          <RouterLink to="/propiedades" class="secondary-link">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m7 7-7-7 7-7"/></svg>
            Ver mas propiedades
          </RouterLink>
        </div>
      </aside>
    </section>

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="lightboxOpen" class="lightbox" @click.self="closeLightbox">
          <div class="lightbox-panel">
            <header class="lightbox-head">
              <span>{{ activeImg + 1 }} / {{ images.length }}</span>
              <strong>{{ images[activeImg]?.label || selectedLabel }}</strong>
              <button type="button" class="icon-btn" aria-label="Cerrar" @click="closeLightbox">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>
              </button>
            </header>
            <div class="lightbox-image">
              <button v-if="images.length > 1" class="nav-btn nav-prev" type="button" aria-label="Anterior" @click.stop="prev">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>
              </button>
              <img :src="images[activeImg]?.image_url" :alt="images[activeImg]?.label || selectedLabel" />
              <button v-if="images.length > 1" class="nav-btn nav-next" type="button" aria-label="Siguiente" @click.stop="next">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </main>
</template>

<style scoped>
* { box-sizing: border-box; }

.detail-page {
  --line: rgba(7, 23, 45, .1);
  min-height: 100vh;
  background: var(--color-cream);
  color: var(--color-navy);
  font-family: 'Poppins', sans-serif;
}

.state {
  min-height: 70vh;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 14px;
  padding: 80px 20px;
  color: var(--color-muted);
  font-family: 'Poppins', sans-serif;
}

.spinner {
  width: 42px;
  height: 42px;
  border: 3px solid rgba(7, 23, 45, .12);
  border-top-color: var(--color-gold);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.error-msg { color: #991b1b; margin: 0; }

svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.hero { background: var(--color-navy); }

.hero-media {
  position: relative;
  height: min(68vh, 620px);
  min-height: 420px;
  overflow: hidden;
  background: var(--color-navy);
}

.hero-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: zoom-in;
}

.hero-shade {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(7, 23, 45, .78), rgba(7, 23, 45, .18) 55%, rgba(7, 23, 45, .38)),
    linear-gradient(0deg, rgba(7, 23, 45, .78), transparent 58%);
  pointer-events: none;
}

.hero-copy {
  position: absolute;
  left: max(22px, calc((100vw - var(--container-max)) / 2));
  right: max(22px, calc((100vw - var(--container-max)) / 2));
  bottom: 42px;
  max-width: 780px;
  color: white;
}

.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.badges span {
  min-height: 28px;
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, .16);
  border: 1px solid rgba(255, 255, 255, .24);
  color: white;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
  backdrop-filter: blur(6px);
}

.badges .gold {
  background: var(--color-gold);
  border-color: var(--color-gold);
  color: var(--color-navy);
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(28px, 4vw, 52px);
  line-height: 1.08;
  max-width: 14ch;
}

.hero-copy p,
.address-card {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.hero-copy p {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, .86);
  font-size: 15px;
}

.hero-actions {
  position: absolute;
  top: 22px;
  right: max(18px, calc((100vw - var(--container-max)) / 2));
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 3;
}

.counter,
.icon-btn,
.nav-btn {
  background: rgba(255, 255, 255, .14);
  color: white;
  border: 1px solid rgba(255, 255, 255, .24);
  backdrop-filter: blur(8px);
}

.counter {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  padding: 0 13px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.icon-btn,
.nav-btn {
  display: grid;
  place-items: center;
  border-radius: 999px;
  transition: .2s ease;
}

.icon-btn {
  width: 38px;
  height: 38px;
}

.nav-btn {
  position: absolute;
  top: 50%;
  width: 44px;
  height: 44px;
  transform: translateY(-50%);
  z-index: 3;
}

.nav-btn:hover,
.icon-btn:hover {
  background: rgba(214, 168, 72, .82);
  color: var(--color-navy);
}

.nav-prev { left: 24px; }
.nav-next { right: 24px; }

.thumb-strip {
  width: min(100% - 32px, var(--container-max));
  min-height: 96px;
  margin: 0 auto;
  display: flex;
  gap: 8px;
  padding: 12px 0;
  overflow-x: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--color-gold) transparent;
}

.thumb {
  flex: 0 0 118px;
  height: 72px;
  padding: 0;
  border: 2px solid transparent;
  border-radius: 8px;
  overflow: hidden;
  background: transparent;
  opacity: .68;
  transition: .2s ease;
}

.thumb img,
.section-gallery img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb.active,
.thumb:hover {
  opacity: 1;
  border-color: var(--color-gold);
}

.content {
  width: min(100% - 32px, var(--container-max));
  margin: 0 auto;
  padding: 34px 0 64px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 24px;
  align-items: start;
}

.main-col,
.side-col {
  display: grid;
  gap: 18px;
}

.summary-card,
.section-card,
.contact-card {
  background: var(--color-card);
  border: 1px solid var(--line);
  border-radius: 10px;
  box-shadow: 0 10px 26px rgba(7, 23, 45, .08);
}

.summary-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
}

.eyebrow {
  display: block;
  color: var(--color-gold);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .12em;
  text-transform: uppercase;
}

.price {
  display: block;
  margin-top: 2px;
  color: var(--color-navy);
  font-size: clamp(28px, 3vw, 38px);
  line-height: 1;
}

.price small {
  color: var(--color-muted);
  font-size: 15px;
  font-weight: 600;
}

.favorite-btn,
.primary-link,
.secondary-link,
.map-link,
.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  border-radius: 8px;
  font-weight: 700;
  text-decoration: none;
}

.favorite-btn {
  padding: 0 16px;
  background: #fff;
  color: var(--color-muted);
  border: 1px solid var(--line);
}

.favorite-btn.active {
  color: #b91c1c;
  border-color: rgba(185, 28, 28, .28);
  background: #fff5f5;
}

.favorite-btn:disabled { opacity: .6; cursor: not-allowed; }

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.feature-card {
  min-height: 132px;
  padding: 16px;
  text-align: left;
  background: var(--color-card);
  border: 1px solid var(--line);
  border-radius: 10px;
  color: var(--color-navy);
  box-shadow: 0 10px 24px rgba(7, 23, 45, .06);
  transition: .2s ease;
}

.feature-card:hover,
.feature-card.active {
  border-color: var(--color-gold);
  background: #fffaf0;
  transform: translateY(-1px);
}

.feature-icon {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  background: #e8edf0;
  color: var(--color-navy-2);
  margin-bottom: 12px;
}

.feature-card.active .feature-icon {
  background: var(--color-gold);
}

.feature-value {
  display: block;
  color: var(--color-navy);
  font-size: 26px;
  font-weight: 800;
  line-height: 1;
}

.feature-label {
  display: block;
  margin-top: 5px;
  color: var(--color-navy);
  font-size: 13px;
  font-weight: 700;
  overflow-wrap: anywhere;
}

.feature-card small {
  display: block;
  margin-top: 5px;
  color: var(--color-muted);
  font-size: 11px;
  font-weight: 600;
}

.section-card,
.contact-card {
  padding: 20px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.section-head h2,
.contact-card h2 {
  margin: 3px 0 0;
  color: var(--color-navy);
  font-size: 22px;
  line-height: 1.2;
}

.description {
  margin: 0;
  color: #3d4b5d;
  font-size: 15px;
  line-height: 1.9;
  text-align: justify;
}

.section-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.section-gallery button {
  aspect-ratio: 4 / 3;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.address-card {
  padding: 13px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  color: #344257;
  font-size: 14px;
}

.address-card svg,
.map-link svg {
  color: var(--color-gold);
  flex: 0 0 auto;
}

.map-box {
  height: 280px;
  margin-top: 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
  background: #e8edf0;
  z-index: 1;
}

.map-link {
  min-height: 36px;
  padding: 0 12px;
  border: 1px solid var(--line);
  background: #fff;
  color: var(--color-navy);
  font-size: 13px;
}

.empty-note {
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
}

.contact-card {
  position: sticky;
  top: 24px;
}

.contact-card p {
  margin: 12px 0 20px;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.7;
}

.primary-link,
.secondary-link,
.back-link {
  width: 100%;
  padding: 0 14px;
}

.primary-link {
  background: var(--color-gold);
  color: var(--color-navy);
}

.contact-btn-action {
  cursor: pointer;
  border: none;
  font-family: inherit;
  font-size: inherit;
  transition: background 0.2s, opacity 0.2s;
}
.contact-btn-action:hover:not(:disabled) {
  background: #e0b03a;
}
.contact-btn-action:disabled {
  cursor: default;
}
.contact-btn-action.success {
  background: #22c55e;
  color: #fff;
}
.contact-btn-action.error {
  background: #dc2626;
  color: #fff;
}
.spin-icon {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.secondary-link,
.back-link {
  margin-top: 10px;
  border: 1px solid var(--line);
  background: #fff;
  color: var(--color-navy);
}

.back-link {
  width: auto;
  margin-top: 0;
}

.lightbox {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(7, 23, 45, .94);
  backdrop-filter: blur(8px);
}

.lightbox-panel {
  width: min(100%, 1040px);
  max-height: 92vh;
  display: grid;
  gap: 12px;
  color: white;
  font-family: 'Poppins', sans-serif;
}

.lightbox-head {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
}

.lightbox-head span,
.lightbox-head strong {
  font-size: 14px;
}

.lightbox-head strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lightbox-image {
  position: relative;
  display: grid;
  place-items: center;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(0, 0, 0, .26);
}

.lightbox-image img {
  max-height: 76vh;
  width: 100%;
  object-fit: contain;
}

.image-fade-enter-active,
.image-fade-leave-active {
  transition: opacity .55s ease;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity .22s ease;
}

.image-fade-enter-from,
.image-fade-leave-to,
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@media (max-width: 920px) {
  .content {
    grid-template-columns: 1fr;
  }

  .contact-card {
    position: static;
  }

  .hero-media {
    height: 460px;
    min-height: 360px;
  }
}

@media (max-width: 560px) {
  .hero-media {
    height: 380px;
    min-height: 340px;
  }

  .hero-copy {
    bottom: 24px;
  }

  .hero-copy h1 {
    max-width: none;
    font-size: 26px;
  }

  .nav-prev { left: 10px; }
  .nav-next { right: 10px; }
  .hero-actions { top: 14px; right: 14px; }
  .summary-card { align-items: stretch; flex-direction: column; }
  .favorite-btn { width: 100%; }
  .thumb { flex-basis: 92px; height: 60px; }
  .section-head { align-items: flex-start; flex-direction: column; }
  .map-link { width: 100%; }
}
</style>

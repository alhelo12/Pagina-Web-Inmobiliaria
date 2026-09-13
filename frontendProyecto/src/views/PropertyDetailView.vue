<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import L from 'leaflet'
import { propertiesApi } from '@/api/properties'
import apiClient from '@/api/axios'
import { appointmentsApi } from '@/api/appointments'
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
const lightboxPanel = ref(null)
let lastFocusedEl = null
const autoplayPaused = ref(false)
const mapEl = ref(null)
const contactStatus = ref('idle')
const contactMessage = ref('')
let contactRedirectTimer = null
let contactResetTimer = null
const bookingDate = ref('')
const bookingTime = ref('')
const bookingStatus = ref('idle')
const bookingMessage = ref('')
const bookingConfirmed = ref('')
const bookingId = ref(null)
const cancelStatus = ref('idle')
const cancelMessage = ref('')
const BOOKING_HOURS = ['09:00', '10:00', '11:00', '12:00', '13:00', '15:00', '16:00', '17:00', '18:00']
const advisorName = computed(() => property.value?.advisor?.user?.full_name?.trim() || '')
const advisorAgency = computed(() => property.value?.advisor?.agency_name?.trim() || '')
const advisorDisplay = computed(() => {
  const name = advisorName.value || 'Tu asesor JAKEDA'
  return advisorAgency.value ? `${name} · ${advisorAgency.value}` : name
})
const isPastHour = (hour) => {
  if (bookingDate.value !== todayMin) return false
  const now = new Date()
  const [hh, mm] = hour.split(':').map(Number)
  return hh * 60 + mm <= now.getHours() * 60 + now.getMinutes()
}
const todayMin = new Date().toISOString().slice(0, 10)
const reducedMotion = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false

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
      value: generalImages.value.length
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

  if (reducedMotion() || autoplayPaused.value) return
  if (generalImages.value.length > 1 && !lightboxOpen.value) {
    autoplayTimer = window.setInterval(() => {
      activeImg.value = (activeImg.value + 1) % generalImages.value.length
    }, 5000)
  }
}

const toggleAutoplay = () => {
  autoplayPaused.value = !autoplayPaused.value
  resetAutoplay()
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
  lastFocusedEl = document.activeElement
  activeImg.value = index
  lightboxOpen.value = true
  resetAutoplay()
  nextTick(() => {
    lightboxPanel.value?.querySelector('button')?.focus()
  })
}

const closeLightbox = () => {
  lightboxOpen.value = false
  resetAutoplay()
  nextTick(() => {
    lastFocusedEl?.focus?.()
  })
}

const trapLightbox = (e) => {
  if (!lightboxOpen.value || e.key !== 'Tab' || !lightboxPanel.value) return
  const focusables = lightboxPanel.value.querySelectorAll('button, a[href], [tabindex]:not([tabindex="-1"])')
  if (!focusables.length) return
  const first = focusables[0]
  const last = focusables[focusables.length - 1]
  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault()
    last.focus()
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault()
    first.focus()
  }
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
    clearTimeout(contactRedirectTimer)
    contactRedirectTimer = setTimeout(() => {
      router.push(auth.role === 'advisor' ? '/advisor/mensajes' : '/cliente/mensajes')
    }, 800)
  } catch (err) {
    contactStatus.value = 'error'
    contactMessage.value = err.response?.data?.detail || 'No se pudo iniciar la conversacion'
    clearTimeout(contactResetTimer)
    contactResetTimer = setTimeout(() => {
      contactStatus.value = 'idle'
      contactMessage.value = ''
    }, 3000)
  }
}

const bookingSubmit = async () => {
  if (bookingStatus.value === 'sending') return
  bookingMessage.value = ''
  bookingConfirmed.value = ''
  if (!auth.isLogged) {
    bookingStatus.value = 'error'
    bookingMessage.value = 'Inicia sesión para agendar una visita'
    return
  }
  if (!bookingDate.value) {
    bookingStatus.value = 'error'
    bookingMessage.value = 'Selecciona una fecha para la visita'
    return
  }
  const advisorId = property.value?.advisor_id
  if (!advisorId) {
    bookingStatus.value = 'error'
    bookingMessage.value = 'Esta propiedad no tiene asesor asignado'
    return
  }
  bookingStatus.value = 'sending'
  cancelStatus.value = 'idle'
  cancelMessage.value = ''
  bookingId.value = null
  try {
    const { data } = await appointmentsApi.create({
      client_id: auth.userId,
      property_id: property.value.id,
      advisor_id: advisorId,
      scheduled_date: `${bookingDate.value}T${bookingTime.value || '10:00'}:00`,
      appointment_type: 'viewing'
    })
    bookingId.value = data?.id ?? data?.appointment?.id ?? null
    bookingStatus.value = 'success'
    const [y, m, d] = bookingDate.value.split('-').map(Number)
    const datePart = new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium' }).format(new Date(y, m - 1, d))
    bookingConfirmed.value = bookingTime.value
      ? `${datePart} a las ${bookingTime.value}`
      : datePart
  } catch (err) {
    bookingStatus.value = 'error'
    bookingMessage.value = err.response?.data?.detail || 'No se pudo agendar la visita'
  }
}

const cancelBooking = async () => {
  if (!bookingId.value || cancelStatus.value === 'sending') return
  cancelStatus.value = 'sending'
  cancelMessage.value = ''
  try {
    await appointmentsApi.delete(bookingId.value)
    cancelStatus.value = 'success'
    bookingStatus.value = 'idle'
    bookingConfirmed.value = ''
    bookingId.value = null
  } catch (err) {
    cancelStatus.value = 'error'
    cancelMessage.value = err.response?.data?.detail || 'No se pudo cancelar la visita'
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
    keyboard: true,
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

watch(bookingDate, () => {
  if (bookingTime.value && isPastHour(bookingTime.value)) bookingTime.value = ''
})

watch(lightboxOpen, resetAutoplay)

onMounted(async () => {
  window.addEventListener('keydown', onKey)
  window.addEventListener('keydown', trapLightbox)
  autoplayPaused.value = reducedMotion()
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
  window.removeEventListener('keydown', trapLightbox)
  window.clearInterval(autoplayTimer)
  clearTimeout(contactRedirectTimer)
  clearTimeout(contactResetTimer)
  destroyMap()
})
</script>

<template>
  <div v-if="loading" class="state">
    <div class="spinner"></div>
    <p>Cargando propiedad...</p>
  </div>

  <div v-else-if="error" class="state">
    <p class="error-msg" role="alert">{{ error }}</p>
    <RouterLink to="/propiedades" class="back-link">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m7 7-7-7 7-7"/></svg>
      Volver a propiedades
    </RouterLink>
  </div>

  <div v-else class="detail-page">
    <section class="hero">
      <div class="hero-media">
        <Transition name="image-fade" mode="out-in">
          <img decoding="async"
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
          <button
            v-if="generalImages.length > 1"
            class="icon-btn"
            type="button"
            :aria-pressed="String(!autoplayPaused)"
            :aria-label="autoplayPaused ? 'Reanudar presentación' : 'Pausar presentación'"
            @click="toggleAutoplay"
          >
            <svg v-if="autoplayPaused" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>
            <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>
          </button>
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
          <h1 class="serif-display">{{ property.title }}</h1>
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
          :aria-selected="activeGallery === 'general' && activeImg === index"
          @click="selectGallery('general'); goTo(index)"
        >
          <img decoding="async" :src="img.image_url" :alt="`Foto general ${index + 1}`" loading="lazy" />
        </button>
      </div>
    </section>

    <section class="content">
      <div class="main-col">
        <div class="summary-card">
          <div>
            <span class="eyebrow-label">Precio</span>
            <strong class="price serif-display">${{ Number(property.price).toLocaleString('es-MX') }} <small>MXN</small></strong>
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
            :aria-selected="activeGallery === tab.key"
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
              <span class="eyebrow-label">Galería</span>
              <h2 class="serif-display">{{ selectedLabel }}</h2>
            </div>
          </div>
          <div v-if="currentTab?.count" class="section-gallery">
            <button v-for="(img, index) in images" :key="img.id ?? index" type="button" @click="openLightbox(index)">
              <img decoding="async" :src="img.image_url" :alt="img.label || selectedLabel" />
            </button>
          </div>
          <p v-else class="empty-note">No hay fotos registradas para este apartado.</p>
        </div>

        <div class="section-card">
          <div class="section-head">
            <div>
              <span class="eyebrow-label">Detalle</span>
              <h2 class="serif-display">Descripción</h2>
            </div>
          </div>
          <p class="description">{{ property.description }}</p>
        </div>

        <div class="section-card">
          <div class="section-head">
            <div>
              <span class="eyebrow-label">Mapa</span>
              <h2 class="serif-display">Ubicación</h2>
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
          <div v-if="hasCoords" ref="mapEl" class="map-box" tabindex="0" aria-label="Mapa de ubicación de la propiedad"></div>
          <p v-if="hasCoords" class="map-alt">Dirección: {{ property.address }}, {{ property.city }}</p>
          <p v-else class="empty-note">Esta propiedad no tiene coordenadas registradas.</p>
        </div>
      </div>

      <aside class="side-col">
        <div class="contact-card">
          <span class="eyebrow-label">Atención personalizada</span>
          <h2 class="serif-display">¿Te interesa esta propiedad?</h2>
          <div class="card-rule" aria-hidden="true"></div>
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
          <div class="booking-block">
            <h3>Agendar visita</h3>
            <p class="booking-advisor">Te atiende {{ advisorDisplay }}</p>
            <form @submit.prevent="bookingSubmit" class="booking-form">
              <label for="booking-date">Fecha</label>
              <input id="booking-date" v-model="bookingDate" type="date" :min="todayMin" />
              <label for="booking-time">Hora (opcional)</label>
              <select id="booking-time" v-model="bookingTime">
                <option value="">Selecciona hora</option>
                <option v-for="hour in BOOKING_HOURS" :key="hour" :value="hour" :disabled="isPastHour(hour)">{{ hour }}</option>
              </select>
              <button class="secondary-link booking-btn" type="submit" :disabled="bookingStatus === 'sending'">
                {{ bookingStatus === 'sending' ? 'Agendando...' : 'Agendar visita' }}
              </button>
              <p class="booking-sla">El asesor confirma tu visita. Te avisamos por notificación.</p>
            </form>
            <p v-if="bookingStatus === 'success'" class="booking-success" role="status">
              Visita agendada para el {{ bookingConfirmed }}.
              <RouterLink to="/cliente/citas">Ver mis citas</RouterLink>
            </p>
            <p v-if="bookingStatus === 'error'" class="booking-error" role="alert">{{ bookingMessage }}</p>
            <button
              v-if="bookingStatus === 'success' && bookingId"
              class="secondary-link booking-cancel-btn"
              type="button"
              :disabled="cancelStatus === 'sending'"
              @click="cancelBooking"
            >
              {{ cancelStatus === 'sending' ? 'Cancelando...' : 'Cancelar visita' }}
            </button>
            <p v-if="cancelStatus === 'success'" class="booking-cancelled" role="status">Visita cancelada.</p>
            <p v-if="cancelStatus === 'error'" class="booking-error" role="alert">{{ cancelMessage }}</p>
          </div>
          <RouterLink to="/propiedades" class="secondary-link">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m7 7-7-7 7-7"/></svg>
            Ver más propiedades
          </RouterLink>
        </div>
      </aside>
    </section>

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="lightboxOpen" class="lightbox" role="dialog" aria-modal="true" aria-label="Vista ampliada de fotos" @click.self="closeLightbox">
          <div ref="lightboxPanel" class="lightbox-panel">
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
              <img decoding="async" :src="images[activeImg]?.image_url" :alt="images[activeImg]?.label || selectedLabel" />
              <button v-if="images.length > 1" class="nav-btn nav-next" type="button" aria-label="Siguiente" @click.stop="next">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>
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
  min-height: 100vh;
  background: var(--color-ivory);
  color: var(--color-ink);
  font-family: var(--sans);
}

.state {
  min-height: 70vh;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 14px;
  padding: 80px 20px;
  color: var(--color-muted);
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

.error-msg { color: var(--color-danger); margin: 0; }

svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.hero { background: var(--color-ink); }

.hero-media {
  position: relative;
  height: min(72vh, 640px);
  min-height: 440px;
  overflow: hidden;
  background: var(--color-ink);
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
    linear-gradient(90deg, rgba(7,27,28,.82), rgba(7,27,28,.2) 55%, rgba(7,27,28,.4)),
    linear-gradient(0deg, rgba(7,27,28,.88), transparent 60%);
  pointer-events: none;
}

.hero-copy {
  position: absolute;
  left: max(22px, calc((100vw - var(--container-max)) / 2));
  right: max(22px, calc((100vw - var(--container-max)) / 2));
  bottom: 44px;
  max-width: 800px;
  color: #fff;
}

.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.badges span {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 28px;
  padding: 6px 12px 6px 10px;
  background: rgba(7, 27, 28, 0.55);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  border: 0;
  border-radius: 999px;
  color: var(--color-ivory);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .18em;
  text-transform: uppercase;
}

.badges span::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-brass);
  flex: 0 0 auto;
}

.badges .gold::before {
  background: var(--color-ivory);
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(38px, 4.6vw, 64px);
  line-height: 1.02;
  max-width: 16ch;
  color: #fff;
}

.hero-copy p,
.address-card {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.hero-copy p {
  margin: 14px 0 0;
  color: rgba(255, 255, 255, .85);
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
  background: rgba(255, 255, 255, .12);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, .26);
  backdrop-filter: blur(8px);
}

.counter {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  padding: 0 13px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: .1em;
}

.icon-btn,
.nav-btn {
  display: grid;
  place-items: center;
  border-radius: 999px;
  transition: background .2s ease, color .2s ease;
}

.icon-btn { width: 44px; height: 44px; min-width: 44px; min-height: 44px; }

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
  background: var(--color-brass);
  border-color: var(--color-brass);
  color: #fff;
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
  scrollbar-color: var(--color-brass) transparent;
}

.thumb {
  flex: 0 0 118px;
  height: 72px;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, .22);
  overflow: hidden;
  background: transparent;
  opacity: .62;
  transition: opacity .2s ease, border-color .2s ease;
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
  border-color: var(--color-brass);
}

.content {
  width: min(100% - 32px, var(--container-max));
  margin: 0 auto;
  padding: 36px 0 72px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 28px;
  align-items: start;
}

.main-col,
.side-col {
  display: grid;
  gap: 20px;
  min-width: 0;
}

.summary-card,
.section-card,
.contact-card {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 2px;
  box-shadow: var(--shadow-soft);
}

.summary-card,
.section-card {
  border-radius: 12px;
}

.summary-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px;
  border-top: 2px solid var(--color-brass);
}

.price {
  display: block;
  margin-top: 4px;
  color: var(--color-petrol);
  font-size: clamp(34px, 3.4vw, 46px);
  line-height: 1;
  font-weight: 500;
}

.price small {
  color: var(--color-muted);
  font-family: var(--sans);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: .18em;
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
  min-height: 44px;
  font-weight: 600;
  text-decoration: none;
  border-radius: 0;
}

.favorite-btn {
  padding: 0 18px;
  background: transparent;
  color: var(--color-petrol);
  border: 1px solid var(--color-line);
  font-size: 12px;
  letter-spacing: .14em;
  text-transform: uppercase;
}

.favorite-btn.active {
  color: var(--color-danger);
  border-color: rgba(185, 28, 28, .3);
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
  padding: 18px;
  text-align: left;
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
  color: var(--color-ink);
  transition: border-color .2s ease, transform .2s ease;
}

.feature-card:hover,
.feature-card.active {
  border-color: var(--color-brass-deep);
  transform: translateY(-1px);
}

.feature-icon {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  background: rgba(16, 45, 45, .07);
  color: var(--color-petrol);
  margin-bottom: 12px;
}

.feature-card.active .feature-icon {
  background: var(--color-petrol);
  color: #fff;
}

.feature-value {
  display: block;
  color: var(--color-petrol);
  font-family: var(--serif);
  font-size: 28px;
  font-weight: 500;
  line-height: 1;
}

.feature-label {
  display: block;
  margin-top: 5px;
  color: var(--color-ink);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: .12em;
  text-transform: uppercase;
  overflow-wrap: anywhere;
}

.feature-card small {
  display: block;
  margin-top: 5px;
  color: var(--color-muted);
  font-size: 11px;
}

.section-card,
.contact-card { padding: 26px; }

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 18px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-line);
}

.section-head h2,
.contact-card h2 {
  margin: 6px 0 0;
  color: var(--color-petrol);
  font-size: 32px;
  line-height: 1.1;
  font-weight: 500;
}

.description {
  margin: 0;
  color: var(--color-muted);
  font-size: 16px;
  line-height: 1.9;
}

.section-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.section-gallery button {
  aspect-ratio: 4 / 3;
  padding: 0;
  border: 1px solid var(--color-line);
  overflow: hidden;
  background: #fff;
}

.address-card {
  padding: 13px 14px;
  border: 1px solid var(--color-line);
  background: var(--color-ivory);
  color: var(--color-charcoal);
  font-size: 14px;
}

.address-card svg,
.map-link svg { color: var(--color-brass-deep); flex: 0 0 auto; }

.map-box {
  height: 280px;
  margin-top: 12px;
  border: 1px solid var(--color-line);
  overflow: hidden;
  background: var(--color-line);
  z-index: 1;
}

.map-link {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 14px;
  border: 1px solid var(--color-line);
  background: transparent;
  color: var(--color-petrol);
  font-size: 12px;
  letter-spacing: .12em;
  text-transform: uppercase;
  white-space: nowrap;
}

.empty-note { margin: 0; color: var(--color-muted); font-size: 14px; }

.contact-card {
  position: sticky;
  top: 24px;
  border-top: 2px solid var(--color-brass);
}

.card-rule {
  margin-top: 16px;
  border-top: 1px solid var(--color-line);
  position: relative;
}

.card-rule::after {
  content: "";
  position: absolute;
  top: -1px;
  left: 0;
  width: 56px;
  height: 2px;
  background: var(--color-brass);
}

.contact-card p {
  margin: 16px 0 22px;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.7;
}

.primary-link,
.secondary-link,
.back-link { width: 100%; padding: 0 14px; }

.primary-link {
  background: var(--color-petrol);
  border: 1px solid var(--color-petrol);
  color: #fff;
  font-size: 12px;
  letter-spacing: .16em;
  text-transform: uppercase;
}

.contact-btn-action {
  cursor: pointer;
  font-family: inherit;
  font-size: 12px;
  transition: background .2s ease;
}

.contact-btn-action:hover:not(:disabled) { background: var(--color-ink); }
.contact-btn-action:disabled { cursor: default; }
.contact-btn-action.success { background: var(--color-success); border-color: var(--color-success); color: #fff; }
.contact-btn-action.error { background: var(--color-danger); border-color: var(--color-danger); color: #fff; }
.spin-icon { animation: spin 1s linear infinite; }

.secondary-link,
.back-link {
  margin-top: 10px;
  border: 1px solid var(--color-line);
  background: transparent;
  color: var(--color-petrol);
  font-size: 12px;
  letter-spacing: .14em;
  text-transform: uppercase;
}

.back-link { width: auto; margin-top: 0; }

.map-alt { margin: 8px 0 0; color: var(--color-muted); font-size: 13px; }

.booking-block { margin-top: 20px; padding-top: 18px; border-top: 1px solid var(--color-line); }
.booking-block h3 { margin: 0 0 10px; color: var(--color-petrol); font-size: 18px; font-weight: 600; }
.booking-form { display: grid; gap: 8px; }
.booking-form label { font-size: 11px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--color-petrol); }
.booking-form input, .booking-form select { min-height: 44px; padding: 0 12px; border: 1px solid var(--color-line); background: #fff; color: var(--color-ink); font-size: 14px; }
.booking-btn { margin-top: 6px; cursor: pointer; font-family: inherit; }
.booking-advisor { margin: 0 0 10px; color: var(--color-petrol); font-size: 13px; font-weight: 600; }
.booking-sla { margin: 8px 0 0; color: var(--color-muted); font-size: 12px; line-height: 1.6; }
.booking-cancel-btn { margin-top: 8px; cursor: pointer; font-family: inherit; }
.booking-cancel-btn:disabled { opacity: .6; cursor: not-allowed; }
.booking-cancelled { margin: 10px 0 0; color: var(--color-muted); font-size: 14px; }
.booking-success { margin: 10px 0 0; color: var(--color-success); font-size: 14px; }
.booking-error { margin: 10px 0 0; color: var(--color-danger); font-size: 14px; }

.lightbox {
  position: fixed;
  inset: 0;
  z-index: var(--z-toast);
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(7, 27, 28, .94);
  backdrop-filter: blur(8px);
}

.lightbox-panel {
  width: min(100%, 1040px);
  max-height: 92vh;
  display: grid;
  gap: 12px;
  color: #fff;
}

.lightbox-head {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
}

.lightbox-head span,
.lightbox-head strong { font-size: 14px; }

.lightbox-head strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--serif);
  font-weight: 500;
  font-size: 18px;
}

.lightbox-image {
  position: relative;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: rgba(0, 0, 0, .26);
}

.lightbox-image img {
  max-height: 76vh;
  width: 100%;
  object-fit: contain;
}

.image-fade-enter-active,
.image-fade-leave-active { transition: opacity .55s ease; }

.modal-enter-active,
.modal-leave-active { transition: opacity .22s ease; }

.image-fade-enter-from,
.image-fade-leave-to,
.modal-enter-from,
.modal-leave-to { opacity: 0; }

@media (max-width: 920px) {
  .content { grid-template-columns: 1fr; }
  .contact-card { position: static; }
  .hero-media { height: 480px; min-height: 380px; }
}

@media (max-width: 560px) {
  .hero-media { height: 400px; min-height: 340px; }
  .hero-copy { bottom: 24px; }
  .hero-copy h1 { font-size: 34px; }
  .nav-prev { left: 10px; }
  .nav-next { right: 10px; }
  .hero-actions { top: 14px; right: 14px; }
  .summary-card { align-items: stretch; flex-direction: column; }
  .favorite-btn { width: 100%; }
  .thumb { flex-basis: 92px; height: 60px; }
  .section-head { align-items: flex-start; flex-direction: column; }
  .map-link { width: 100%; }
  .section-card, .contact-card { padding: 20px; }
}
</style>

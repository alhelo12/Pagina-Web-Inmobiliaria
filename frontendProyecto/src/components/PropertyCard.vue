<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { enumLabel } from '@/utils/enums'
import { FALLBACK_PROPERTY_IMAGE } from '@/utils/propertyImages'

const props = defineProps({
  id: Number,
  title: String,
  price: [Number, String],
  city: String,
  type: String,
  image: String,
  transactionType: {
    type: String,
    default: ''
  },
  bedrooms: {
    type: [Number, String],
    default: 0
  },
  bathrooms: {
    type: [Number, String],
    default: 0
  },
  squareMeters: {
    type: [Number, String],
    default: 0
  },
  images: {
    type: Array,
    default: () => []
  },
  showCta: {
    type: Boolean,
    default: false
  }
})

const auth = useAuthStore()
const favStore = useFavoritesStore()
const isFav = computed(() => favStore.isFavorite(props.id))

const typeLabel = (v) => enumLabel('property_types', v)
const operationLabel = (v) => enumLabel('transaction_types', v)

const extrasLabels = computed(() => {
  if (!props.images || !props.images.length) return []
  return props.images
    .filter((img) => img.is_extra && img.label)
    .map((img) => img.label)
    .slice(0, 3)
})

const toggle = async (e) => {
  e.preventDefault()
  e.stopPropagation()
  if (!auth.isLogged || auth.role !== 'client') return
  await favStore.toggleFavorite(props.id)
}

const handleImageError = (event) => {
  if (event.target.src !== FALLBACK_PROPERTY_IMAGE) {
    event.target.src = FALLBACK_PROPERTY_IMAGE
  }
}
</script>

<template>
  <article class="card">
    <div class="media">
      <img :src="image || FALLBACK_PROPERTY_IMAGE" :alt="title" loading="lazy" @error="handleImageError" />
      <span class="type-pill type-gold">{{ typeLabel(type) }}</span>
      <span class="type-pill type-blue">{{ operationLabel(transactionType) }}</span>
      <button
        class="fav-btn"
        :class="{ active: isFav }"
        :aria-label="isFav ? 'Quitar de favoritos' : 'Guardar favorito'"
        :title="auth.isLogged ? (isFav ? 'Quitar de favoritos' : 'Guardar favorito') : 'Inicia sesion para guardar favoritos'"
        @click="toggle"
      >
        <svg v-if="isFav" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#d64545" stroke="#d64545" stroke-width="2">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
      </button>
    </div>

    <div class="body">
      <p class="city">{{ operationLabel(transactionType) }} — {{ city }}</p>
      <h3 class="serif-display">{{ title }}</h3>
      <div class="meta">
        <span>{{ Number(squareMeters || 0) }} m²</span>
        <span>{{ Number(bedrooms || 0) }} hab.</span>
        <span>{{ Number(bathrooms || 0) }} baños</span>
        <span v-for="extra in extrasLabels" :key="extra" class="extra-tag">{{ extra }}</span>
      </div>
      <div class="bottom-row">
        <strong>${{ Number(price).toLocaleString('es-MX') }} <small>MXN</small></strong>
        <span v-if="showCta" class="cta">Ver →</span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card {
  position: relative;
  min-height: 440px;
  height: 100%;
  display: flex;
  overflow: hidden;
  background: var(--color-petrol);
  border: 1px solid var(--color-line);
  border-radius: 2px;
  box-shadow: var(--shadow-soft);
  transition: transform .25s ease, box-shadow .25s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-strong);
}

.media {
  position: absolute;
  inset: 0;
  overflow: hidden;
  background: var(--color-ink);
}

.media::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(7,27,28,.18) 0%, rgba(7,27,28,0) 32%, rgba(7,27,28,.28) 55%, rgba(7,27,28,.9) 100%);
}

.media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform .5s ease;
}

.card:hover .media img {
  transform: scale(1.05);
}

.type-pill,
.fav-btn {
  position: absolute;
  z-index: 2;
}

.type-pill {
  padding: 7px 13px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .14em;
  text-transform: uppercase;
}

.type-gold {
  left: 16px;
  top: 16px;
  background: var(--color-brass);
  color: #fff;
}

.type-blue {
  left: 16px;
  top: 50px;
  background: rgba(7, 27, 28, .72);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, .28);
  backdrop-filter: blur(6px);
}

.fav-btn {
  right: 14px;
  top: 14px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, .94);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform .25s ease, background .2s ease;
  z-index: 2;
  color: #8a8a8a;
}

.fav-btn:hover { transform: scale(1.1); background: #fff; }

.fav-btn.active {
  background: #fff;
  animation: heartPop .35s ease;
}

@keyframes heartPop {
  0% { transform: scale(1); }
  50% { transform: scale(1.25); }
  100% { transform: scale(1.08); }
}

.body {
  position: relative;
  z-index: 1;
  margin-top: auto;
  width: 100%;
  padding: 22px 22px 20px;
  color: #fff;
}

.city {
  margin: 0 0 6px;
  color: var(--color-brass);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .2em;
}

.body h3 {
  margin: 0 0 12px;
  color: #fff;
  font-size: 29px;
  line-height: 1.05;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.meta span {
  padding: 5px 10px;
  background: rgba(255, 255, 255, .14);
  border: 1px solid rgba(255, 255, 255, .18);
  color: rgba(255, 255, 255, .92);
  font-size: 12px;
  font-weight: 500;
  backdrop-filter: blur(4px);
}

.extra-tag {
  background: rgba(185, 148, 95, .85) !important;
  border-color: transparent !important;
  color: #fff !important;
}

.bottom-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, .22);
}

.body strong {
  display: block;
  color: #fff;
  font-family: var(--serif);
  font-weight: 500;
  font-size: 24px;
  letter-spacing: .01em;
}

.body strong small {
  font-family: var(--sans);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .18em;
  color: rgba(255, 255, 255, .7);
}

.cta {
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: .16em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--color-brass);
  padding-bottom: 3px;
  white-space: nowrap;
}
</style>

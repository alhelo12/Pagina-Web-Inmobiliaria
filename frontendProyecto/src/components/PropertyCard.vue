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
        <svg v-if="isFav" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#d64545" stroke="#d64545" stroke-width="2">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
      </button>
    </div>

    <div class="body">
      <p class="city">{{ city }}</p>
      <h3>{{ title }}</h3>
      <div class="meta">
        <span>{{ Number(squareMeters || 0) }} m2</span>
        <span>{{ Number(bedrooms || 0) }} Hab.</span>
        <span>{{ Number(bathrooms || 0) }} baños</span>
        <span v-for="extra in extrasLabels" :key="extra" class="extra-tag">{{ extra }}</span>
      </div>
      <div class="bottom-row">
        <strong>${{ Number(price).toLocaleString('es-MX') }} MXN</strong>
        <span v-if="showCta" class="cta">Ver propiedad</span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card {
  position: relative;
  background: #fffdf8;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(7, 23, 45, .08);
  box-shadow: var(--shadow-soft);
  transition: transform .25s ease, box-shadow .25s ease;
}

.card:hover {
  transform: translateY(-7px);
  box-shadow: var(--shadow-strong);
}

.media {
  position: relative;
  height: 220px;
  overflow: hidden;
  background: #102e4f;
}

.media::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(7,23,45,.04), rgba(7,23,45,.56));
}

.media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform .35s ease;
}

.card:hover .media img {
  transform: scale(1.06);
}

.type-pill,
.fav-btn {
  position: absolute;
  z-index: 1;
}

.type-pill {
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.type-gold {
  left: 14px;
  top: 14px;
  background: #d6a848;
  color: #07172d;
}

.type-blue {
  left: 90px;
  top: 14px;
  background: #0a355e;
  color: #fff;
}

.fav-btn {
  right: 14px;
  top: 14px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(7, 23, 45, 0.15);
  transition: transform .25s ease, background .2s ease, box-shadow .2s ease;
  z-index: 2;
  color: #c4c4c4;
}

.fav-btn:hover {
  transform: scale(1.12);
  background: #fff;
  box-shadow: 0 6px 20px rgba(7, 23, 45, 0.25);
}

.fav-btn.active {
  background: #fff;
  transform: scale(1.08);
  animation: heartPop .35s ease;
}

@keyframes heartPop {
  0% { transform: scale(1); }
  50% { transform: scale(1.25); }
  100% { transform: scale(1.08); }
}

.fav-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.body {
  padding: 20px;
}

.city {
  color: #d6a848;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: .12em;
  margin-bottom: 8px;
}

.body h3 {
  min-height: 48px;
  color: #07172d;
  font-size: 20px;
  line-height: 1.2;
  margin-bottom: 14px;
}

.meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}

.meta span {
  padding: 6px 9px;
  border-radius: 999px;
  background: #eef4fb;
  color: #40566e;
  font-size: 12px;
  font-weight: 700;
}

.extra-tag {
  background: linear-gradient(135deg, #0a355e 0%, #11497d 100%) !important;
  color: #fff !important;
}

.body strong {
  display: block;
  color: #07172d;
  font-size: 21px;
}

.bottom-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.cta {
  color: #d6a848;
  font-size: 13px;
  font-weight: 800;
}
</style>

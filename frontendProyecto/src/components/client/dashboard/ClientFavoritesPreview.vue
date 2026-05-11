<script setup>
import { RouterLink } from 'vue-router'
import { getPropertyImage, FALLBACK_PROPERTY_IMAGE } from '@/utils/propertyImages'

defineProps({
  favorites: { type: Array, default: () => [] }
})

const getId = (fav) => {
  const prop = fav.favorited_property ?? fav.property ?? fav
  return prop?.id
}

const getTitle = (fav) => {
  const prop = fav.favorited_property ?? fav.property ?? fav
  return prop?.title || 'Sin titulo'
}

const getCity = (fav) => {
  const prop = fav.favorited_property ?? fav.property ?? fav
  return prop?.city || 'Sin ciudad'
}

const getPrice = (fav) => {
  const prop = fav.favorited_property ?? fav.property ?? fav
  return Number(prop?.price || 0).toLocaleString('es-MX')
}
</script>

<template>
  <article class="favorites-card">
    <div class="card-head">
      <p>Favoritos</p>
      <h3>Propiedades Guardadas</h3>
    </div>

    <div v-if="favorites.length" class="fav-list">
      <RouterLink
        v-for="fav in favorites.slice(0, 4)"
        :key="fav.id"
        :to="`/propiedades/${getId(fav)}`"
        class="fav-item"
      >
        <div class="fav-thumb">
          <img
            :src="getPropertyImage(fav.favorited_property ?? fav.property ?? fav) || FALLBACK_PROPERTY_IMAGE"
            :alt="getTitle(fav)"
            @error="(e) => { e.target.src = FALLBACK_PROPERTY_IMAGE }"
          />
        </div>
        <div class="fav-info">
          <span class="city">{{ getCity(fav) }}</span>
          <strong>{{ getTitle(fav) }}</strong>
          <span class="price">${{ getPrice(fav) }}</span>
        </div>
      </RouterLink>
    </div>

    <p v-else class="empty">No tienes favoritos guardados.</p>
  </article>
</template>

<style scoped>
.favorites-card {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 10px;
  box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08);
  padding: 18px;
}
.card-head { margin-bottom: 12px; }
.card-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.card-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; }
.fav-list { display: grid; gap: 10px; }
.fav-item {
  display: flex;
  gap: 12px;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid var(--color-line);
  background: #fff;
  text-decoration: none;
  transition: .2s ease;
}
.fav-item:hover { border-color: var(--color-gold); background: #fdfcf8; }
.fav-thumb {
  width: 52px;
  height: 52px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--color-cream);
}
.fav-thumb img { width: 100%; height: 100%; object-fit: cover; }
.fav-info { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.fav-info .city { color: var(--color-gold); font-size: 10px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; }
.fav-info strong {
  color: var(--color-navy);
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 2px 0;
}
.fav-info .price { color: var(--color-navy-2); font-weight: 700; font-size: 13px; }
.empty { margin: 0; color: var(--color-muted); font-size: 13px; }
</style>
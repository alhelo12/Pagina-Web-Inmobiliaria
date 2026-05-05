<script setup>
import { useAuthStore } from '@/stores/authStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { FALLBACK_PROPERTY_IMAGE } from '@/utils/propertyImages'

const props = defineProps({
  id: Number,
  title: String,
  price: [Number, String],
  city: String,
  type: String,
  image: String
})

const auth = useAuthStore()
const favStore = useFavoritesStore()

const typeLabel = {
  house: 'Casa',
  apartment: 'Departamento',
  land: 'Terreno',
  commercial: 'Comercial'
}

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
      <span class="type-pill">{{ typeLabel[type] ?? type }}</span>
      <button
        class="fav-btn"
        :class="{ active: favStore.isFavorite(id) }"
        aria-label="Guardar favorito"
        :title="auth.isLogged ? 'Guardar favorito' : 'Inicia sesion para guardar favoritos'"
        @click="toggle"
      >♥</button>
    </div>

    <div class="body">
      <p class="city">{{ city }}</p>
      <h3>{{ title }}</h3>
      <div class="meta">
        <span>Verificada</span>
        <span>Asesor disponible</span>
      </div>
      <strong>${{ Number(price).toLocaleString('es-MX') }} MXN</strong>
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
  left: 14px;
  top: 14px;
  padding: 7px 12px;
  border-radius: 999px;
  background: #d6a848;
  color: #07172d;
  font-size: 12px;
  font-weight: 900;
}

.fav-btn {
  right: 14px;
  top: 14px;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(255,255,255,.92);
  color: #87909b;
  font-size: 18px;
  box-shadow: 0 10px 22px rgba(7,23,45,.18);
  transition: transform .2s ease, color .2s ease;
}

.fav-btn.active {
  color: #d64545;
  transform: scale(1.08);
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

.body strong {
  display: block;
  color: #07172d;
  font-size: 21px;
}
</style>

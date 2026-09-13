<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { getPropertyImage } from '@/utils/propertyImages'

const favStore = useFavoritesStore()

const propertyOf = (fav) => fav.favorited_property ?? fav.property ?? fav
const idOf = (fav) => propertyOf(fav)?.id ?? fav.property_id
const imageOf = (fav) => getPropertyImage(propertyOf(fav))

onMounted(() => favStore.fetchFavorites())
</script>

<template>
  <div class="dashboard">
    <aside class="dash-sidebar">
      <RouterLink to="/" class="brand"><span>J</span><strong>JAKEDA</strong></RouterLink>
      <nav>
        <RouterLink to="/">Inicio</RouterLink>
        <RouterLink to="/favoritos">Favoritos</RouterLink>
      </nav>
    </aside>

    <div class="favorites">
      <section class="hero-panel">
        <p class="eyebrow-label">Dashboard personal</p>
        <h1 class="serif-display">Mis favoritos</h1>
        <span>Propiedades guardadas con una vista clara para comparar opciones.</span>
      </section>

      <div v-if="favStore.loading" class="state">
        <div class="spinner"></div>
      </div>

      <div v-else-if="favStore.error" class="state error-msg" role="alert">
        {{ favStore.error }}
      </div>

      <div v-else-if="!favStore.favorites.length" class="empty-state">
        <h2 class="serif-display">Aun no tienes propiedades favoritas</h2>
        <p>Explora el catalogo y guarda las propiedades que quieras revisar despues.</p>
        <RouterLink to="/propiedades" class="btn-ink">Ver propiedades</RouterLink>
      </div>

      <div v-else class="grid">
        <RouterLink
          v-for="fav in favStore.favorites"
          :key="fav.id"
          :to="`/propiedades/${idOf(fav)}`"
          class="fav-card"
        >
          <div class="media">
            <img decoding="async" :src="imageOf(fav)" :alt="propertyOf(fav)?.title" loading="lazy" />
            <span>Guardada</span>
          </div>
          <div class="body">
            <p>{{ propertyOf(fav)?.city }}</p>
            <h3>{{ propertyOf(fav)?.title }}</h3>
            <strong>${{ Number(propertyOf(fav)?.price ?? 0).toLocaleString('es-MX') }} MXN</strong>
            <div class="chips">
              <span>{{ propertyOf(fav)?.property_type }}</span>
              <span>{{ propertyOf(fav)?.transaction_type }}</span>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  min-height: calc(100vh - 60px);
  background: var(--color-ivory);
}

.dash-sidebar {
  position: sticky;
  top: 82px;
  height: calc(100vh - 82px);
  width: 260px;
  flex: 0 0 260px;
  padding: 24px;
  background: var(--color-petrol);
  border-right: 1px solid var(--color-line);
  box-shadow: none;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--color-ivory);
  margin-bottom: 28px;
}

.brand span {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: var(--color-brass);
  color: var(--color-petrol);
  font-weight: 900;
}

.brand strong {
  letter-spacing: .22em;
  font-size: 12px;
  font-weight: 600;
}

nav {
  display: grid;
  gap: 8px;
}

nav a {
  padding: 12px 14px;
  border-radius: 8px;
  color: rgba(243, 238, 228, .72);
  font-weight: 600;
  font-size: 14px;
  border-bottom: 1px solid transparent;
}

nav a.router-link-active,
nav a:hover {
  background: rgba(185, 148, 95, .14);
  color: var(--color-brass);
}

.favorites {
  flex: 1;
  min-width: 0;
  padding: 34px;
}

.hero-panel {
  padding: 32px;
  border-radius: 12px;
  color: var(--color-ivory);
  background: var(--color-petrol);
  border: 1px solid var(--color-line);
  box-shadow: none;
  margin-bottom: 24px;
}

.hero-panel p {
  color: var(--color-brass);
  margin-bottom: 10px;
}

.hero-panel h1 {
  font-size: clamp(30px, 5vw, 48px);
  margin: 0 0 10px;
  color: var(--color-ivory);
}

.hero-panel span {
  color: rgba(243, 238, 228, .75);
  font-size: 14px;
}

.state,
.empty-state {
  display: grid;
  place-items: center;
  text-align: center;
  gap: 16px;
  min-height: 330px;
  color: var(--color-muted);
  background: #fff;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  box-shadow: none;
  padding: 34px;
}

.empty-state h2 {
  color: var(--color-petrol);
  font-size: 30px;
  font-weight: 500;
  margin: 0;
}

.error-msg { color: var(--color-danger); }
.spinner {
  width: 42px;
  height: 42px;
  border: 3px solid var(--color-line);
  border-top-color: var(--color-brass);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
}

.fav-card {
  background: #fff;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: none;
  transition: border-color .2s ease;
}

.fav-card:hover {
  transform: none;
  box-shadow: none;
  border-color: var(--color-brass);
}

.media {
  position: relative;
  height: 210px;
  background: var(--color-petrol);
  overflow: hidden;
}

.media::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent, rgba(7, 27, 28, .45));
}

.media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform .35s ease;
}

.fav-card:hover img {
  transform: scale(1.03);
}

.media span {
  position: absolute;
  z-index: 1;
  top: 14px;
  left: 14px;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--color-brass);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .12em;
  text-transform: uppercase;
}

.body {
  padding: 20px;
}

.body p {
  color: var(--color-brass-deep);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .22em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.body h3 {
  min-height: 48px;
  color: var(--color-petrol);
  font-family: var(--serif);
  font-weight: 500;
  font-size: 22px;
  line-height: 1.2;
  margin-bottom: 14px;
}

.body strong {
  color: var(--color-petrol);
  font-size: 20px;
}

.chips {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  flex-wrap: wrap;
  padding-top: 14px;
  border-top: 1px solid var(--color-line);
}

.chips span {
  padding: 5px 10px;
  border-radius: 999px;
  background: transparent;
  border: 1px solid var(--color-line);
  color: var(--color-muted);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
}

@media (max-width: 1040px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard {
    flex-direction: column;
  }
  .dash-sidebar {
    position: static;
    width: 100%;
    height: auto;
    flex: none;
  }
  nav {
    grid-template-columns: repeat(2, 1fr);
  }
  .favorites {
    padding: 22px;
  }
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

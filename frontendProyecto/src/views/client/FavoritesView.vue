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
        <RouterLink to="/propiedades">Explorar</RouterLink>
        <RouterLink to="/crear-propiedad">Publicar</RouterLink>
        <RouterLink to="/contacto">Configuracion</RouterLink>
      </nav>
    </aside>

    <main class="favorites">
      <section class="hero-panel">
        <p>Dashboard personal</p>
        <h1>Mis favoritos</h1>
        <span>Propiedades guardadas con una vista clara para comparar opciones.</span>
      </section>

      <div v-if="favStore.loading" class="state">
        <div class="spinner"></div>
      </div>

      <div v-else-if="favStore.error" class="state error-msg">
        {{ favStore.error }}
      </div>

      <div v-else-if="!favStore.favorites.length" class="empty-state">
        <h2>Aun no tienes propiedades favoritas</h2>
        <p>Explora el catalogo y guarda las propiedades que quieras revisar despues.</p>
        <RouterLink to="/propiedades" class="btn">Ver propiedades</RouterLink>
      </div>

      <div v-else class="grid">
        <RouterLink
          v-for="fav in favStore.favorites"
          :key="fav.id"
          :to="`/propiedades/${idOf(fav)}`"
          class="fav-card"
        >
          <div class="media">
            <img :src="imageOf(fav)" :alt="propertyOf(fav)?.title" />
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
    </main>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  min-height: calc(100vh - 60px);
  background:
    radial-gradient(circle at 30% 0%, rgba(42,140,255,.12), transparent 28%),
    #f5f2ec;
}

.dash-sidebar {
  position: sticky;
  top: 82px;
  height: calc(100vh - 82px);
  width: 260px;
  flex: 0 0 260px;
  padding: 24px;
  background: linear-gradient(180deg, #07172d, #102e4f);
  box-shadow: var(--shadow-strong);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  margin-bottom: 28px;
}

.brand span {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: #d6a848;
  color: #07172d;
  font-weight: 900;
}

.brand strong {
  letter-spacing: .12em;
}

nav {
  display: grid;
  gap: 8px;
}

nav a {
  padding: 13px 14px;
  border-radius: 10px;
  color: rgba(255,255,255,.78);
  font-weight: 800;
}

nav a.router-link-active,
nav a:hover {
  background: rgba(214,168,72,.16);
  color: #f2c46d;
}

.favorites {
  flex: 1;
  min-width: 0;
  padding: 34px;
}

.hero-panel {
  padding: 32px;
  border-radius: 16px;
  color: white;
  background:
    linear-gradient(90deg, rgba(7,23,45,.96), rgba(16,46,79,.7)),
    url('@/assets/images/fondo.webp') center/cover;
  box-shadow: var(--shadow-strong);
  margin-bottom: 24px;
}

.hero-panel p {
  color: #f2c46d;
  font-weight: 900;
  letter-spacing: .16em;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.hero-panel h1 {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(36px, 5vw, 58px);
  margin-bottom: 10px;
}

.hero-panel span {
  color: rgba(255,255,255,.78);
}

.state,
.empty-state {
  display: grid;
  place-items: center;
  text-align: center;
  gap: 16px;
  min-height: 330px;
  color: #65717e;
  background: #fffdf8;
  border-radius: 16px;
  box-shadow: var(--shadow-soft);
  padding: 34px;
}

.empty-state h2 {
  font-family: Georgia, 'Times New Roman', serif;
  color: #07172d;
  font-size: 32px;
}

.error-msg { color: #991b1b; }
.spinner {
  width: 42px;
  height: 42px;
  border: 3px solid #eadfcf;
  border-top-color: #d6a848;
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.btn {
  display: inline-flex;
  min-height: 46px;
  align-items: center;
  padding: 0 22px;
  border-radius: 8px;
  background: #d6a848;
  color: #07172d;
  font-weight: 900;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
}

.fav-card {
  background: #fffdf8;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  transition: transform .24s ease, box-shadow .24s ease;
}

.fav-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-strong);
}

.media {
  position: relative;
  height: 210px;
  background: #102e4f;
  overflow: hidden;
}

.media::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent, rgba(7,23,45,.62));
}

.media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform .35s ease;
}

.fav-card:hover img {
  transform: scale(1.06);
}

.media span {
  position: absolute;
  z-index: 1;
  top: 14px;
  left: 14px;
  padding: 7px 12px;
  border-radius: 999px;
  background: #d6a848;
  color: #07172d;
  font-size: 12px;
  font-weight: 900;
}

.body {
  padding: 20px;
}

.body p {
  color: #d6a848;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: .12em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.body h3 {
  min-height: 48px;
  color: #07172d;
  font-size: 20px;
  line-height: 1.2;
  margin-bottom: 14px;
}

.body strong {
  color: #07172d;
  font-size: 22px;
}

.chips {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.chips span {
  padding: 6px 9px;
  border-radius: 999px;
  background: #eef4fb;
  color: #40566e;
  font-size: 12px;
  font-weight: 800;
}

@media (max-width: 1040px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 820px) {
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
}

@media (max-width: 560px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

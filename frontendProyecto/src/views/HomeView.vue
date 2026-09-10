<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { usePropertyStore } from '@/stores/propertyStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useAuthStore } from '@/stores/authStore'
import PropertyCard from '@/components/PropertyCard.vue'
import { getPropertyImage } from '@/utils/propertyImages'
import homeFallbackImage from '@/assets/images/fondo2.jpg'
const router = useRouter()
const propertyStore = usePropertyStore()
const favoritesStore = useFavoritesStore()
const authStore = useAuthStore()

const filters = ref({
  city: 'Tuxtla Gutiérrez',
  property_type: '',
  transaction_type: '',
  max_price: ''
})

const categories = [
  { key: 'house', label: 'Casas', note: 'Residencial familiar' },
  { key: 'apartment', label: 'Departamentos', note: 'Ciudad y comodidad' },
  { key: 'land', label: 'Terrenos', note: 'Inversión y construcción' },
  { key: 'commercial', label: 'Locales comerciales', note: 'Negocio y oficina' }
]

const selectedCategory = ref('')

const approvedProperties = computed(() =>
  (propertyStore.properties ?? []).filter((p) => p.status === 'approved')
)

const cityOptions = computed(() =>
  [...new Set(approvedProperties.value.map((p) => p.city).filter(Boolean))]
)

const heroProperty = computed(() => approvedProperties.value[0] ?? null)
const heroImage = computed(() =>
  heroProperty.value ? getPropertyImage(heroProperty.value) : homeFallbackImage
)

const onHeroImageError = (event) => {
  if (event?.target) event.target.src = homeFallbackImage
}

const highlightedProperties = computed(() => {
  let list = approvedProperties.value

  if (selectedCategory.value) {
    list = list.filter((p) => p.property_type === selectedCategory.value)
  }

  return list
    .filter((p) => {
      if (filters.value.property_type && p.property_type !== filters.value.property_type) return false
      if (filters.value.transaction_type && p.transaction_type !== filters.value.transaction_type) return false
      if (filters.value.max_price && Number(p.price) > Number(filters.value.max_price)) return false
      return true
    })
    .slice(0, 3)
})

const goToProperties = (extra = {}) => {
  const query = { ...extra }
  if (filters.value.city) query.city = filters.value.city
  if (filters.value.property_type) query.property_type = filters.value.property_type
  if (filters.value.transaction_type) query.transaction_type = filters.value.transaction_type
  if (filters.value.max_price) query.max_price = Number(filters.value.max_price)
  router.push({ path: '/propiedades', query })
}

const resetFilters = () => {
  filters.value = {
    city: 'Tuxtla Gutiérrez',
    property_type: '',
    transaction_type: '',
    max_price: ''
  }
}

const selectCategory = (value) => {
  selectedCategory.value = selectedCategory.value === value ? '' : value
}

onMounted(async () => {
  await propertyStore.fetch({ status: 'approved', limit: 40 })
  if (authStore.isLogged && authStore.role === 'client') {
    await favoritesStore.fetchFavorites()
  }
})
</script>

<template>
  <main class="home-page">
    <header class="hero">
      <img
        class="hero-image"
        :src="heroImage"
        @error="onHeroImageError"
        alt="Propiedad principal"
      />
      <div class="hero-overlay"></div>

      <div class="hero-content">
        <p class="eyebrow-label hero-eyebrow">Jakeda · Inmobiliaria premium</p>
        <h1 class="serif-display">Hogares que inspiran tu vida</h1>
        <p class="hero-sub">
          Propiedades reales con diseño, ubicación y valor. Filtra en segundos y descubre la opción ideal para ti.
        </p>
        <div class="hero-actions">
          <RouterLink to="/propiedades" class="btn-brass">Explorar propiedades</RouterLink>
          <RouterLink to="/nosotros" class="btn-ghost-light">Conocer más</RouterLink>
        </div>
        <div class="search-shell">
          <div class="search-bar">
            <input v-model="filters.city" type="text" placeholder="Ciudad" class="search-input search-input-city" />
            <span class="search-divider"></span>
            <select v-model="filters.property_type" class="search-select">
              <option value="">Tipo</option>
              <option value="house">Casa</option>
              <option value="apartment">Departamento</option>
              <option value="land">Terreno</option>
              <option value="commercial">Local comercial</option>
            </select>
            <span class="search-divider"></span>
            <select v-model="filters.transaction_type" class="search-select">
              <option value="">Operación</option>
              <option value="sale">Venta</option>
              <option value="rent">Renta</option>
            </select>
            <span class="search-divider"></span>
            <input v-model="filters.max_price" type="number" placeholder="Precio max" class="search-input" />
            <div class="search-actions">
              <button class="search-btn" @click="goToProperties">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
                Buscar
              </button>
              <button class="search-reset" @click="resetFilters" title="Limpiar filtros">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <nav class="cat-strip" aria-label="Categorías">
      <button
        v-for="c in categories"
        :key="c.key"
        type="button"
        class="cat-item"
        :class="{ active: selectedCategory === c.key }"
        @click="selectCategory(c.key)"
      >
        <span class="cat-label">{{ c.label }}</span>
        <span class="cat-note">{{ c.note }}</span>
      </button>
    </nav>

    <section class="about reveal">
      <div class="about-img-wrap">
        <img src="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=800&q=80" alt="Habitacion elegante" />
      </div>
      <div class="about-content">
        <p class="eyebrow-label">Nosotros</p>
        <h2 class="serif-display">Espacios que se sienten como hogar</h2>
        <hr class="rule" />
        <p class="about-copy">
          Curaduría de propiedades con carácter: luz, proporción y ubicación. Te acompañamos con trato cercano y criterio patrimonial.
        </p>
        <article class="rating-card">
          <strong class="rating-value serif-display">4.9 / 5</strong>
          <p>La calificación de familias e inversionistas que ya encontraron su lugar.</p>
        </article>
        <article class="contact-card">
          <div>
            <small>Habla con un asesor por teléfono o correo</small>
            <strong>+52 961 123 4567</strong>
          </div>
          <RouterLink class="btn-ink" to="/contacto">Llamar</RouterLink>
        </article>
      </div>
    </section>

    <section class="featured reveal">
      <div class="section-head">
        <div>
          <p class="eyebrow-label">Selección editorial</p>
          <h3 class="serif-display">Propiedades destacadas</h3>
        </div>
        <RouterLink to="/propiedades" class="link-all">Ver todas las propiedades →</RouterLink>
      </div>
      <hr class="rule" />

      <div v-if="propertyStore.loading" class="state">Cargando propiedades...</div>
      <div v-else-if="!highlightedProperties.length" class="state">No encontramos resultados con esos filtros.</div>
      <div v-else class="cards-grid">
        <RouterLink v-for="p in highlightedProperties" :key="p.id" :to="`/propiedades/${p.id}`" class="card-link">
          <PropertyCard
            :id="p.id"
            :title="p.title"
            :price="p.price"
            :city="p.city"
            :type="p.property_type"
            :transaction-type="p.transaction_type"
            :bedrooms="p.bedrooms"
            :bathrooms="p.bathrooms"
            :square-meters="p.square_meters"
            :images="p.images || []"
            :image="getPropertyImage(p)"
            :show-cta="true"
          />
        </RouterLink>
      </div>
    </section>

    <section class="bottom-banner reveal">
      <div class="banner-copy">
        <p class="eyebrow-label eyebrow-on-dark">Nuestros servicios</p>
        <h2 class="serif-display">El confort y el carácter, en un mismo lugar</h2>
        <hr class="rule rule-light" />
        <p>
          Propiedades seleccionadas y acompañamiento personalizado según lo que buscas: habitar, rentar o invertir.
        </p>
        <RouterLink to="/servicios" class="btn-ghost-light banner-cta">Ver servicios</RouterLink>
      </div>
      <div class="banner-cards">
        <article class="mini-card" v-for="p in highlightedProperties.slice(0, 2)" :key="`mini-${p.id}`">
          <img :src="getPropertyImage(p)" :alt="p.title" />
          <div>
            <strong>{{ p.title }}</strong>
            <small>{{ p.city }} · ${{ Number(p.price).toLocaleString('es-MX') }}</small>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>

<style scoped>
.home-page {
  font-family: var(--sans);
  background: var(--color-ivory);
  color: var(--color-ink);
  padding: 0 0 72px;
  overflow: hidden;
}

/* ── HERO full-bleed cinematográfico ── */
.hero {
  position: relative;
  min-height: 100dvh;
  display: flex;
  align-items: flex-end;
  background: var(--color-ink);
  overflow: hidden;
}

.hero-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  background:
    linear-gradient(180deg, rgba(7, 27, 28, 0.55) 0%, rgba(7, 27, 28, 0.25) 42%, rgba(7, 27, 28, 0.86) 100%),
    linear-gradient(90deg, rgba(7, 27, 28, 0.82) 0%, rgba(7, 27, 28, 0.2) 62%, transparent 100%);
}

.hero-content {
  position: relative;
  z-index: 3;
  width: min(var(--container-max), 100% - (var(--container-pad) * 2));
  margin-inline: auto;
  padding: 16vh 0 44px;
  color: var(--color-ivory);
  text-align: left;
}

.hero-eyebrow {
  color: var(--color-brass);
  margin: 0 0 16px;
}

.hero-content h1 {
  margin: 0;
  color: #fff;
  font-size: clamp(52px, 8.5vw, 116px);
  max-width: 12ch;
}

.hero-sub {
  margin: 18px 0 0;
  max-width: 52ch;
  line-height: 1.65;
  color: rgba(243, 238, 228, 0.88);
  font-size: clamp(15px, 1.6vw, 17px);
}

.hero-actions {
  margin-top: 28px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

/* ── Filter strip editorial sobre héroe ── */
.search-shell {
  margin-top: 36px;
  border-top: 1px solid rgba(243, 238, 228, 0.35);
  padding-top: 18px;
}

.search-bar {
  display: grid;
  grid-template-columns: 1.2fr auto 1fr auto 1fr auto 1fr auto;
  align-items: center;
  gap: 10px;
  background: transparent;
  padding: 0;
}

.search-input,
.search-select {
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(243, 238, 228, 0.4);
  border-radius: 0;
  color: var(--color-ivory);
  font-size: 14px;
  height: 44px;
  padding: 0 6px;
  outline: none;
  min-width: 0;
}

.search-input::placeholder {
  color: rgba(243, 238, 228, 0.6);
}

.search-select {
  cursor: pointer;
}

.search-select option {
  color: var(--color-ink);
}

.search-input:focus,
.search-select:focus {
  border-bottom-color: var(--color-brass);
}

.search-divider {
  width: 1px;
  height: 28px;
  background: rgba(243, 238, 228, 0.25);
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--color-brass);
  color: #fff;
  border: 1px solid var(--color-brass);
  padding: 12px 22px;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.search-btn:hover {
  background: var(--color-brass-deep);
}

.search-reset {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  background: transparent;
  color: var(--color-ivory);
  border: 1px solid rgba(243, 238, 228, 0.5);
  border-radius: 50%;
  cursor: pointer;
  flex-shrink: 0;
}

.search-reset:hover {
  background: rgba(255, 255, 255, 0.12);
}

/* ── Tira editorial de categorías ── */
.cat-strip {
  width: min(var(--container-max), 100% - (var(--container-pad) * 2));
  margin: 0 auto;
  padding: 26px 0;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  border-bottom: 1px solid var(--color-line);
}

.cat-item {
  background: transparent;
  border: none;
  border-left: 1px solid var(--color-line);
  padding: 6px 20px;
  text-align: left;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cat-item:first-child {
  border-left: none;
  padding-left: 0;
}

.cat-label {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-petrol);
}

.cat-note {
  font-size: 13px;
  color: var(--color-muted);
}

.cat-item.active .cat-label {
  color: var(--color-brass-deep);
}

.cat-item.active {
  box-shadow: inset 0 2px 0 var(--color-brass);
}

/* ── Secciones editoriales ── */
.rule {
  border: none;
  border-top: 1px solid var(--color-line);
  margin: 20px 0;
}

.rule-light {
  border-top-color: rgba(243, 238, 228, 0.3);
}

.eyebrow-on-dark {
  color: var(--color-brass);
}

.about,
.featured {
  width: min(var(--container-max), 100% - (var(--container-pad) * 2));
  margin: 72px auto 0;
}

.about {
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  gap: clamp(28px, 4vw, 64px);
  align-items: start;
}

.about-img-wrap img {
  width: 100%;
  aspect-ratio: 4 / 5;
  object-fit: cover;
  display: block;
}

.about-content h2 {
  margin: 0;
  font-size: clamp(34px, 4.4vw, 56px);
  color: var(--color-petrol);
}

.about-copy {
  margin: 0;
  color: #43524f;
  line-height: 1.7;
  max-width: 52ch;
}

.rating-card,
.contact-card {
  margin-top: 22px;
  padding: 20px 0;
  border-top: 1px solid var(--color-line);
}

.rating-value {
  font-size: clamp(38px, 4vw, 54px);
  color: var(--color-petrol);
}

.rating-card p,
.contact-card small {
  margin: 8px 0 0;
  color: var(--color-muted);
  line-height: 1.6;
}

.contact-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.contact-card strong {
  display: block;
  margin-top: 6px;
  font-size: 20px;
  color: var(--color-petrol);
}

/* ── Destacadas asimétricas ── */
.featured {
  background: transparent;
  border: none;
  padding: 0;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
}

.section-head h3 {
  margin: 6px 0 0;
  color: var(--color-petrol);
  font-size: clamp(32px, 4vw, 52px);
}

.link-all {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-brass-deep);
  white-space: nowrap;
}

.state {
  padding: 16px 0 24px;
  color: var(--color-muted);
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 22px;
  margin-top: 26px;
}

.card-link {
  color: inherit;
  transition: transform 0.22s ease;
  min-width: 0;
}

.card-link:hover {
  transform: translateY(-4px);
}

.card-link:nth-child(1) {
  grid-column: span 7;
}

.card-link:nth-child(2) {
  grid-column: span 5;
  margin-top: 48px;
}

.card-link:nth-child(3) {
  grid-column: 3 / span 7;
}

/* ── Cierre petrol ── */
.bottom-banner {
  width: min(var(--container-max), 100% - (var(--container-pad) * 2));
  margin: 80px auto 0;
  background: var(--color-petrol);
  color: var(--color-ivory);
  padding: clamp(32px, 4vw, 56px);
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 32px;
  align-items: center;
}

.banner-copy h2 {
  margin: 6px 0 0;
  color: #fff;
  font-size: clamp(32px, 4vw, 54px);
}

.banner-copy p {
  margin: 0;
  color: rgba(243, 238, 228, 0.82);
  max-width: 52ch;
  line-height: 1.65;
}

.banner-cta {
  margin-top: 24px;
}

.banner-cards {
  display: grid;
  gap: 14px;
}

.mini-card {
  background: var(--color-card);
  color: var(--color-ink);
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: 14px;
  padding: 12px;
  align-items: center;
}

.mini-card:nth-child(2) {
  margin-left: 32px;
}

.mini-card img {
  width: 96px;
  height: 96px;
  object-fit: cover;
}

.mini-card strong {
  color: var(--color-petrol);
}

.mini-card small {
  display: block;
  margin-top: 6px;
  color: var(--color-muted);
}

.reveal {
  animation: fadeUp 0.7s ease both;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 900px) {
  .about {
    grid-template-columns: 1fr;
  }

  .bottom-banner {
    grid-template-columns: 1fr;
  }

  .card-link:nth-child(1),
  .card-link:nth-child(2),
  .card-link:nth-child(3) {
    grid-column: 1 / -1;
    margin-top: 0;
  }

  .mini-card:nth-child(2) {
    margin-left: 0;
  }
}

@media (max-width: 768px) {
  .home-page {
    padding-bottom: 48px;
  }

  .hero-content {
    padding-top: 14vh;
  }

  .hero-actions {
    flex-direction: column;
  }

  .hero-actions > * {
    width: 100%;
  }

  .search-bar {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .search-divider {
    display: none;
  }

  .search-input,
  .search-select {
    border: 1px solid rgba(243, 238, 228, 0.35);
    padding: 10px 12px;
  }

  .search-actions {
    width: 100%;
  }

  .search-btn {
    flex: 1;
    justify-content: center;
  }

  .cat-strip {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .cat-item {
    border-left: none;
    border-top: 1px solid var(--color-line);
    padding: 12px 0 0;
  }

  .cat-item:first-child {
    border-top: none;
    padding-top: 0;
  }

  .about,
  .featured,
  .bottom-banner {
    margin-top: 48px;
  }

  .section-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .contact-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

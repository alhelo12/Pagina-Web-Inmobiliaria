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
  { key: 'apartment', label: 'Departamentos', note: 'Ciudad y comodidad' }
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
  await propertyStore.fetchProperties({ status: 'approved', limit: 40 })
  if (authStore.isLogged && authStore.role === 'client') {
    await favoritesStore.fetchFavorites()
  }
})
</script>

<template>
  <main class="home-page">
    <header class="hero reveal">
      <img
        class="hero-image"
        :src="heroImage"
        @error="onHeroImageError"
        alt="Propiedad principal"
      />
      <div class="hero-overlay"></div>

      <div class="hero-content">
        <p class="eyebrow">INICIO PREMIUM</p>
        <h1>HOGARES QUE INSPIRAN TU VIDA</h1>
        <p>
          Explora propiedades reales con diseño, ubicación y valor. Filtra en segundos y descubre la opción ideal para ti.
        </p>
        <div class="hero-actions">
          <RouterLink to="/propiedades" class="cta-primary">Explorar propiedades</RouterLink>
          <RouterLink to="/nosotros" class="cta-outline">Conocer más</RouterLink>
        </div>
        <div class="search-shell">
          <div class="search-bar">
            <input v-model="filters.city" type="text" placeholder="Ciudad" class="search-input search-input-city" />
            <span class="search-divider"></span>
            <select v-model="filters.property_type" class="search-select">
              <option value="">Tipo</option>
              <option value="house">Casa</option>
              <option value="apartment">Departamento</option>
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

      <div class="hero-curve">
        <svg viewBox="0 0 1440 120" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0,60 C480,120 960,0 1440,60 L1440,120 L0,120 Z" fill="#f5f2ec"/>
        </svg>
      </div>
    </header>

    <section class="about reveal">
      <div class="about-img-wrap">
        <img src="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=800&q=80" alt="Habitacion elegante" />
        <button type="button" class="play-btn" aria-label="Reproducir video">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M8 5v14l11-7z" fill="#fff"></path>
          </svg>
        </button>
      </div>
      <div class="about-content">
        <p class="eyebrow">ABOUT US</p>
        <h2>We Can Help You Feel More Comfortable!</h2>
        <p class="about-copy">
          Need a home that reflects elegance and modern style? Explore expertly curated spaces that elevate your lifestyle and bring comfort to every moment.
        </p>
        <article class="rating-card">
          <strong class="rating-value">4.9/5 Rating</strong>
          <p>Trusted by families and investors with a personalized buying experience.</p>
        </article>
        <article class="contact-card">
          <div>
            <small>For More Information, Please Contact Us By Telephone Or Email</small>
            <strong>+598 123 47 509</strong>
          </div>
          <RouterLink class="contact-btn" to="/contacto">CALL US</RouterLink>
        </article>
      </div>
    </section>

    <section class="featured reveal">
      <div class="section-head">
        <h3>Propiedades destacadas</h3>
        <RouterLink to="/propiedades" class="link-all">Ver todas las propiedades</RouterLink>
      </div>

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
        <p class="comfort-label">OUR SERVICES</p>
        <h2>Comfort Are Perfectly Combined Here !</h2>
        <p>
          Special home finder offers premium interior and lifestyle value around your needs. Discover curated residences and personalized support.
        </p>
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
  font-family: 'Poppins', sans-serif;
  background: #f5f2ec;
  color: #07182c;
  padding: 0 0 64px;
  overflow: hidden;
}

.hero {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-width: 1180px;
  margin: 18px auto 0;
  min-height: 640px;
  overflow: hidden;
  background: #07182c;
  border-radius: 22px;
}

.hero-image {
  position: absolute;
  right: 0;
  top: 0;
  width: 55%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  background: linear-gradient(to right, #07182c 0%, transparent 100%);
}

.hero-content {
  position: static;
  z-index: 4;
  max-width: 560px;
  padding: 90px 32px 80px;
  color: #fff;
  grid-column: 1 / 2;
}

.hero-content h1 {
  margin: 0 0 12px;
  font-size: clamp(42px, 5.4vw, 72px);
  line-height: 0.95;
  font-weight: 800;
}

.hero-content p {
  margin: 0;
  max-width: 470px;
  line-height: 1.65;
  color: rgba(255, 255, 255, 0.86);
}

.eyebrow {
  margin: 0 0 14px;
  color: #d8a54d;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 11px;
  font-weight: 700;
}

.hero-actions {
  margin-top: 28px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  width: min(520px, 100%);
}

.cta-primary,
.cta-outline {
  min-height: clamp(46px, 5.4vw, 54px);
  padding: 0 clamp(16px, 2.5vw, 28px);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: clamp(15px, 1.7vw, 16px);
  font-weight: 700;
  text-align: center;
  transition: transform .2s ease, opacity .2s ease;
}

.cta-primary {
  background: #d8a54d;
  color: #07182c;
}

.cta-outline {
  border: 1px solid rgba(255, 255, 255, 0.6);
  color: #fff;
}

.hero-curve {
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  z-index: 2;        /* MENOR que el buscador */
  line-height: 0;
  pointer-events: none;
}

.hero-curve svg {
  width: 100%;
  height: 120px;
  display: block;
}

.cta-primary:hover,
.cta-outline:hover {
  transform: translateY(-2px);
}

.search-shell {
  position: absolute;
  bottom: 100px;
  left: auto;
  right: 8px;
  transform: none;
  width: min(650px, calc(100% - 16px));
  z-index: 5;
}

@media (min-width: 1024px) {
  .hero-actions {
    width: min(500px, 100%);
  }

  .search-shell {
    right: 16px;
    bottom: 540px;
    width: min(700px, calc(100% - 32px));
  }
}

.search-bar {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(10px);
  border-radius: 999px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.22);
  padding: 8px 8px 8px 28px;
  gap: 0;
}

.search-input,
.search-select {
  padding: 10px 4px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-family: 'Poppins', sans-serif;
  color: #07182c;
  min-width: 100px;
  outline: none;
  flex: 1;
}

.search-input::placeholder {
  color: #999;
}

.search-input-city {
  min-width: 130px;
}

.search-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2307182c' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 4px center;
  padding-right: 20px;
}

.search-input:focus,
.search-select:focus {
  box-shadow: 0 0 0 3px rgba(214, 168, 72, 0.18);
}

.search-divider {
  width: 1px;
  height: 32px;
  background: #d8e2f0;
  flex-shrink: 0;
}

input,
select {
  height: 42px;
  border: 1px solid #dfe5ec;
  border-radius: 8px;
  padding: 0 11px;
  font: inherit;
  font-size: 13px;
  background: #fff;
  outline: none;
}

input:focus,
select:focus {
  border-color: #d8a54d;
  box-shadow: 0 0 0 3px rgba(216, 165, 77, 0.18);
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 8px;
}

.search-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #0a355e 0%, #11497d 100%);
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 14px 26px;
  font-weight: 700;
  font-size: 16px;
  white-space: nowrap;
  flex-shrink: 0;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  transition: all .2s ease;
}

.search-btn:hover {
  transform: scale(1.03);
  box-shadow: 0 8px 20px rgba(10, 53, 94, 0.35);
}

.search-reset {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  padding: 0;
  background: #f5f2ec;
  color: #07182c;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: background .2s, transform .2s;
  flex-shrink: 0;
}

.search-reset:hover {
  background: #e8e4dc;
  transform: scale(1.1);
}

.about,
.featured,
.bottom-banner {
  max-width: 1120px;
  margin: 70px auto 0;
}

.about {
  display: grid;
  grid-template-columns: 1fr;
  gap: 28px;
  align-items: center;
}

.about-img-wrap {
  position: relative;
}

.about-img-wrap img {
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: 18px;
  object-fit: cover;
}

.play-btn {
  position: absolute;
  bottom: 24px;
  left: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: #0e6b6b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.play-btn svg {
  width: 20px;
  height: 20px;
}

.about-content h2 {
  margin: 0;
  font-size: clamp(30px, 4vw, 44px);
  line-height: 1.1;
  color: #132846;
}

.about-copy {
  margin: 12px 0 0;
  color: #4d627c;
  line-height: 1.6;
}

.rating-card,
.contact-card {
  background: #f7faff;
  border-radius: 14px;
  margin-top: 14px;
  padding: 16px 20px;
}

.rating-card strong,
.contact-card strong {
  color: #113963;
}

.rating-value {
  color: #d8a54d !important;
}

.rating-card p,
.contact-card small {
  margin: 8px 0 0;
  color: #667c96;
}

.contact-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
}

.contact-btn {
  min-height: 52px;
  padding: 0 28px;
  background: #0a355e;
  color: #fff;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  font-size: 15px;
  font-weight: 700;
}

.featured {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e3e9f2;
  padding: 24px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  margin-bottom: 20px;
}

.section-head h3 {
  margin: 0;
  color: #143057;
  font-size: clamp(24px, 3vw, 36px);
}

.link-all {
  font-size: 12px;
  font-weight: 700;
  color: #7a8da4;
}

.state {
  padding: 12px 0 20px;
  color: #61748c;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
}

.card-link {
  color: inherit;
  transition: transform .22s ease;
}

.card-link:hover {
  transform: translateY(-4px);
}

.bottom-banner {
  background: linear-gradient(120deg, #07182c 0%, #0b2744 100%);
  border-radius: 14px;
  padding: 40px 28px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.banner-copy h2 {
  margin: 0;
  color: #fff;
  line-height: 1.1;
  font-size: clamp(30px, 4vw, 50px);
}

.banner-copy p {
  margin: 14px 0 0;
  color: rgba(255, 255, 255, 0.83);
  max-width: 500px;
}

.banner-cards {
  display: grid;
  gap: 14px;
}

.mini-card {
  border-radius: 14px;
  background: #fff;
  display: grid;
  grid-template-columns: 94px 1fr;
  gap: 12px;
  padding: 10px;
  align-items: center;
}

.mini-card img {
  width: 94px;
  height: 94px;
  border-radius: 10px;
  object-fit: cover;
}

.mini-card strong {
  color: #102c4f;
}

.mini-card small {
  display: block;
  margin-top: 6px;
  color: #6d7f94;
}

.reveal {
  animation: fadeUp .7s ease both;
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

@media (min-width: 860px) {
  .bottom-banner {
    grid-template-columns: 1.1fr .9fr;
    align-items: center;
  }

  .banner-cards {
    justify-self: end;
    width: min(100%, 360px);
  }
}

@media (min-width: 900px) {
  .about {
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }
}

@media (max-width: 1023px) {
  .hero {
    grid-template-columns: 1fr;
    min-height: 700px;
    margin-top: 0;
    border-radius: 0 0 22px 22px;
  }

  .hero-image {
    width: 100%;
    object-position: center;
  }

  .hero-overlay {
    background: linear-gradient(180deg, rgba(7, 24, 44, 0.86) 0%, rgba(7, 24, 44, 0.62) 48%, rgba(7, 24, 44, 0.9) 100%);
  }

  .hero-content {
    max-width: 100%;
    padding: 128px 20px 34px;
  }

  .hero-actions {
    grid-template-columns: 1fr;
    width: 100%;
  }

  .search-shell {
    position: relative;
    bottom: auto;
    right: auto;
    width: 100%;
    max-width: 100%;
    margin-top: 16px;
  }

  .search-bar {
    flex-direction: column;
    border-radius: 16px;
    padding: 12px;
    gap: 8px;
    align-items: stretch;
  }

  .search-divider {
    display: none;
  }

  .search-input,
  .search-select {
    padding: 10px 8px;
    border-bottom: 1px solid #eee;
  }

  .search-actions {
    width: 100%;
    justify-content: center;
    margin-left: 0;
    margin-top: 8px;
    gap: 12px;
  }

  .search-btn {
    flex: 1;
    justify-content: center;
    border-radius: 10px;
    padding: 14px;
  }

  .search-reset {
    width: 46px;
    height: 46px;
  }
}

@media (max-width: 859px) {
  .home-page {
    padding-bottom: 44px;
  }

  .about,
  .featured,
  .bottom-banner {
    margin-top: 30px;
    margin-left: 12px;
    margin-right: 12px;
  }
}

@media (max-width: 620px) {
  .hero {
    min-height: 730px;
  }

  .hero-content {
    padding-top: 140px;
  }

  .hero-content h1 {
    font-size: clamp(34px, 12vw, 46px);
    line-height: 1.02;
  }

  .section-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .contact-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .banner-copy h2 {
    font-size: clamp(28px, 9vw, 42px);
  }
}
</style>


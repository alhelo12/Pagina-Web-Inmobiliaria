<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import Hero from '../components/home/Hero.vue'
import PropertyCard from '@/components/PropertyCard.vue'
import { propertiesApi } from '@/api/properties'
import { favoritesApi } from '@/api/favorites'

const loading = ref(true)
const popularProperties = ref([])
const featuredProperties = ref([])

const highlights = [
  {
    title: 'Budget Friendly',
    text: 'Propiedades bien valoradas con excelente relacion entre ubicacion y precio.'
  },
  {
    title: 'Prime Location',
    text: 'Opciones en zonas con crecimiento y conectividad para inversion inteligente.'
  },
  {
    title: 'Trusted By Clients',
    text: 'Operacion guiada con respaldo juridico y acompanamiento profesional.'
  }
]

const allCount = computed(() => popularProperties.value.length + featuredProperties.value.length)

const normalizeImage = (url) => {
  if (!url) return 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80'
  if (url.startsWith('/media')) return `http://localhost:8000${url}`
  return url
}

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await propertiesApi.getAll({ status: 'approved', limit: 40 })
    const raw = data.properties ?? data.items ?? data ?? []

    const withCounts = await Promise.all(
      raw.map(async (property) => {
        let favoritesCount = 0
        try {
          const { data: favData } = await favoritesApi.getPropertyCount(property.id)
          favoritesCount = favData.favorites_count ?? 0
        } catch {
          favoritesCount = 0
        }

        return {
          ...property,
          favoritesCount,
          image: normalizeImage(property.images?.[0]?.image_url)
        }
      })
    )

    withCounts.sort((a, b) => b.favoritesCount - a.favoritesCount || b.id - a.id)
    popularProperties.value = withCounts.slice(0, 3)

    const usedIds = new Set(popularProperties.value.map((p) => p.id))
    featuredProperties.value = withCounts.filter((p) => !usedIds.has(p.id)).slice(0, 6)
  } catch {
    popularProperties.value = []
    featuredProperties.value = []
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <Hero />

  <section class="home-shell">
    <section class="popular">
      <div class="section-head">
        <span>Popular Properties</span>
        <h2>Propiedades mas destacadas</h2>
      </div>

      <div v-if="loading" class="skeleton-grid">
        <div v-for="n in 3" :key="n" class="skeleton-card"></div>
      </div>

      <div v-else-if="popularProperties.length" class="cards-grid three">
        <RouterLink v-for="p in popularProperties" :key="p.id" :to="`/propiedades/${p.id}`" class="card-link">
          <PropertyCard
            :id="p.id"
            :title="p.title"
            :price="p.price"
            :city="p.city"
            :type="p.property_type"
            :image="p.image"
          />
          <small class="fav-tag">{{ p.favoritesCount }} favoritos</small>
        </RouterLink>
      </div>

      <p v-else class="empty">Aun no hay propiedades aprobadas para mostrar.</p>
    </section>

    <section class="editorial">
      <div class="editorial-media">
        <img src="https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1400&q=80" alt="Interior premium" />
        <img class="floating" src="https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=900&q=80" alt="Casa moderna" />
      </div>

      <div class="editorial-copy">
        <span class="kicker">Why choose us</span>
        <h2>We Provide Latest Properties For Our Valuable Clients</h2>
        <div class="highlight-list">
          <article v-for="item in highlights" :key="item.title">
            <h4>{{ item.title }}</h4>
            <p>{{ item.text }}</p>
          </article>
        </div>
      </div>
    </section>

    <section class="featured">
      <div class="section-head inline">
        <div>
          <span>Featured Properties</span>
          <h2>Mas opciones para explorar</h2>
        </div>
        <RouterLink to="/propiedades" class="see-all">Ver todo</RouterLink>
      </div>

      <div v-if="loading" class="skeleton-grid six">
        <div v-for="n in 6" :key="n" class="skeleton-card small"></div>
      </div>

      <div v-else-if="featuredProperties.length" class="cards-grid six">
        <RouterLink v-for="p in featuredProperties" :key="p.id" :to="`/propiedades/${p.id}`" class="card-link compact">
          <img :src="p.image" :alt="p.title" loading="lazy" />
          <div class="compact-body">
            <h3>{{ p.title }}</h3>
            <p>{{ p.city }} · {{ p.property_type }}</p>
            <strong>${{ Number(p.price).toLocaleString('es-MX') }}</strong>
          </div>
        </RouterLink>
      </div>

      <div v-else class="empty">Cuando existan mas propiedades aprobadas apareceran aqui.</div>
    </section>

    <section v-if="allCount" class="bottom-cta">
      <h3>¿Buscas una propiedad especifica?</h3>
      <p>Explora el catalogo completo y aplica filtros para encontrar tu mejor opcion.</p>
      <RouterLink to="/propiedades">Ir a propiedades</RouterLink>
    </section>
  </section>
</template>

<style scoped>
.home-shell {
  max-width: 1180px;
  margin: 0 auto;
  padding: 74px 24px;
  display: grid;
  gap: 74px;
}

.section-head span,
.kicker {
  display: inline-block;
  color: #d6a848;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .14em;
  font-weight: 800;
  margin-bottom: 10px;
}

.section-head h2,
.editorial-copy h2 {
  margin: 0;
  font-family: Georgia, 'Times New Roman', serif;
  color: #07172d;
  font-size: clamp(30px, 4vw, 46px);
  line-height: 1.08;
}

.cards-grid {
  margin-top: 28px;
  display: grid;
  gap: 20px;
}

.cards-grid.three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.cards-grid.six { grid-template-columns: repeat(3, minmax(0, 1fr)); }

.card-link {
  text-decoration: none;
  color: inherit;
  display: block;
  position: relative;
}

.fav-tag {
  position: absolute;
  left: 12px;
  top: 12px;
  background: rgba(7, 23, 45, .85);
  color: #f2c46d;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 700;
  z-index: 2;
}

.editorial {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px;
  align-items: center;
}

.editorial-media {
  position: relative;
  min-height: 360px;
}

.editorial-media > img {
  width: 78%;
  border-radius: 28px;
  border: 3px solid #ffffff;
  box-shadow: 0 20px 34px rgba(7, 23, 45, .18);
}

.editorial-media .floating {
  position: absolute;
  right: 0;
  bottom: 16px;
  width: 52%;
  border-radius: 22px;
}

.editorial-copy h2 {
  max-width: 560px;
}

.highlight-list {
  margin-top: 22px;
  display: grid;
  gap: 14px;
}

.highlight-list article {
  background: #fffdf8;
  border: 1px solid rgba(7, 23, 45, .08);
  border-radius: 12px;
  padding: 14px;
}

.highlight-list h4 {
  margin: 0 0 6px;
  color: #0f2c4c;
}

.highlight-list p {
  margin: 0;
  color: #667381;
  line-height: 1.6;
}

.section-head.inline {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 14px;
}

.see-all {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  padding: 0 16px;
  border-radius: 8px;
  background: #07172d;
  color: #fff;
  font-weight: 700;
}

.compact {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(7, 23, 45, .08);
  background: #fffdf8;
  box-shadow: 0 10px 24px rgba(7, 23, 45, .08);
}

.compact img {
  width: 100%;
  height: 160px;
  object-fit: cover;
}

.compact-body {
  padding: 12px;
}

.compact-body h3 {
  margin: 0;
  font-size: 16px;
  color: #07172d;
}

.compact-body p {
  margin: 6px 0;
  color: #667381;
  font-size: 13px;
}

.compact-body strong {
  color: #0f2c4c;
}

.bottom-cta {
  text-align: center;
  background: linear-gradient(120deg, #07172d, #0f2c4c);
  color: #fff;
  border-radius: 14px;
  padding: 34px 22px;
}

.bottom-cta h3 { margin: 0 0 8px; font-size: 32px; }
.bottom-cta p { margin: 0 0 16px; color: rgba(255,255,255,.82); }
.bottom-cta a {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  padding: 0 18px;
  border-radius: 8px;
  background: #d6a848;
  color: #07172d;
  font-weight: 800;
}

.empty {
  margin-top: 18px;
  color: #6b7784;
}

.skeleton-grid {
  margin-top: 28px;
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.skeleton-grid.six { grid-template-columns: repeat(3, minmax(0, 1fr)); }

.skeleton-card {
  height: 340px;
  border-radius: 12px;
  background: linear-gradient(90deg, #eee7da 25%, #fffaf1 50%, #eee7da 75%);
  background-size: 300% 100%;
  animation: shimmer 1.4s linear infinite;
}

.skeleton-card.small { height: 250px; }

@keyframes shimmer { to { background-position: -300% 0; } }

@media (max-width: 980px) {
  .cards-grid.three,
  .cards-grid.six,
  .skeleton-grid,
  .skeleton-grid.six,
  .editorial {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 680px) {
  .home-shell { padding: 58px 18px; gap: 54px; }
  .cards-grid.three,
  .cards-grid.six,
  .skeleton-grid,
  .skeleton-grid.six,
  .editorial {
    grid-template-columns: 1fr;
  }

  .editorial-media > img { width: 100%; }
  .editorial-media .floating {
    width: 58%;
    right: 6px;
    bottom: -6px;
  }

  .section-head.inline {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

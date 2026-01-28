<script setup>
import { ref, computed } from 'vue'
import FiltersBar from '@/components/properties/FiltersBar.vue'
import { RouterLink } from 'vue-router'

/* =========================
   FILTROS
========================= */
const filters = ref({
  city: '',
  type: '',
  maxPrice: ''
})

/* =========================
   PROPIEDADES (mock)
========================= */
const properties = ref([
  {
    id: 1,
    price: 2500000,
    title: 'Casa Moderna en Residencial Cerrado',
    city: 'Zona Norte',
    type: 'Casa',
    image: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c'
  },
  {
    id: 2,
    price: 8500,
    title: 'Departamento en Zona Céntrica',
    city: 'Centro Histórico',
    type: 'Departamento',
    image: 'https://images.unsplash.com/photo-1600585152915-d208bec867a1'
  },
  {
    id: 3,
    price: 3700000,
    title: 'Local Comercial en Plaza',
    city: 'Zona Comercial',
    type: 'Local',
    image: 'https://images.unsplash.com/photo-1570129477492-45c003edd2be'
  }
])

/* =========================
   FILTRADO
========================= */
const filteredProperties = computed(() => {
  return properties.value.filter(p => {
    const cityMatch = !filters.value.city || p.city === filters.value.city
    const typeMatch = !filters.value.type || p.type === filters.value.type
    const priceMatch =
      !filters.value.maxPrice || p.price <= Number(filters.value.maxPrice)

    return cityMatch && typeMatch && priceMatch
  })
})

const applyFilters = (data) => {
  filters.value = data
}
</script>

<template>
  <section class="properties">
    <h1>Propiedades</h1>
    <p class="subtitle">
      Descubre nuestra selección de propiedades disponibles
    </p>

    <!-- FILTROS -->
    <FiltersBar @filter="applyFilters" />

    <!-- GRID -->
    <div class="grid">
      <RouterLink
        v-for="property in filteredProperties"
        :key="property.id"
        :to="`/propiedades/${property.id}`"
        class="card-link"
      >
        <div class="card">
          <img :src="property.image" alt="Propiedad" />

          <div class="card-body">
            <h3>{{ property.title }}</h3>
            <p>{{ property.city }} · {{ property.type }}</p>
            <strong>
              ${{ property.price.toLocaleString() }} MXN
            </strong>
          </div>
        </div>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
/* =========================
   CONTENEDOR
========================= */
.properties {
  padding: 60px 40px;
  font-family: 'Poppins', sans-serif;
}

h1 {
  text-align: center;
  font-size: 34px;
  font-weight: 600;
}

.subtitle {
  text-align: center;
  color: #666;
  font-size: 15px;
  margin-bottom: 40px;
}

/* =========================
   GRID
========================= */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}

/* =========================
   ROUTER LINK
========================= */
.card-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

/* =========================
   CARD
========================= */
.card {
  background: white;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(0,0,0,0.08);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-6px);
  box-shadow: 0 18px 40px rgba(0,0,0,0.12);
}

.card img {
  width: 100%;
  height: 220px;
  object-fit: cover;
}

.card-body {
  padding: 18px;
}

.card-body h3 {
  font-size: 17px;
  margin-bottom: 6px;
}

.card-body p {
  font-size: 14px;
  color: #777;
  margin-bottom: 8px;
}

.card-body strong {
  font-size: 16px;
  color: #0d2c54;
}

/* =========================
   RESPONSIVE
========================= */
@media (max-width: 1024px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .properties {
    padding: 40px 20px;
  }

  h1 {
    font-size: 26px;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  .card img {
    height: 180px;
  }
}
</style>

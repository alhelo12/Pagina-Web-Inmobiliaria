<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import properties from '@/data/properties.mock'

const route = useRoute()

const property = computed(() =>
  properties.find(p => p.id === Number(route.params.id))
)
</script>

<template>
  <section v-if="property" class="detail">
    <!-- IMAGEN -->
    <div class="image">
      <img :src="property.image" alt="Propiedad" />
    </div>

    <!-- INFO -->
    <div class="info">
      <h1>{{ property.title }}</h1>
      <p class="location">{{ property.city }} · {{ property.type }}</p>

      <div class="price">
        ${{ property.price.toLocaleString() }} MXN
      </div>

      <p class="description">
        {{ property.description }}
      </p>

      <div class="features">
        <span>🛏 {{ property.bedrooms }} Recámaras</span>
        <span>🛁 {{ property.bathrooms }} Baños</span>
        <span>📐 {{ property.area }} m²</span>
      </div>

<RouterLink to="/contacto" class="btn-contact">
  Contactar asesor
</RouterLink>

    </div>
  </section>

  <p v-else class="not-found">
    Propiedad no encontrada
  </p>
</template>

<style scoped>
.detail {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 40px;
  padding: 60px 40px;
}

.image img {
  width: 100%;
  border-radius: 16px;
  object-fit: cover;
}

.info h1 {
  font-size: 32px;
  margin-bottom: 8px;
}

.location {
  color: #777;
  margin-bottom: 16px;
}

.price {
  font-size: 26px;
  font-weight: 700;
  color: #0d2c54;
  margin-bottom: 20px;
}

.description {
  line-height: 1.6;
  margin-bottom: 20px;
}

.features {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  font-weight: 500;
}

.contact {
  background: #f59e0b;
  border: none;
  color: white;
  padding: 14px 26px;
  border-radius: 10px;
  font-size: 15px;
  cursor: pointer;
}

@media (max-width: 900px) {
  .detail {
    grid-template-columns: 1fr;
    padding: 40px 20px;
  }
}
.btn-contact {
  display: inline-block;
  background: #f59e0b;
  color: white;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s;
}

.btn-contact:hover {
  background: #e6951c;
}

</style>

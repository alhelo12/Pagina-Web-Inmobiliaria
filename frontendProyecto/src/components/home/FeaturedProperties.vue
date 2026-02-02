<script setup>
import { computed } from 'vue'
import PropertyCard from '../PropertyCard.vue'
import properties from '../../data/properties.mock'

// 🔥 Propiedades aleatorias (máx 3)
const featuredProperties = computed(() => {
  if (!properties.length) return []

  const shuffled = [...properties].sort(() => 0.5 - Math.random())
  return shuffled.slice(0, 3)
})
</script>


<template>
  <section class="featured" v-if="featuredProperties.length">
    <h2>Propiedades disponibles</h2>

    <div class="featured-grid">
      <PropertyCard
        v-for="property in featuredProperties"
        :key="property.id"
        v-bind="property"
      />
    </div>
  </section>
</template>
<style scoped>
.featured {
  padding: 80px 20px;
  max-width: 1200px;
  margin: auto;
  text-align: center;
}

.featured-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  margin-top: 30px;
}

/* 💻 Desktop */
@media (min-width: 768px) {
  .featured-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>

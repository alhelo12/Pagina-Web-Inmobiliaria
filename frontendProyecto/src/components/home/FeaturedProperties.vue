<script setup>
import PropertyCard from '../PropertyCard.vue'
import properties from '../../data/properties.mock'
</script>

<template>
  <section class="featured">
    <h2>Propiedades Destacadas</h2>

    <div class="grid">
      <PropertyCard
        v-for="p in properties"
        :key="p.id"
        v-bind="p"
      />
    </div>
  </section>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
</style>

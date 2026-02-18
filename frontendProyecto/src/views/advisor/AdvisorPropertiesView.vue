<script setup>
import { ref } from 'vue'
import PropertyCard from '@/components/PropertyCard.vue'
import { properties } from '@/data/properties'

const list = ref(properties)

const changeStatus = (id, status) => {
  const prop = list.value.find(p => p.id === id)
  if (prop) prop.status = status
}
</script>

<template>
  <div class="advisor">
    <h1>Propiedades pendientes</h1>

    <div class="grid">
      <div v-for="p in list.filter(x => x.status === 'pending')" :key="p.id">
        <PropertyCard v-bind="p" />

        <div class="actions">
          <button @click="changeStatus(p.id, 'approved')">Aprobar</button>
          <button @click="changeStatus(p.id, 'rejected')">Rechazar</button>
          <button @click="changeStatus(p.id, 'sold')">Vendida</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.advisor {
  padding: 40px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

button {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>

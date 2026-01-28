<script setup>
import { ref } from 'vue'

const city = ref('')
const type = ref('')
const maxPrice = ref('')

const emit = defineEmits(['filter'])

const apply = () => {
  emit('filter', {
    city: city.value,
    type: type.value,
    maxPrice: maxPrice.value
  })
}
</script>

<template>
  <div class="filters">
    <select v-model="city">
      <option value="">Ciudad</option>
      <option>Zona Norte</option>
      <option>Centro Histórico</option>
      <option>Zona Comercial</option>
    </select>

    <select v-model="type">
      <option value="">Tipo</option>
      <option>Casa</option>
      <option>Departamento</option>
      <option>Local</option>
    </select>

    <input
      type="number"
      v-model="maxPrice"
      placeholder="Precio máximo"
    />

    <button @click="apply">Filtrar</button>
  </div>
</template>

<style scoped>
.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

select,
input {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

button {
  padding: 10px 20px;
  background: #f5a623;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
</style>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['filter'])

const city  = ref('')
const type  = ref('')
const tx    = ref('')
const maxPrice = ref('')

const apply = () => {
  const params = {}
  if (city.value)     params.city             = city.value
  if (type.value)     params.property_type    = type.value
  if (tx.value)       params.transaction_type = tx.value
  if (maxPrice.value) params.max_price        = Number(maxPrice.value)
  emit('filter', params)
}

const reset = () => {
  city.value = type.value = tx.value = maxPrice.value = ''
  emit('filter', {})
}
</script>

<template>
  <div class="filters">
    <input v-model="city" type="text" placeholder="Ciudad" />

    <select v-model="type">
      <option value="">Tipo de propiedad</option>
      <option value="house">Casa</option>
      <option value="apartment">Departamento</option>
      <option value="land">Terreno</option>
      <option value="commercial">Local comercial</option>
    </select>

    <select v-model="tx">
      <option value="">Operación</option>
      <option value="sale">Venta</option>
      <option value="rent">Renta</option>
    </select>

    <input v-model="maxPrice" type="number" placeholder="Precio máximo" />

    <button class="btn-apply" @click="apply">Buscar</button>
    <button class="btn-reset" @click="reset">Limpiar</button>
  </div>
</template>

<style scoped>
.filters {
  display: flex; gap: 10px; margin-bottom: 30px; flex-wrap: wrap;
}

input, select {
  padding: 10px 12px; border-radius: 8px; border: 1px solid #ddd;
  font-size: 14px; font-family: inherit; min-width: 160px;
}
input:focus, select:focus { outline: none; border-color: #f5a623; }

.btn-apply {
  padding: 10px 20px; background: #f5a623; color: white;
  border: none; border-radius: 8px; cursor: pointer;
  font-weight: 600; font-family: inherit; transition: background .2s;
}
.btn-apply:hover { background: #e69008; }

.btn-reset {
  padding: 10px 16px; background: white; color: #555;
  border: 1px solid #ddd; border-radius: 8px; cursor: pointer;
  font-family: inherit; transition: border-color .2s;
}
.btn-reset:hover { border-color: #aaa; }
</style>

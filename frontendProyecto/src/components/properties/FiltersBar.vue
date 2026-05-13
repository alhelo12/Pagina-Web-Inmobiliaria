<script setup>
import { ref } from 'vue'

const emit = defineEmits(['filter'])

const city  = ref('Tuxtla Gutiérrez')
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
  city.value = 'Tuxtla Gutiérrez'
  type.value = tx.value = maxPrice.value = ''
  emit('filter', {})
}
</script>

<template>
  <div class="filters-wrapper">
    <div class="filters-bar reveal">
      <input v-model="city" type="text" placeholder="Ciudad" class="filter-input" />
      <span class="divider"></span>
      <select v-model="type" class="filter-select">
        <option value="">Tipo</option>
        <option value="house">Casa</option>
        <option value="apartment">Departamento</option>
      </select>
      <span class="divider"></span>
      <select v-model="tx" class="filter-select">
        <option value="">Operación</option>
        <option value="sale">Venta</option>
        <option value="rent">Renta</option>
      </select>
      <span class="divider"></span>
      <input v-model="maxPrice" type="number" placeholder="Precio máx" class="filter-input price-input" />
      <div class="filter-actions">
        <button class="btn-apply" @click="apply">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          Buscar
        </button>
        <button class="btn-reset" @click="reset">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filters-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.filters-bar {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 8px 8px 8px 28px;
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(10px);
  border-radius: 999px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.22);
}

.filter-input,
.filter-select {
  padding: 10px 4px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-family: 'Poppins', sans-serif;
  color: #07182c;
  min-width: 100px;
}

.filter-input::placeholder {
  color: #999;
}

.filter-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2307182c' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 4px center;
  padding-right: 20px;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(214, 168, 72, 0.18);
}

.divider {
  width: 1px;
  height: 32px;
  background: #d8e2f0;
  flex-shrink: 0;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 8px;
}

.btn-apply {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 14px 26px;
  background: linear-gradient(135deg, #0a355e 0%, #11497d 100%);
  color: white;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 700;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
  transition: transform .2s, box-shadow .2s;
  white-space: nowrap;
}

.btn-apply:hover {
  transform: scale(1.03);
  box-shadow: 0 4px 16px rgba(10, 53, 94, 0.35);
}

.btn-reset {
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
}

.btn-reset:hover {
  background: #e8e4dc;
  transform: scale(1.1);
}

@media (max-width: 900px) {
  .filters-wrapper {
    justify-content: flex-start;
  }

  .filters-bar {
    flex-wrap: wrap;
    border-radius: 16px;
    padding: 16px;
    gap: 8px;
    max-width: 100%;
  }

  .filter-input,
  .filter-select {
    flex: 1;
    min-width: calc(50% - 20px);
    padding: 10px 8px;
    border-bottom: 1px solid #eee;
  }

  .price-input {
    min-width: calc(50% - 20px);
  }

  .divider {
    display: none;
  }

  .filter-actions {
    width: 100%;
    justify-content: center;
    margin-left: 0;
    margin-top: 8px;
    gap: 12px;
  }

  .btn-apply {
    flex: 1;
    justify-content: center;
  }

  .btn-reset {
    width: 46px;
    height: 46px;
  }
}
</style>
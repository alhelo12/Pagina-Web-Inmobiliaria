<script setup>
import { computed, ref } from 'vue'
import { enumOptions } from '@/utils/enums'

const emit = defineEmits(['filter'])

const city  = ref('Tuxtla Gutiérrez')
const type  = ref('')
const tx    = ref('')
const maxPrice = ref('')

const typeOptions = computed(() => enumOptions('property_types'))
const txOptions = computed(() => enumOptions('transaction_types'))

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
      <label class="field">
        <span class="field-label">Ciudad</span>
        <input v-model="city" type="text" placeholder="Ciudad" class="filter-input" />
      </label>
      <span class="divider" aria-hidden="true"></span>
      <label class="field">
        <span class="field-label">Tipo</span>
        <select v-model="type" class="filter-select">
          <option value="">Todos</option>
          <option v-for="opt in typeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </label>
      <span class="divider" aria-hidden="true"></span>
      <label class="field">
        <span class="field-label">Operación</span>
        <select v-model="tx" class="filter-select">
          <option value="">Todas</option>
          <option v-for="opt in txOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </label>
      <span class="divider" aria-hidden="true"></span>
      <label class="field">
        <span class="field-label">Precio máx</span>
        <input v-model="maxPrice" type="number" placeholder="—" class="filter-input price-input" />
      </label>
      <div class="filter-actions">
        <button class="btn-apply" @click="apply">Aplicar</button>
        <button class="btn-reset" @click="reset" title="Limpiar filtros" aria-label="Limpiar filtros">
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
  display: block;
  margin: 26px 0 8px;
}

.filters-bar {
  display: flex;
  align-items: flex-end;
  gap: 22px;
  padding: 18px 4px;
  background: transparent;
  border-top: 1px solid var(--color-line);
  border-bottom: 1px solid var(--color-line);
  border-radius: 0;
  box-shadow: none;
}

.field {
  display: grid;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.field-label {
  font-size: 11px;
  letter-spacing: .22em;
  text-transform: uppercase;
  font-weight: 600;
  color: var(--color-brass-deep);
}

.filter-input,
.filter-select {
  width: 100%;
  padding: 9px 2px;
  border: none;
  border-bottom: 1px solid var(--color-line);
  border-radius: 0;
  background: transparent;
  font-size: 15px;
  font-family: var(--sans);
  color: var(--color-ink);
}

.filter-input::placeholder { color: #a8a294; }

.filter-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2397773f' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 2px center;
  padding-right: 20px;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-bottom-color: var(--color-petrol);
}

.divider {
  width: 1px;
  align-self: stretch;
  background: var(--color-line);
  flex-shrink: 0;
  margin-bottom: 4px;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: 6px;
  flex-shrink: 0;
}

.btn-apply {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 13px 34px;
  background: var(--color-petrol);
  color: #fff;
  border: 1px solid var(--color-petrol);
  font-weight: 600;
  font-size: 12px;
  letter-spacing: .16em;
  text-transform: uppercase;
  font-family: var(--sans);
  cursor: pointer;
  transition: background .2s ease;
  white-space: nowrap;
}

.btn-apply:hover { background: var(--color-ink); }

.btn-reset {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  padding: 0;
  background: transparent;
  color: var(--color-petrol);
  border: 1px solid var(--color-line);
  border-radius: 50%;
  cursor: pointer;
  transition: border-color .2s ease, background .2s ease;
}

.btn-reset:hover {
  border-color: var(--color-petrol);
  background: rgba(16, 45, 45, .05);
}

@media (max-width: 900px) {
  .filters-bar {
    flex-wrap: wrap;
    gap: 16px 14px;
    padding: 18px 2px;
  }

  .field { flex: 1 1 calc(50% - 14px); min-width: calc(50% - 14px); }

  .divider { display: none; }

  .filter-actions {
    width: 100%;
    margin-left: 0;
    gap: 12px;
  }

  .btn-apply { flex: 1; }
}
</style>

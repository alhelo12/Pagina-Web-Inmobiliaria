<script setup>
import { ref, computed } from 'vue'
import { usePropertyStore } from '@/stores/propertyStore'
import { storeToRefs } from 'pinia'
import PropertyTable from '@/views/advisor/PropertyTable.vue'




const propertyStore = usePropertyStore()
const { properties } = storeToRefs(propertyStore)

/* ===== FILTRO ACTIVO ===== */
const current = ref('all')

/* ===== CONTADORES ===== */
const counts = computed(() => ({
  all: properties.value.length,
  pending: properties.value.filter(p => p.status === 'pending').length,
  approved: properties.value.filter(p => p.status === 'approved').length,
  rejected: properties.value.filter(p => p.status === 'rejected').length,
  sold: properties.value.filter(p => p.status === 'sold').length
}))

/* ===== LISTA FILTRADA ===== */
const filtered = computed(() => {
  if (current.value === 'all') return properties.value
  return properties.value.filter(p => p.status === current.value)
})

/* ===== ACCIONES ===== */
const approve = (p) => propertyStore.approve(p.id)
const reject = (p) => propertyStore.reject(p.id)
const markSold = (p) => propertyStore.markSold(p.id)

/* ===== TÍTULOS ===== */
const titles = {
  all: 'Todas',
  pending: 'Pendientes',
  approved: 'Aprobadas',
  rejected: 'Rechazadas',
  sold: 'Vendidas'
}

</script>


<template>
  <section class="panel">

    <h1>Panel de Propiedades</h1>

    <!-- ===== BOTONES DE FILTRO ===== -->
<div class="top-filters">
  <button
    v-for="(label, key) in titles"
    :key="key"
    :class="{ active: current === key }"
    @click="current = key"
  >
    {{ label }} ({{ counts[key] }})
  </button>
</div>


    <!-- ===== TABLA ===== -->
<PropertyTable
  v-if="filtered.length"
  :items="filtered"
  @approve="approve"
  @reject="reject"
  @sold="markSold"
/>

<p v-else class="empty">
  No hay propiedades en esta sección.
</p>

  </section>
</template>

<style scoped>
.panel {
  padding: 20px;
}

/* ===== BOTONES ===== */
.top-filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.top-filters button {
  padding: 10px 14px;
  border: none;
  border-radius: 10px;
  background: #eef2f7;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
  white-space: nowrap;
}

.top-filters button.active {
  background: #0d2c54;
  color: white;
}
.empty {
  margin-top: 30px;
  color: #666;
  font-weight: 500;
}

/* ===== TABLA RESPONSIVE ===== */
@media (max-width: 768px) {

  .panel {
    padding: 10px;
  }

  .top-filters {
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 5px;
  }

  .top-filters button {
    flex: 0 0 auto;
    font-size: 14px;
  }

  /* tabla en modo tarjetas */
  :deep(table) {
    display: none;
  }

  :deep(.mobile-cards) {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
}
</style>

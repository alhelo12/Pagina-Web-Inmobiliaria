<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePropertyStore } from '@/stores/propertyStore'
import { storeToRefs } from 'pinia'
import PropertyTable from './PropertyTable.vue'

const store = usePropertyStore()
const { properties, loading, error } = storeToRefs(store)

const current = ref('all')

const counts = computed(() => ({
  all:      properties.value.length,
  pending:  properties.value.filter(p => p.status === 'pending').length,
  approved: properties.value.filter(p => p.status === 'approved').length,
  rejected: properties.value.filter(p => p.status === 'rejected').length,
  sold:     properties.value.filter(p => p.status === 'sold').length
}))

const filtered = computed(() => {
  if (current.value === 'all') return properties.value
  return properties.value.filter(p => p.status === current.value)
})

const titles = {
  all:      'Todas',
  pending:  'Pendientes',
  approved: 'Aprobadas',
  rejected: 'Rechazadas',
  sold:     'Vendidas'
}

// El asesor ve todas las propiedades asignadas a él
onMounted(() => store.fetchProperties())
</script>

<template>
  <section class="panel">
    <h1>Panel de Propiedades</h1>

    <!-- FILTROS -->
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

    <!-- ESTADO -->
    <div v-if="loading" class="state"><div class="spinner"></div></div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <template v-else>
      <PropertyTable
        v-if="filtered.length"
        :items="filtered"
        @approve="store.approve($event.id)"
        @reject="store.reject($event.id)"
        @sold="store.markSold($event.id)"
      />
      <p v-else class="empty">No hay propiedades en esta sección.</p>
    </template>
  </section>
</template>

<style scoped>
.panel { padding: 20px; font-family: 'Poppins', sans-serif; }
h1     { font-size: 26px; margin-bottom: 20px; }

.top-filters { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.top-filters button {
  padding: 10px 14px; border: none; border-radius: 10px;
  background: #eef2f7; cursor: pointer; font-weight: 600;
  transition: .2s; white-space: nowrap; font-family: inherit;
}
.top-filters button.active { background: #0d2c54; color: white; }

.state { display: flex; justify-content: center; padding: 40px; color: #666; }
.error-msg { color: #991b1b; }
.spinner {
  width: 36px; height: 36px; border: 3px solid #f3f3f3;
  border-top-color: #f59e0b; border-radius: 50%; animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty { margin-top: 30px; color: #666; font-weight: 500; }

@media (max-width: 768px) {
  .top-filters { overflow-x: auto; flex-wrap: nowrap; padding-bottom: 5px; }
  .top-filters button { flex: 0 0 auto; font-size: 14px; }
}
</style>

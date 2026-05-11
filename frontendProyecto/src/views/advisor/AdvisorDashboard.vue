<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { usePropertyStore } from '@/stores/propertyStore'
import { storeToRefs } from 'pinia'
import AdvisorDashboardHeader from '@/components/advisor/dashboard/AdvisorDashboardHeader.vue'
import AdvisorMetricCards from '@/components/advisor/dashboard/AdvisorMetricCards.vue'
import AdvisorStatusChart from '@/components/admin/dashboard/AdminStatusChart.vue'
import AdvisorRightPanel from '@/components/advisor/dashboard/AdvisorRightPanel.vue'
import AdvisorRecentList from '@/components/advisor/dashboard/AdvisorRecentList.vue'
import AdvisorAvailablePanel from '@/components/advisor/dashboard/AdvisorAvailablePanel.vue'
import AdvisorRelationshipPanel from '@/components/advisor/AdvisorRelationshipPanel.vue'

const auth = useAuthStore()
const router = useRouter()
const store = usePropertyStore()

const { properties, availableProperties, loading } = storeToRefs(store)

const loadingDashboard = ref(true)
const error = ref('')

const stats = computed(() => store.advisorStats || {
  total: 0, approved: 0, pending: 0, rejected: 0, sold: 0, available_to_take: 0
})

const metrics = computed(() => ({
  total: stats.value.total,
  approved: stats.value.approved,
  pending: stats.value.pending,
  sold: stats.value.sold,
  availableToTake: stats.value.available_to_take,
  clientsCount: stats.value.clients_count
}))

const chartData = computed(() => [
  { label: 'Pendientes', value: stats.value.pending },
  { label: 'Aprobadas', value: stats.value.approved },
  { label: 'Rechazadas', value: stats.value.rejected },
  { label: 'Vendidas', value: stats.value.sold }
])

const myProperties = computed(() => {
  return properties.value.filter(p => p.advisor_id !== null).slice(0, 5)
})

const pendingMyProperties = computed(() => {
  return properties.value.filter(p => p.advisor_id !== null && p.status === 'pending').slice(0, 4)
})

const handleTakeProperty = async (property) => {
  try {
    await store.takeProperty(property.id)
    await store.fetchAdvisorStats()
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al tomar propiedad'
  }
}

onMounted(async () => {
  loadingDashboard.value = true
  error.value = ''
  try {
    await Promise.all([
      store.fetchByAdvisor(),
      store.fetchAvailable(),
      store.fetchAdvisorStats()
    ])
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al cargar el dashboard'
  } finally {
    loadingDashboard.value = false
  }
})
</script>

<template>
  <section class="dashboard">
    <AdvisorDashboardHeader
      eyebrow="Dashboard"
      title="Panel del Asesor"
      :show-add="true"
      add-label="Nueva propiedad"
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Asesor'"
      :profile-email="auth.userEmail || ''"
      @add="router.push('/crear-propiedad')"
    />

    <div v-if="loadingDashboard" class="state">Cargando resumen...</div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <template v-else>
      <AdvisorMetricCards :metrics="metrics" />

      <div class="middle-grid">
        <AdvisorStatusChart :dataset="chartData" />
        <AdvisorRightPanel
          :pending-properties="pendingMyProperties"
          @go-to-properties="router.push('/advisor/panel')"
        />
        <AdvisorRelationshipPanel :clients="[]" :stats="{ appointments: 0 }" />
      </div>

      <div class="overview-grid">
        <AdvisorRecentList :items="myProperties" />
        <AdvisorAvailablePanel @take="handleTakeProperty" />
      </div>
    </template>
  </section>
</template>

<style scoped>
.dashboard { display: grid; gap: 16px; }
.middle-grid { display: grid; gap: 14px; grid-template-columns: 2fr 1fr; }
.overview-grid { display: grid; gap: 14px; grid-template-columns: 1fr 1fr; }
.state { padding: 18px; color: var(--color-muted); background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; }
.error-msg { color: #991b1b; }
@media (max-width: 1050px) {
  .middle-grid,
  .overview-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 700px) {
  .overview-grid { grid-template-columns: 1fr; }
}
</style>
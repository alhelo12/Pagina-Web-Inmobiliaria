<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { usePropertyStore } from '@/stores/propertyStore'
import { storeToRefs } from 'pinia'
import DashboardHeader from '@/components/shared/dashboard/DashboardHeader.vue'
import MetricCards from '@/components/shared/dashboard/MetricCards.vue'
import StatusChart from '@/components/shared/dashboard/StatusChart.vue'
import SidebarPanel from '@/components/shared/dashboard/SidebarPanel.vue'
import RecentList from '@/components/shared/dashboard/RecentList.vue'
import Breadcrumb from '@/components/shared/Breadcrumb.vue'
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

const cardConfig = [
  { key: 'total', label: 'Mis propiedades', sublabel: 'Total asignadas', highlight: false, iconStyle: { background: '#e8edf0', color: 'var(--color-navy-2)' } },
  { key: 'approved', label: 'Aprobadas', sublabel: 'Visibles al público', highlight: false, iconStyle: { background: '#dff7e9', color: '#166534' } },
  { key: 'pending', label: 'Pendientes', sublabel: 'En revisión', highlight: false, iconStyle: { background: '#fff3ce', color: '#856404' } },
  { key: 'sold', label: 'Vendidas', sublabel: 'Cerradas', highlight: true, iconStyle: { background: '#d4edda', color: '#155724' } },
  { key: 'availableToTake', label: 'Disponibles', sublabel: 'Para tomar', highlight: false, iconStyle: { background: '#f7efe0', color: 'var(--color-navy-2)' } },
  { key: 'clientsCount', label: 'Clientes', sublabel: 'Propietarios únicos', highlight: false, iconStyle: { background: '#f0e8fd', color: '#6b21a8' } }
]

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
    await store.fetch({ mode: 'stats' })
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al tomar propiedad'
  }
}

onMounted(async () => {
  loadingDashboard.value = true
  error.value = ''
  try {
    await Promise.all([
      store.fetch({ mode: 'advisor' }),
      store.fetch({ mode: 'available' }),
      store.fetch({ mode: 'stats' })
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
    <DashboardHeader
      eyebrow="Dashboard"
      title="Panel del Asesor"
      :show-add="true"
      add-label="Nueva propiedad"
      :show-profile="true"
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Asesor'"
      :profile-email="auth.userEmail || ''"
      @add="router.push('/advisor/publicar')"
    />

    <Breadcrumb :crumbs="[{ label: 'Dashboard', path: '/advisor/dashboard' }]" />

    <div v-if="loadingDashboard" class="state">Cargando resumen...</div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <template v-else>
      <MetricCards :cards="cardConfig" :metrics="metrics" />

      <div class="middle-grid">
        <StatusChart :dataset="chartData" />

        <SidebarPanel title="Próximas acciones">
          <div v-if="pendingMyProperties.length" class="actions-list">
            <div v-for="p in pendingMyProperties" :key="p.id" class="action-item">
              <div class="action-info">
                <strong>{{ p.title }}</strong>
                <span>{{ p.city || 'Sin ciudad' }}</span>
                <small>${{ Number(p.price || 0).toLocaleString('es-MX') }}</small>
              </div>
            </div>
          </div>
          <p v-else class="empty">No hay acciones pendientes</p>

          <button class="review-btn" @click="router.push('/advisor/panel')">
            Revisar propiedades
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
          </button>
        </SidebarPanel>

        <AdvisorRelationshipPanel :clients="[]" :stats="{ appointments: 0 }" />
      </div>

      <div class="overview-grid">
        <RecentList
          subtitle="Mis propiedades"
          title="Recientes"
          :items="myProperties"
          :show-status="true"
          :show-price="false"
          empty-text="No tienes propiedades aún."
        />

        <article class="available-card">
          <div class="available-head">
            <p>Nuevas</p>
            <h3>Disponibles para tomar</h3>
          </div>

          <div v-if="availableProperties?.length" class="available-list">
            <div v-for="p in availableProperties" :key="p.id" class="available-row">
              <div class="available-thumb-wrap">
                <img
                  :src="(p.images?.find(i => i.is_main) ?? p.images?.[0])?.image_url ?? ''"
                  :alt="p.title"
                  class="available-thumb"
                  @error="(e) => { e.target.src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgdmlld0JveD0iMCAwIDY0IDY0IiBzdHlsZT0iZGlzcGxheTpibG9jazsiIGNsYXNzPSJhIiBmaWxsPSIjZWRlY2VkIj48cmVjdCB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHJ4PSIxMiIgc3R5bGU9ImZpbGw6I2VkZWNlZCIgc3BhY2Y9Im5vbmUiLz48cGF0aCBkPSJNMjIgMzZoMjBjLTEuMSAwLTIgLjktMiAyIDAgMS4xLjkgMiAyIDIgMCAxLjEtLjkgMi0yIDJoLTIwYzEuMSAwIDItLjkgMi0yIDAtMS4xLS45LTItMi0yeiIgZmlsbD0iI2RkYzJkNSIvPjwvc3ZnPg==' }"
                />
              </div>
              <div class="available-info">
                <strong>{{ p.title }}</strong>
                <span>{{ p.city || 'Sin ciudad' }}</span>
              </div>
              <small>${{ Number(p.price || 0).toLocaleString('es-MX') }}</small>
              <button class="take-btn" @click="handleTakeProperty(p)">Tomar</button>
            </div>
          </div>
          <p v-else class="empty">No hay propiedades disponibles.</p>
        </article>
      </div>
    </template>
  </section>
</template>

<style scoped>
.dashboard { display: grid; gap: 16px; max-width: 1400px; width: 100%; }
.middle-grid { display: grid; gap: 14px; grid-template-columns: 2fr 1fr; }
.overview-grid { display: grid; gap: 14px; grid-template-columns: 1fr 1fr; }
.middle-grid > *, .overview-grid > * { min-width: 0; }
.state { padding: 18px; color: var(--color-muted); background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; }
.error-msg { color: #991b1b; }
.empty { margin: 0; color: var(--color-muted); }
.actions-list { display: flex; flex-direction: column; gap: 10px; flex: 1; }
.action-item { padding: 12px; border-radius: 8px; background: #faf9f7; border: 1px solid var(--color-line); }
.action-info { min-width: 0; }
.action-info strong { display: block; color: var(--color-navy); font-size: 14px; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.action-info span { display: block; color: var(--color-muted); font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.action-info small { display: block; color: var(--color-navy); font-weight: 700; font-size: 13px; margin-top: 4px; }
.review-btn { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 16px; padding: 12px 16px; border-radius: 8px; background: var(--color-navy); color: #fff; font-weight: 700; font-size: 14px; border: none; cursor: pointer; transition: .2s; width: 100%; }
.review-btn:hover { filter: brightness(1.1); }
.available-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
.available-head { margin-bottom: 12px; display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; flex-wrap: wrap; }
.available-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.available-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; min-width: 0; }
.available-list { display: grid; gap: 10px; }
.available-row { display: grid; grid-template-columns: auto minmax(0, 1fr) auto auto; align-items: center; column-gap: 12px; row-gap: 8px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--color-line); background: #fff; }
.available-thumb-wrap { flex-shrink: 0; width: 52px; height: 52px; border-radius: 8px; overflow: hidden; background: #f0ece4; }
.available-thumb { width: 100%; height: 100%; object-fit: cover; }
.available-info { flex: 1; min-width: 0; }
.available-info strong { display: block; color: var(--color-navy); font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.available-info span { display: block; margin-top: 4px; color: var(--color-muted); font-size: 12px; }
.available-row small { color: var(--color-navy-2); font-weight: 700; white-space: nowrap; }
.take-btn { padding: 6px 12px; border-radius: 6px; background: var(--color-gold); color: var(--color-navy); font-weight: 600; font-size: 12px; border: none; cursor: pointer; transition: .2s; }
.take-btn:hover { filter: brightness(1.05); }
@media (max-width: 1050px) {
  .middle-grid { grid-template-columns: 1fr; }
  .overview-grid { grid-template-columns: 1fr; }
}
@media (max-width: 700px) {
  .middle-grid, .overview-grid { grid-template-columns: 1fr; }
}
</style>

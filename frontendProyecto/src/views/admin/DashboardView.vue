<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { propertiesApi } from '@/api/properties'
import { usersApi } from '@/api/users'
import DashboardHeader from '@/components/shared/dashboard/DashboardHeader.vue'
import MetricCards from '@/components/shared/dashboard/MetricCards.vue'
import StatusChart from '@/components/shared/dashboard/StatusChart.vue'
import SidebarPanel from '@/components/shared/dashboard/SidebarPanel.vue'
import RecentList from '@/components/shared/dashboard/RecentList.vue'
import ActivityFeed from '@/components/shared/dashboard/ActivityFeed.vue'
import Breadcrumb from '@/components/shared/Breadcrumb.vue'

const auth = useAuthStore()
const router = useRouter()

const loading = ref(true)
const error = ref('')

const summary = ref({
  total: 0, approved: 0, pending: 0, rejected: 0, sold: 0, average_price: 0
})
const recentProperties = ref([])
const pendingProperties = ref([])
const userStats = ref({ total_users: 0, active_users: 0, advisors_count: 0, clients_count: 0 })
const recentActivity = ref([])

const cardConfig = [
  { key: 'total', label: 'Total propiedades', sublabel: 'En toda la plataforma', highlight: false, iconStyle: { background: '#e8edf0', color: 'var(--color-navy-2)' } },
  { key: 'approved', label: 'Aprobadas', sublabel: 'Disponibles al público', highlight: false, iconStyle: { background: '#dff7e9', color: '#166534' } },
  { key: 'pending', label: 'Pendientes', sublabel: 'En revisión', highlight: false, iconStyle: { background: '#fff3ce', color: '#856404' } },
  { key: 'approvalRate', label: 'Tasa aprobación', sublabel: 'Rendimiento general', highlight: true, iconStyle: { background: '#f7efe0', color: 'var(--color-navy-2)' } },
  { key: 'totalUsers', label: 'Total usuarios', sublabel: 'Registrados en plataforma', highlight: false, iconStyle: { background: '#e8edf0', color: 'var(--color-navy-2)' } },
  { key: 'activeAdvisors', label: 'Asesores', sublabel: 'Publicando propiedades', highlight: false, iconStyle: { background: '#f0e8fd', color: '#6b21a8' } }
]

const metrics = computed(() => ({
  total: summary.value.total,
  approved: summary.value.approved,
  pending: summary.value.pending,
  approvalRate: summary.value.total
    ? Math.round((summary.value.approved / summary.value.total) * 100)
    : 0,
  totalUsers: userStats.value.total_users,
  activeAdvisors: userStats.value.advisors_count
}))

const chartData = computed(() => [
  { label: 'Pendientes', value: summary.value.pending },
  { label: 'Aprobadas', value: summary.value.approved },
  { label: 'Rechazadas', value: summary.value.rejected },
  { label: 'Vendidas', value: summary.value.sold }
])

const avgPrice = computed(() =>
  summary.value.average_price
    ? Math.round(summary.value.average_price).toLocaleString('es-MX')
    : '0'
)

const sidebarItems = computed(() => [
  { key: 'sold', label: 'Vendidas', value: summary.value.sold },
  { key: 'rejected', label: 'Rechazadas', value: summary.value.rejected },
  { key: 'avgPrice', label: 'Precio promedio', value: `$${avgPrice.value}` }
])

const formatRelativeTime = (timestamp) => {
  if (!timestamp) return ''
  const diff = Date.now() - new Date(timestamp).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'hace un momento'
  if (mins < 60) return `hace ${mins} min`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `hace ${hrs}h`
  const days = Math.floor(hrs / 24)
  if (days < 30) return `hace ${days}d`
  return new Date(timestamp).toLocaleDateString('es-MX', { day: '2-digit', month: 'short' })
}

const getPropertyImage = (property) => {
  const img = property.images?.find(i => i.is_main) ?? property.images?.[0]
  if (img) {
    const url = img.image_url ?? img.url
    if (!url) return null
    if (/^(https?:|blob:|data:)/.test(url)) return url
    const base = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
    return `${base}${url.startsWith('/') ? '' : '/'}${url}`
  }
  return null
}

const propertyFallback = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgdmlld0JveD0iMCAwIDY0IDY0IiBzdHlsZT0iZGlzcGxheTpibG9jazsiIGNsYXNzPSJhIiBmaWxsPSIjZWRlY2VkIj48cmVjdCB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHJ4PSIxMiIgc3R5bGU9ImZpbGw6I2VkZWNlZCIgc3BhY2Y9Im5vbmUiLz48cGF0aCBkPSJNMjIgMzZoMjBjLTEuMSAwLTIgLjktMiAyIDAgMS4xLjkgMiAyIDIgMCAxLjEtLjkgMi0yIDJoLTIwYzEuMSAwIDItLjkgMi0yIDAtMS4xLS45LTItMi0yeiIgZmlsbD0iI2RkYzJkNSIvPjwvc3ZnPg=='

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const [sumRes, recentRes, pendingRes, userStatsRes, activityRes] = await Promise.all([
      propertiesApi.getSummary(),
      propertiesApi.getAll({ limit: 5 }),
      propertiesApi.getPending({ limit: 5 }),
      usersApi.getStats(),
      usersApi.getRecentActivity({ limit: 10 })
    ])
    summary.value = sumRes.data
    recentProperties.value = recentRes.data.properties ?? recentRes.data.items ?? []
    pendingProperties.value = pendingRes.data.properties ?? pendingRes.data.items ?? []
    userStats.value = userStatsRes.data
    recentActivity.value = activityRes.data
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al cargar el dashboard'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="dashboard">
    <DashboardHeader
      eyebrow="Dashboard"
      title="Panel Administrativo"
      :show-profile="true"
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Admin'"
      :profile-email="auth.userEmail || ''"
    />

    <Breadcrumb :crumbs="[{ label: 'Panel', path: '/admin/dashboard' }]" />

    <div v-if="loading" class="state">Cargando resumen...</div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <template v-else>
      <MetricCards :cards="cardConfig" :metrics="metrics" />

      <div class="middle-grid">
        <StatusChart :dataset="chartData" />
        <SidebarPanel title="Resumen rápido" :items="sidebarItems" />
      </div>

      <div class="overview-grid">
        <RecentList
          title="Propiedades recientes"
          :items="recentProperties"
          :show-price="true"
          :show-status="false"
          empty-text="Sin propiedades recientes."
        />

        <ActivityFeed
          title="Actividad reciente"
          subtitle="Admin"
          :items="recentActivity.map(a => ({ id: a.id, icon: a.icon, title: a.message, message: '', timestamp: a.timestamp }))"
          empty-text="Sin actividad reciente."
        />

        <article class="review-card">
          <div class="review-head">
            <div>
              <p>Revisión</p>
              <h3>Pendientes por revisar</h3>
            </div>
            <button @click="router.push('/admin/propiedades')">Ver tabla</button>
          </div>

          <div v-if="pendingProperties.length" class="review-list">
            <div v-for="property in pendingProperties" :key="property.id" class="review-row">
              <div class="review-thumb-wrap">
                <img
                  :src="getPropertyImage(property) || propertyFallback"
                  :alt="property.title"
                  class="review-thumb"
                  @error="(e) => { e.target.src = propertyFallback }"
                />
              </div>
              <div>
                <strong>{{ property.title }}</strong>
                <span>{{ property.city || 'Sin ciudad' }}</span>
              </div>
              <small>${{ Number(property.price || 0).toLocaleString('es-MX') }}</small>
            </div>
          </div>

          <p v-else class="empty">No hay propiedades pendientes.</p>
        </article>
      </div>
    </template>
  </section>
</template>

<style scoped>
.dashboard { display: grid; gap: 16px; max-width: 1400px; width: 100%; }
.middle-grid { display: grid; gap: 14px; grid-template-columns: 2fr 1fr; }
.overview-grid { display: grid; gap: 14px; grid-template-columns: 1fr 1fr 1fr; }
.middle-grid > *, .overview-grid > * { min-width: 0; }
.state { padding: 18px; color: var(--color-muted); background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; }
.error-msg { color: #991b1b; }
.review-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
.review-head { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 12px; }
.review-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.review-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; }
.review-head button { min-height: 38px; padding: 0 14px; border-radius: 8px; background: var(--color-navy); color: #fff; font-weight: 700; border: none; cursor: pointer; }
.review-list { display: grid; gap: 10px; }
.review-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--color-line); background: #fff; }
.review-row strong { display: block; color: var(--color-navy); font-size: 14px; }
.review-row span { display: block; margin-top: 4px; color: var(--color-muted); font-size: 12px; }
.review-thumb-wrap { flex-shrink: 0; width: 52px; height: 52px; border-radius: 8px; overflow: hidden; background: #f0ece4; }
.review-thumb { width: 100%; height: 100%; object-fit: cover; }
.review-row small { color: var(--color-navy-2); font-weight: 700; white-space: nowrap; }
.empty { margin: 0; color: var(--color-muted); }
@media (max-width: 1050px) {
  .middle-grid, .overview-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 700px) {
  .middle-grid, .overview-grid { grid-template-columns: 1fr; }
}
</style>

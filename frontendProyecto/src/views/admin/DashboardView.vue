<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { propertiesApi } from '@/api/properties'
import { usersApi } from '@/api/users'
import AdminDashboardHeader from '@/components/admin/dashboard/AdminDashboardHeader.vue'
import AdminMetricCards from '@/components/admin/dashboard/AdminMetricCards.vue'
import AdminStatusChart from '@/components/admin/dashboard/AdminStatusChart.vue'
import AdminRightPanel from '@/components/admin/dashboard/AdminRightPanel.vue'
import AdminRecentList from '@/components/admin/dashboard/AdminRecentList.vue'
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

const formatPrice = (price) => Number(price || 0).toLocaleString('es-MX')

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
</script>

<template>
  <section class="dashboard">
    <AdminDashboardHeader
      eyebrow="Dashboard"
      title="Panel Administrativo"
      :show-search="false"
      :show-export="false"
      add-label="Nueva propiedad"
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Admin'"
      :profile-email="auth.userEmail || ''"
      @add="router.push('/crear-propiedad')"
    />

    <Breadcrumb :crumbs="[{ label: 'Panel', path: '/admin/dashboard' }]" />

    <div v-if="loading" class="state">Cargando resumen...</div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <template v-else>
      <AdminMetricCards :metrics="metrics" />

      <div class="middle-grid">
        <AdminStatusChart :dataset="chartData" />
        <AdminRightPanel :sold="summary.sold" :rejected="summary.rejected" :avg-price="avgPrice" />
      </div>

      <div class="overview-grid">
        <AdminRecentList :items="recentProperties" />

        <article class="activity-card">
          <div class="activity-head">
            <p>Admin</p>
            <h3>Actividad reciente</h3>
          </div>
          <div v-if="recentActivity.length" class="activity-list">
            <div v-for="a in recentActivity" :key="a.id" class="activity-row">
              <span class="activity-icon">{{ a.icon }}</span>
              <div class="activity-body">
                <p>{{ a.message }}</p>
                <small>{{ formatRelativeTime(a.timestamp) }}</small>
              </div>
            </div>
          </div>
          <p v-else class="empty">Sin actividad reciente.</p>
        </article>

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
.state { padding: 18px; color: var(--color-muted); background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; }
.error-msg { color: #991b1b; }
.activity-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
.activity-head { margin-bottom: 12px; }
.activity-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.activity-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; }
.activity-list { display: grid; gap: 8px; }
.activity-row { display: flex; align-items: flex-start; gap: 10px; padding: 8px 10px; border-radius: 8px; border: 1px solid var(--color-line); background: #fff; }
.activity-icon { font-size: 18px; flex-shrink: 0; margin-top: 1px; }
.activity-body { flex: 1; min-width: 0; }
.activity-body p { margin: 0 0 2px; color: var(--color-navy); font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.activity-body small { color: var(--color-muted); font-size: 11px; }
.review-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
.review-head { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 12px; }
.review-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.review-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; }
.review-head button { min-height: 38px; padding: 0 14px; border-radius: 8px; background: var(--color-navy); color: #fff; font-weight: 700; }
.review-list { display: grid; gap: 10px; }
.review-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--color-line); background: #fff; }
.review-row strong { display: block; color: var(--color-navy); font-size: 14px; }
.review-row span { display: block; margin-top: 4px; color: var(--color-muted); font-size: 12px; }
.review-thumb-wrap { flex-shrink: 0; width: 52px; height: 52px; border-radius: 8px; overflow: hidden; background: #f0ece4; }
.review-thumb { width: 100%; height: 100%; object-fit: cover; }
.review-row small { color: var(--color-navy-2); font-weight: 700; white-space: nowrap; }
.empty { margin: 0; color: var(--color-muted); }
@media (max-width: 1050px) {
  .middle-grid,
  .overview-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 700px) {
  .middle-grid,
  .overview-grid { grid-template-columns: 1fr; }
}
</style>

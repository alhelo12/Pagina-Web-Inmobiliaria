<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { propertiesApi } from '@/api/properties'
import AdminDashboardHeader from '@/components/admin/dashboard/AdminDashboardHeader.vue'
import AdminMetricCards from '@/components/admin/dashboard/AdminMetricCards.vue'
import AdminStatusChart from '@/components/admin/dashboard/AdminStatusChart.vue'
import AdminRightPanel from '@/components/admin/dashboard/AdminRightPanel.vue'
import AdminRecentList from '@/components/admin/dashboard/AdminRecentList.vue'

const auth = useAuthStore()
const router = useRouter()

const loading = ref(true)
const error = ref('')

const summary = ref({
  total: 0, approved: 0, pending: 0, rejected: 0, sold: 0, average_price: 0
})
const recentProperties = ref([])
const pendingProperties = ref([])

const metrics = computed(() => ({
  total: summary.value.total,
  approved: summary.value.approved,
  pending: summary.value.pending,
  approvalRate: summary.value.total
    ? Math.round((summary.value.approved / summary.value.total) * 100)
    : 0
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

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const [sumRes, recentRes, pendingRes] = await Promise.all([
      propertiesApi.getSummary(),
      propertiesApi.getAll({ limit: 5 }),
      propertiesApi.getPending({ limit: 5 })
    ])
    summary.value = sumRes.data
    recentProperties.value = recentRes.data.properties ?? recentRes.data.items ?? []
    pendingProperties.value = pendingRes.data.properties ?? pendingRes.data.items ?? []
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al cargar el dashboard'
  } finally {
    loading.value = false
  }
})
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
.dashboard { display: grid; gap: 16px; }
.middle-grid { display: grid; gap: 14px; grid-template-columns: 2fr 1fr; }
.overview-grid { display: grid; gap: 14px; grid-template-columns: 1.1fr 1fr; }
.state { padding: 18px; color: var(--color-muted); background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; }
.error-msg { color: #991b1b; }
.review-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
.review-head { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 12px; }
.review-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.review-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; }
.review-head button { min-height: 38px; padding: 0 14px; border-radius: 8px; background: var(--color-navy); color: #fff; font-weight: 700; }
.review-list { display: grid; gap: 10px; }
.review-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--color-line); background: #fff; }
.review-row strong { display: block; color: var(--color-navy); font-size: 14px; }
.review-row span { display: block; margin-top: 4px; color: var(--color-muted); font-size: 12px; }
.review-row small { color: var(--color-navy-2); font-weight: 700; white-space: nowrap; }
.empty { margin: 0; color: var(--color-muted); }
@media (max-width: 1050px) {
  .middle-grid,
  .overview-grid { grid-template-columns: 1fr; }
}
</style>

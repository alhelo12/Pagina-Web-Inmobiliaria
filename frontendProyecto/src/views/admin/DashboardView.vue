<script setup>
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { usePropertyStore } from '@/stores/propertyStore'
import AdminDashboardHeader from '@/components/admin/dashboard/AdminDashboardHeader.vue'
import AdminMetricCards from '@/components/admin/dashboard/AdminMetricCards.vue'
import AdminStatusChart from '@/components/admin/dashboard/AdminStatusChart.vue'
import AdminRightPanel from '@/components/admin/dashboard/AdminRightPanel.vue'
import AdminRecentList from '@/components/admin/dashboard/AdminRecentList.vue'

const store = usePropertyStore()
const auth = useAuthStore()
const router = useRouter()
const { properties, loading, error } = storeToRefs(store)

const metrics = computed(() => {
  const total = properties.value.length
  const approved = properties.value.filter(p => p.status === 'approved').length
  const pending = properties.value.filter(p => p.status === 'pending').length
  return {
    total,
    approved,
    pending,
    approvalRate: total ? Math.round((approved / total) * 100) : 0
  }
})

const chartData = computed(() => [
  { label: 'Pendientes', value: properties.value.filter(p => p.status === 'pending').length },
  { label: 'Aprobadas', value: properties.value.filter(p => p.status === 'approved').length },
  { label: 'Rechazadas', value: properties.value.filter(p => p.status === 'rejected').length },
  { label: 'Vendidas', value: properties.value.filter(p => p.status === 'sold').length }
])

const avgPrice = computed(() => {
  if (!properties.value.length) return '0'
  const sum = properties.value.reduce((acc, p) => acc + Number(p.price || 0), 0)
  return Math.round(sum / properties.value.length).toLocaleString('es-MX')
})

const recent = computed(() => [...properties.value].sort((a, b) => b.id - a.id).slice(0, 5))
const pendingReview = computed(() => properties.value.filter(p => p.status === 'pending').slice(0, 5))

onMounted(() => store.fetchProperties())
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
        <AdminRightPanel :sold="chartData[3].value" :rejected="chartData[2].value" :avg-price="avgPrice" />
      </div>

      <div class="overview-grid">
        <AdminRecentList :items="recent" />

        <article class="review-card">
          <div class="review-head">
            <div>
              <p>Revisión</p>
              <h3>Pendientes por revisar</h3>
            </div>
            <button @click="router.push('/admin/propiedades')">Ver tabla</button>
          </div>

          <div v-if="pendingReview.length" class="review-list">
            <div v-for="property in pendingReview" :key="property.id" class="review-row">
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

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePropertyStore } from '@/stores/propertyStore'
import { useAuthStore } from '@/stores/authStore'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import AdminDashboardHeader from '@/components/admin/dashboard/AdminDashboardHeader.vue'
import AdminMetricCards from '@/components/admin/dashboard/AdminMetricCards.vue'
import AdminStatusChart from '@/components/admin/dashboard/AdminStatusChart.vue'
import AdminRightPanel from '@/components/admin/dashboard/AdminRightPanel.vue'
import AdminRecentList from '@/components/admin/dashboard/AdminRecentList.vue'

const store = usePropertyStore()
const auth = useAuthStore()
const router = useRouter()
const { properties, loading, error } = storeToRefs(store)
const filter = ref('todos')
const search = ref('')

const statusMap = {
  pending: { label: 'Pendiente', cls: 'pendiente' },
  approved: { label: 'Aprobada', cls: 'aprobada' },
  rejected: { label: 'Rechazada', cls: 'rechazada' },
  sold: { label: 'Vendida', cls: 'vendida' }
}

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

const filtered = computed(() => {
  const byStatus = filter.value === 'todos' ? properties.value : properties.value.filter(p => p.status === filter.value)
  const q = search.value.trim().toLowerCase()
  if (!q) return byStatus
  return byStatus.filter(p => p.title?.toLowerCase().includes(q) || p.city?.toLowerCase().includes(q))
})

const recent = computed(() => [...properties.value].sort((a, b) => b.id - a.id).slice(0, 5))

const confirm = async (action, id) => {
  if (!window.confirm('Confirmas esta accion?')) return
  await store[action](id)
  await store.fetchProperties({ user_id: auth.userId })
}

const exportJson = () => {
  const blob = new Blob([JSON.stringify(filtered.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'propiedades.json'
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => store.fetchProperties({ user_id: auth.userId }))
</script>

<template>
  <section class="dashboard">
    <AdminDashboardHeader
      v-model:search="search"
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Admin'"
      :profile-email="auth.userEmail || ''"
      @add="router.push('/crear-propiedad')"
      @export="exportJson"
    />

    <AdminMetricCards :metrics="metrics" />

    <div class="middle-grid">
      <AdminStatusChart :dataset="chartData" />
      <AdminRightPanel :sold="chartData[3].value" :rejected="chartData[2].value" :avg-price="avgPrice" />
    </div>

    <div class="bottom-grid">
      <AdminRecentList :items="recent" />

      <article class="table-card">
        <div class="filters">
          <button :class="{ active: filter === 'todos' }" @click="filter = 'todos'">Todos</button>
          <button :class="{ active: filter === 'pending' }" @click="filter = 'pending'">Pendientes</button>
          <button :class="{ active: filter === 'approved' }" @click="filter = 'approved'">Aprobadas</button>
          <button :class="{ active: filter === 'rejected' }" @click="filter = 'rejected'">Rechazadas</button>
          <button :class="{ active: filter === 'sold' }" @click="filter = 'sold'">Vendidas</button>
        </div>

        <div v-if="loading" class="state">Cargando...</div>
        <div v-else-if="error" class="state error-msg">{{ error }}</div>

        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Titulo</th><th>Ciudad</th><th>Precio</th><th>Estado</th><th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in filtered" :key="p.id">
                <td class="td-title">{{ p.title }}</td>
                <td>{{ p.city }}</td>
                <td>${{ Number(p.price).toLocaleString('es-MX') }}</td>
                <td><span :class="['badge', statusMap[p.status]?.cls]">{{ statusMap[p.status]?.label ?? p.status }}</span></td>
                <td class="actions">
                  <button v-if="p.status === 'pending'" class="approve" @click="confirm('approve', p.id)">Aprobar</button>
                  <button v-if="p.status === 'pending'" class="reject" @click="confirm('reject', p.id)">Rechazar</button>
                  <button v-if="p.status === 'approved'" class="sold" @click="confirm('markSold', p.id)">Vendida</button>
                  <button class="delete" @click="confirm('remove', p.id)">Eliminar</button>
                </td>
              </tr>
              <tr v-if="!filtered.length">
                <td colspan="5" class="empty">Sin propiedades</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.dashboard { display: grid; gap: 16px; }
.middle-grid { display: grid; gap: 14px; grid-template-columns: 2fr 1fr; }
.bottom-grid { display: grid; gap: 14px; grid-template-columns: 1.2fr 2fr; }
.table-card { background: #fff; border: 1px solid #e6edf8; border-radius: 14px; box-shadow: 0 10px 26px rgba(15, 23, 42, 0.07); padding: 16px; }
.filters { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.filters button { border: 1px solid #dbe3f0; background: #fff; padding: 7px 12px; border-radius: 999px; font-weight: 700; color: #334155; transition: .3s ease; }
.filters button.active, .filters button:hover { background: #2563eb; color: #fff; border-color: #2563eb; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; border-bottom: 1px solid #edf2fb; font-size: 14px; text-align: left; }
th { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: .08em; }
.td-title { color: #0f172a; font-weight: 700; }
.badge { padding: 5px 9px; border-radius: 999px; font-size: 12px; font-weight: 800; }
.pendiente { background: #fff3ce; color: #8a5a00; }
.aprobada { background: #dff7e9; color: #166534; }
.rechazada { background: #fee2e2; color: #991b1b; }
.vendida { background: #e4ecff; color: #243f86; }
.actions { display: flex; gap: 6px; flex-wrap: wrap; }
.actions button { border: none; border-radius: 7px; padding: 6px 9px; font-size: 12px; font-weight: 800; transition: .3s ease; }
.actions button:hover { filter: brightness(1.02); transform: translateY(-1px); }
.approve { background: #dff7e9; color: #166534; }
.reject { background: #fee2e2; color: #991b1b; }
.sold { background: #e4ecff; color: #243f86; }
.delete { background: #0f172a; color: #fff; }
.state { padding: 16px 0; color: #64748b; }
.error-msg { color: #991b1b; }
.empty { text-align: center; color: #94a3b8; }
@media (max-width: 1050px) { .middle-grid, .bottom-grid { grid-template-columns: 1fr; } }
</style>

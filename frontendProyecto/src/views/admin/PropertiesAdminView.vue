<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { usePropertyStore } from '@/stores/propertyStore'
import AdminDashboardHeader from '@/components/admin/dashboard/AdminDashboardHeader.vue'

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

const filtered = computed(() => {
  const byStatus = filter.value === 'todos' ? properties.value : properties.value.filter(p => p.status === filter.value)
  const q = search.value.trim().toLowerCase()
  if (!q) return byStatus
  return byStatus.filter(p => p.title?.toLowerCase().includes(q) || p.city?.toLowerCase().includes(q))
})

const ownerName = (property) => property.owner?.full_name || `Usuario #${property.submitted_by_user_id}`
const ownerEmail = (property) => property.owner?.email || 'Sin correo'
const formatRegisteredAt = (value) => {
  if (!value) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(new Date(value))
}

const confirm = async (action, id) => {
  if (!window.confirm('¿Confirmas esta acción?')) return
  await store[action](id)
  await store.fetchProperties()
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

onMounted(() => store.fetchProperties())
</script>

<template>
  <section class="properties-admin">
    <AdminDashboardHeader
      v-model:search="search"
      eyebrow="Gestión inmobiliaria"
      title="Propiedades"
      add-label="Agregar propiedad"
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Admin'"
      :profile-email="auth.userEmail || ''"
      @add="router.push('/crear-propiedad')"
      @export="exportJson"
    />

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
              <th>Título</th><th>Registrado por</th><th>Registrada</th><th>Ciudad</th><th>Precio</th><th>Estado</th><th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in filtered" :key="p.id">
              <td class="td-title">{{ p.title }}</td>
              <td>
                <span class="owner-name">{{ ownerName(p) }}</span>
                <small class="owner-email">{{ ownerEmail(p) }}</small>
              </td>
              <td class="registered-at">{{ formatRegisteredAt(p.created_at) }}</td>
              <td>{{ p.city }}</td>
              <td>${{ Number(p.price).toLocaleString('es-MX') }}</td>
              <td><span :class="['badge', statusMap[p.status]?.cls]">{{ statusMap[p.status]?.label ?? p.status }}</span></td>
              <td class="actions">
                <button class="view" @click="router.push(`/propiedades/${p.id}`)">Ver</button>
                <button class="edit" @click="router.push(`/admin/propiedades/${p.id}/editar`)">Editar</button>
                <button v-if="p.status === 'pending'" class="approve" @click="confirm('approve', p.id)">Aprobar</button>
                <button v-if="p.status === 'pending'" class="reject" @click="confirm('reject', p.id)">Rechazar</button>
                <button v-if="p.status === 'approved'" class="sold" @click="confirm('markSold', p.id)">Vendida</button>
                <button class="delete" @click="confirm('remove', p.id)">Eliminar</button>
              </td>
            </tr>
            <tr v-if="!filtered.length">
              <td colspan="7" class="empty">Sin propiedades</td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>
  </section>
</template>

<style scoped>
.properties-admin { display: grid; gap: 16px; }
.table-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 16px; }
.filters { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.filters button { border: 1px solid rgba(7, 23, 45, .14); background: #fff; padding: 7px 12px; border-radius: 999px; font-weight: 700; color: var(--color-muted); transition: .3s ease; }
.filters button.active, .filters button:hover { background: var(--color-navy); color: #fff; border-color: var(--color-navy); }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; border-bottom: 1px solid rgba(7, 23, 45, .08); font-size: 14px; text-align: left; }
th { font-size: 12px; color: var(--color-muted); text-transform: uppercase; letter-spacing: .08em; }
.td-title { color: var(--color-navy); font-weight: 700; }
.owner-name { display: block; color: var(--color-navy); font-weight: 700; }
.owner-email { display: block; color: var(--color-muted); font-size: 12px; margin-top: 2px; }
.registered-at { color: var(--color-navy-2); font-weight: 600; white-space: nowrap; }
.badge { padding: 5px 9px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.pendiente { background: #fff3ce; color: #8a5a00; }
.aprobada { background: #dff7e9; color: #166534; }
.rechazada { background: #fee2e2; color: #991b1b; }
.vendida { background: #e8edf0; color: var(--color-navy-2); }
.actions { display: flex; gap: 6px; flex-wrap: wrap; }
.actions button { border: none; border-radius: 7px; padding: 6px 9px; font-size: 12px; font-weight: 700; transition: .3s ease; }
.actions button:hover { filter: brightness(1.02); transform: translateY(-1px); }
.view { background: #f7efe0; color: var(--color-navy-2); }
.edit { background: #e8edf0; color: var(--color-navy-2); }
.approve { background: #dff7e9; color: #166534; }
.reject { background: #fee2e2; color: #991b1b; }
.sold { background: #f2eadc; color: var(--color-navy-2); }
.delete { background: var(--color-navy); color: #fff; }
.state { padding: 16px 0; color: var(--color-muted); }
.error-msg { color: #991b1b; }
.empty { text-align: center; color: #94a3b8; }
</style>

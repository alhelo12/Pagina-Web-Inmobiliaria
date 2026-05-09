<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { usePropertyStore } from '@/stores/propertyStore'
import AdminDashboardHeader from '@/components/admin/dashboard/AdminDashboardHeader.vue'
import Toast from '@/components/shared/Toast.vue'

const store = usePropertyStore()
const auth = useAuthStore()
const router = useRouter()
const { loading, error } = storeToRefs(store)

const filter = ref('todos')
const search = ref('')
const debouncedSearch = ref('')
let searchTimeout = null

const page = ref(1)
const perPage = ref(20)
const totalItems = ref(0)

const statusMap = {
  pending: { label: 'Pendiente', cls: 'pendiente' },
  approved: { label: 'Aprobada', cls: 'aprobada' },
  rejected: { label: 'Rechazada', cls: 'rechazada' },
  sold: { label: 'Vendida', cls: 'vendida' }
}

const toastState = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const confirmModal = ref({ show: false, action: '', propertyId: null, title: '' })

const totalPages = computed(() => Math.max(1, Math.ceil(totalItems.value / perPage.value)))

const properties = computed(() => {
  const q = debouncedSearch.value.trim().toLowerCase()
  if (!q) return store.properties
  return store.properties.filter(p =>
    p.title?.toLowerCase().includes(q) || p.city?.toLowerCase().includes(q)
  )
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

const fetchPage = () => {
  const params = { skip: (page.value - 1) * perPage.value, limit: perPage.value }
  if (filter.value !== 'todos') params.status = filter.value
  store.fetchProperties(params).then(() => {
    totalItems.value = store.total
  })
}

const showToast = (message, type = 'success') => {
  clearTimeout(toastTimeout)
  toastState.value = { show: true, message, type }
  toastTimeout = setTimeout(() => { toastState.value.show = false }, 3000)
}

const changeFilter = (f) => {
  filter.value = f
  page.value = 1
  fetchPage()
}

const goToPage = (p) => {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  fetchPage()
}

watch(search, (val) => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { debouncedSearch.value = val }, 300)
})

const openConfirm = (action, p) => {
  confirmModal.value = { show: true, action, propertyId: p.id, title: p.title }
}

const executeConfirm = async () => {
  const { action, propertyId } = confirmModal.value
  confirmModal.value.show = false
  try {
    await store[action](propertyId)
    fetchPage()
    const messages = {
      approve: 'Propiedad aprobada correctamente',
      reject: 'Propiedad rechazada',
      markSold: 'Propiedad marcada como vendida',
      remove: 'Propiedad eliminada'
    }
    showToast(messages[action] || 'Acción completada')
  } catch (err) {
    showToast(err.response?.data?.detail ?? 'Error al ejecutar acción', 'error')
  }
}

const exportCsv = () => {
  const headers = ['Título', 'Registrado por', 'Email', 'Registrada', 'Ciudad', 'Precio', 'Estado']
  const rows = properties.value.map(p => [
    p.title, ownerName(p), ownerEmail(p),
    formatRegisteredAt(p.created_at), p.city,
    Number(p.price).toLocaleString('es-MX'),
    statusMap[p.status]?.label ?? p.status
  ])
  const csv = [headers.join(','), ...rows.map(r =>
    r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')
  )].join('\n')
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'propiedades.csv'; a.click()
  URL.revokeObjectURL(url)
}

onMounted(fetchPage)
onUnmounted(() => { clearTimeout(searchTimeout); clearTimeout(toastTimeout) })
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
      @export="exportCsv"
    />

    <article class="table-card">
      <div class="filters">
        <button :class="{ active: filter === 'todos' }" @click="changeFilter('todos')">Todos</button>
        <button :class="{ active: filter === 'pending' }" @click="changeFilter('pending')">Pendientes</button>
        <button :class="{ active: filter === 'approved' }" @click="changeFilter('approved')">Aprobadas</button>
        <button :class="{ active: filter === 'rejected' }" @click="changeFilter('rejected')">Rechazadas</button>
        <button :class="{ active: filter === 'sold' }" @click="changeFilter('sold')">Vendidas</button>
      </div>

      <div v-if="loading" class="state"><div class="spinner"></div></div>
      <div v-else-if="error" class="state error-msg">{{ error }}</div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Título</th><th>Registrado por</th><th>Registrada</th><th>Ciudad</th><th>Precio</th><th>Estado</th><th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in properties" :key="p.id">
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
                <button v-if="p.status === 'pending'" class="approve" @click="openConfirm('approve', p)">Aprobar</button>
                <button v-if="p.status === 'pending'" class="reject" @click="openConfirm('reject', p)">Rechazar</button>
                <button v-if="p.status === 'approved'" class="sold" @click="openConfirm('markSold', p)">Vendida</button>
                <button class="delete" @click="openConfirm('remove', p)">Eliminar</button>
              </td>
            </tr>
            <tr v-if="!properties.length">
              <td colspan="7" class="empty">Sin propiedades</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <button :disabled="page <= 1" @click="goToPage(page - 1)">Anterior</button>
        <template v-for="p in totalPages" :key="p">
          <button v-if="Math.abs(p - page) <= 2 || p === 1 || p === totalPages" :class="{ active: p === page }" @click="goToPage(p)">{{ p }}</button>
          <span v-else-if="p === page - 3 || p === page + 3" class="dots">&hellip;</span>
        </template>
        <button :disabled="page >= totalPages" @click="goToPage(page + 1)">Siguiente</button>
        <span class="pagination-info">Mostrando {{ properties.length }} de {{ totalItems }} propiedades</span>
      </div>
    </article>

    <Teleport to="body">
      <div v-if="confirmModal.show" class="modal-overlay" @click.self="confirmModal.show = false">
        <div class="modal">
          <h2>{{ confirmModal.action === 'remove' ? 'Eliminar' : confirmModal.action === 'approve' ? 'Aprobar' : confirmModal.action === 'reject' ? 'Rechazar' : 'Marcar vendida' }} propiedad</h2>
          <p class="modal-desc">¿Confirmas que deseas <strong>{{ confirmModal.action === 'remove' ? 'eliminar' : confirmModal.action === 'approve' ? 'aprobar' : confirmModal.action === 'reject' ? 'rechazar' : 'marcar como vendida' }}</strong> la propiedad <strong>"{{ confirmModal.title }}"</strong>?</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="confirmModal.show = false">Cancelar</button>
            <button :class="['btn-confirm', confirmModal.action]" @click="executeConfirm">
              {{ confirmModal.action === 'approve' ? 'Aprobar' : confirmModal.action === 'reject' ? 'Rechazar' : confirmModal.action === 'markSold' ? 'Vendida' : 'Eliminar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Toast :visible="toastState.show" :message="toastState.message" :type="toastState.type" @close="toastState.show = false" />
  </section>
</template>

<style scoped>
.properties-admin { display: grid; gap: 16px; }
.table-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 16px; }
.filters { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.filters button { border: 1px solid rgba(7, 23, 45, .14); background: #fff; padding: 7px 12px; border-radius: 999px; font-weight: 700; color: var(--color-muted); transition: .3s ease; cursor: pointer; }
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
.actions button { border: none; border-radius: 7px; padding: 6px 9px; font-size: 12px; font-weight: 700; transition: .3s ease; cursor: pointer; }
.actions button:hover { filter: brightness(1.02); transform: translateY(-1px); }
.view { background: #f7efe0; color: var(--color-navy-2); }
.edit { background: #e8edf0; color: var(--color-navy-2); }
.approve { background: #dff7e9; color: #166534; }
.reject { background: #fee2e2; color: #991b1b; }
.sold { background: #f2eadc; color: var(--color-navy-2); }
.delete { background: var(--color-navy); color: #fff; }
.state { display: flex; justify-content: center; padding: 40px; color: #65717e; }
.error-msg { color: #991b1b; }
.spinner { width: 36px; height: 36px; border: 3px solid #eadfcf; border-top-color: #d6a848; border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; color: #94a3b8; }

.pagination { display: flex; align-items: center; gap: 6px; margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--color-line); flex-wrap: wrap; }
.pagination button { padding: 6px 11px; border-radius: 7px; font-weight: 700; font-size: 13px; background: #fff; border: 1px solid rgba(7, 23, 45, .14); color: var(--color-muted); cursor: pointer; transition: .2s ease; }
.pagination button:hover:not(:disabled) { border-color: var(--color-navy); color: var(--color-navy); }
.pagination button.active { background: var(--color-navy); color: #fff; border-color: var(--color-navy); }
.pagination button:disabled { opacity: .4; cursor: not-allowed; }
.pagination .dots { color: var(--color-muted); font-size: 13px; padding: 0 2px; }
.pagination-info { margin-left: auto; color: var(--color-muted); font-size: 13px; }

.modal-overlay { position: fixed; inset: 0; background: rgba(7, 23, 45, .56); display: flex; align-items: center; justify-content: center; z-index: 2000; padding: 20px; }
.modal { background: #fffdf8; border-radius: 10px; padding: 30px; width: 100%; max-width: 460px; box-shadow: var(--shadow-strong); }
.modal h2 { font-family: 'Poppins', sans-serif; color: #07172d; font-size: 26px; margin-bottom: 14px; }
.modal-desc { color: var(--color-muted); line-height: 1.6; margin-bottom: 24px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
.btn-cancel { padding: 0 18px; min-height: 44px; background: #eee7dc; border-radius: 8px; color: #40566e; font-weight: 900; cursor: pointer; border: none; }
.btn-confirm { padding: 0 18px; min-height: 44px; border-radius: 8px; font-weight: 900; cursor: pointer; border: none; }
.btn-confirm.approve { background: #dff7e9; color: #166534; }
.btn-confirm.reject { background: #fee2e2; color: #991b1b; }
.btn-confirm.markSold { background: #f2eadc; color: var(--color-navy-2); }
.btn-confirm.remove { background: var(--color-navy); color: #fff; }
</style>

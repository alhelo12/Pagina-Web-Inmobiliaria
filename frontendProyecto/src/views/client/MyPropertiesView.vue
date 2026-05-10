<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePropertyStore } from '@/stores/propertyStore'
import { useAuthStore } from '@/stores/authStore'
import { storeToRefs } from 'pinia'
import ClientDashboardHeader from '@/components/client/dashboard/ClientDashboardHeader.vue'
import Toast from '@/components/shared/Toast.vue'

const store = usePropertyStore()
const auth = useAuthStore()
const { properties, loading, error, total } = storeToRefs(store)
const router = useRouter()

const currentStatus = ref('all')
const search = ref('')
const debouncedSearch = ref('')
let searchTimeout = null

const page = ref(1)
const perPage = ref(20)
const totalItems = ref(0)

const toastState = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const confirmModal = ref({ show: false, action: '', propertyId: null, title: '' })

const totalPages = computed(() => Math.max(1, Math.ceil(totalItems.value / perPage.value)))

const myProperties = computed(() => {
  const q = debouncedSearch.value.trim().toLowerCase()
  let filtered = properties.value.filter(p => p.owner_id === auth.userId)
  if (q) {
    filtered = filtered.filter(p =>
      p.title?.toLowerCase().includes(q) || p.city?.toLowerCase().includes(q)
    )
  }
  return filtered
})

const counts = computed(() => ({
  all: myProperties.value.length,
  pending: myProperties.value.filter(p => p.status === 'pending').length,
  approved: myProperties.value.filter(p => p.status === 'approved').length,
  rejected: myProperties.value.filter(p => p.status === 'rejected').length
}))

const filtered = computed(() => {
  if (currentStatus.value === 'all') return myProperties.value
  return myProperties.value.filter(p => p.status === currentStatus.value)
})

const statusMap = {
  pending: { label: 'Pendiente', cls: 'pendiente' },
  approved: { label: 'Aprobada', cls: 'aprobada' },
  rejected: { label: 'Rechazada', cls: 'rechazada' }
}

const formatRegisteredAt = (value) => {
  if (!value) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(new Date(value))
}

const getAdvisorName = (property) => {
  if (property.advisor?.user?.full_name) {
    return property.advisor.user.full_name
  }
  return 'Sin asignar'
}

const fetchPage = () => {
  const params = { skip: (page.value - 1) * perPage.value, limit: perPage.value }
  store.fetchProperties(params).then(() => {
    totalItems.value = myProperties.value.length
  })
}

const showToast = (message, type = 'success') => {
  clearTimeout(toastTimeout)
  toastState.value = { show: true, message, type }
  toastTimeout = setTimeout(() => { toastState.value.show = false }, 3000)
}

const changeFilter = (f) => {
  currentStatus.value = f
  page.value = 1
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
    if (action === 'remove') {
      await store.remove(propertyId)
      showToast('Propiedad eliminada correctamente')
    }
    fetchPage()
  } catch (err) {
    showToast(err.response?.data?.detail ?? 'Error al ejecutar acción', 'error')
  }
}

const handleView = (propertyId) => {
  router.push(`/propiedades/${propertyId}`)
}

const handleEdit = (propertyId) => {
  router.push(`/admin/propiedades/${propertyId}/editar`)
}

onMounted(fetchPage)
onUnmounted(() => { clearTimeout(searchTimeout); clearTimeout(toastTimeout) })
</script>

<template>
  <section class="my-properties">
    <ClientDashboardHeader
      :search="search"
      eyebrow="Gestión"
      title="Mis Propiedades"
      :show-search="true"
      :show-add="true"
      add-label="Nueva propiedad"
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Cliente'"
      :profile-email="auth.userEmail || ''"
      @add="router.push('/cliente/publicar')"
      @search="(val) => search = val"
    />

    <article class="table-card">
      <div class="filters">
        <button :class="{ active: currentStatus === 'all' }" @click="changeFilter('all')">Todas ({{ counts.all }})</button>
        <button :class="{ active: currentStatus === 'pending' }" @click="changeFilter('pending')">Pendientes ({{ counts.pending }})</button>
        <button :class="{ active: currentStatus === 'approved' }" @click="changeFilter('approved')">Aprobadas ({{ counts.approved }})</button>
        <button :class="{ active: currentStatus === 'rejected' }" @click="changeFilter('rejected')">Rechazadas ({{ counts.rejected }})</button>
      </div>

      <div v-if="loading" class="state"><div class="spinner"></div></div>
      <div v-else-if="error" class="state error-msg">{{ error }}</div>

      <div v-else class="table-wrap">
        <table>
<thead>
              <tr>
                <th>Título</th>
                <th>Fecha</th>
                <th>Ciudad</th>
                <th>Precio</th>
                <th>Asesor</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
          <tbody>
            <tr v-for="p in filtered" :key="p.id">
              <td class="td-title">{{ p.title }}</td>
              <td class="registered-at">{{ formatRegisteredAt(p.created_at) }}</td>
              <td>{{ p.city }}</td>
              <td>${{ Number(p.price).toLocaleString('es-MX') }}</td>
              <td>
                <span :class="['advisor-badge', p.advisor_id ? 'assigned' : 'unassigned']">
                  {{ getAdvisorName(p) }}
                </span>
              </td>
              <td><span :class="['badge', statusMap[p.status]?.cls]">{{ statusMap[p.status]?.label ?? p.status }}</span></td>
              <td class="actions">
                <button class="view" @click="handleView(p.id)">Ver</button>
                <button class="edit" @click="handleEdit(p.id)">Editar</button>
                <button class="delete" @click="openConfirm('remove', p)">Eliminar</button>
              </td>
            </tr>
            <tr v-if="!filtered.length">
              <td colspan="7" class="empty">No tienes propiedades {{ currentStatus !== 'all' ? currentStatus : '' }}</td>
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
        <span class="pagination-info">Mostrando {{ filtered.length }} propiedades</span>
      </div>
    </article>

    <Teleport to="body">
      <div v-if="confirmModal.show" class="modal-overlay" @click.self="confirmModal.show = false">
        <div class="modal">
          <h2>Eliminar propiedad</h2>
          <p class="modal-desc">¿Confirmas que deseas <strong>eliminar</strong> la propiedad <strong>"{{ confirmModal.title }}"</strong>?</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="confirmModal.show = false">Cancelar</button>
            <button class="btn-confirm remove" @click="executeConfirm">Eliminar</button>
          </div>
        </div>
      </div>
    </Teleport>

    <Toast :visible="toastState.show" :message="toastState.message" :type="toastState.type" @close="toastState.show = false" />
  </section>
</template>

<style scoped>
.my-properties { font-family: 'Poppins', sans-serif; display: grid; gap: 16px; }

.table-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 16px; }
.filters { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.filters button { border: 1px solid rgba(7, 23, 45, .14); background: #fff; padding: 7px 12px; border-radius: 999px; font-weight: 700; color: var(--color-muted); transition: .3s ease; cursor: pointer; }
.filters button.active, .filters button:hover { background: var(--color-navy); color: #fff; border-color: var(--color-navy); }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; font-size: 14px; text-align: left; border-bottom: 1px solid rgba(7, 23, 45, .08); }
th { font-size: 12px; color: var(--color-muted); text-transform: uppercase; letter-spacing: .08em; }
.td-title { color: var(--color-navy); font-weight: 700; }
.registered-at { color: var(--color-navy-2); font-weight: 600; white-space: nowrap; }
.badge { padding: 5px 9px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.pendiente { background: #fff3ce; color: #8a5a00; }
.aprobada { background: #dff7e9; color: #166534; }
.rechazada { background: #fee2e2; color: #991b1b; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; align-content: center; min-height: 44px; }
.actions button { border: none; border-radius: 7px; padding: 6px 9px; font-size: 12px; font-weight: 700; transition: .3s ease; cursor: pointer; flex-shrink: 0; }
.actions button:hover { filter: brightness(1.02); transform: translateY(-1px); }
.view { background: #f7efe0; color: var(--color-navy-2); }
.edit { background: #e8edf0; color: var(--color-navy-2); }
.delete { background: var(--color-navy); color: #fff; }
.state { display: flex; justify-content: center; padding: 40px; color: var(--color-muted); }
.error-msg { color: #991b1b; }
.spinner { width: 36px; height: 36px; border: 3px solid #eadfcf; border-top-color: var(--color-gold); border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; color: var(--color-muted); padding: 20px; }

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
.btn-confirm.remove { background: var(--color-navy); color: #fff; }

@media (max-width: 768px) {
  .filters { overflow-x: auto; flex-wrap: nowrap; }
  .filters button { flex: 0 0 auto; }
}
</style>
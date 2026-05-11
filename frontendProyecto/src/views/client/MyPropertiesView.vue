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
const actionLoading = ref(false)

const sortKey = ref('created_at')
const sortDir = ref('desc')

const sort = (key) => {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'desc'
  }
  page.value = 1
  fetchPage()
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

// Popover de asesor
const activeAdvisorPopover = ref(null)
const advisorDetails = ref({})
const advisorLoading = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(totalItems.value / perPage.value)))

const myProperties = computed(() => {
  const q = debouncedSearch.value.trim().toLowerCase()
  const uid = Number(auth.userId)
  let filtered = properties.value.filter(p => p.submitted_by_user_id === uid)
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
  toastTimeout = setTimeout(() => { toastState.value.show = false }, 4000)
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
  actionLoading.value = true
  try {
    if (action === 'remove') {
      await store.remove(propertyId)
      showToast('Propiedad eliminada correctamente')
    }
    fetchPage()
  } catch (err) {
    showToast(err.response?.data?.detail ?? 'Error al ejecutar acción', 'error')
  } finally {
    actionLoading.value = false
  }
}

const handleView = (propertyId) => {
  router.push(`/propiedades/${propertyId}`)
}

const handleEdit = (propertyId) => {
  router.push(`/admin/propiedades/${propertyId}/editar`)
}

// Obtener detalles del asesor
const fetchAdvisorDetails = async (advisorId) => {
  advisorLoading.value = true
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/advisors/${advisorId}`, {
      headers: { ...auth.authHeaders }
    })
    if (!response.ok) throw new Error('Error al cargar datos del asesor')
    const data = await response.json()
    advisorDetails.value = {
      name: data.user?.full_name || `Asesor #${advisorId}`,
      email: data.user?.email || '',
      phone: data.user?.phone || '',
      agency: data.agency_name || '',
      licenseNumber: data.license_number || ''
    }
  } catch (err) {
    advisorDetails.value = { name: 'Error', email: '', phone: '', agency: '' }
  } finally {
    advisorLoading.value = false
  }
}

const toggleAdvisorPopover = async (event, property) => {
  event.stopPropagation()

  if (activeAdvisorPopover.value === property.id) {
    activeAdvisorPopover.value = null
    return
  }

  activeAdvisorPopover.value = property.id

  // Solo hacer fetch si no tenemos los datos ya
  if (!advisorDetails.value.name || advisorDetails.value.name === 'Error') {
    await fetchAdvisorDetails(property.advisor_id)
  } else if (advisorDetails.value.name === '') {
    await fetchAdvisorDetails(property.advisor_id)
  }
}

const closeAdvisorPopover = (event) => {
  if (activeAdvisorPopover.value !== null) {
    activeAdvisorPopover.value = null
  }
}

document.addEventListener('click', closeAdvisorPopover)

onMounted(fetchPage)
onUnmounted(() => {
  clearTimeout(searchTimeout)
  clearTimeout(toastTimeout)
  document.removeEventListener('click', closeAdvisorPopover)
})
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

    <Breadcrumb :crumbs="[{ label: 'Mis Propiedades', path: '/cliente/mis-propiedades' }]" />

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
              <th></th>
              <th class="sortable" @click="sort('title')">Título <span class="sort-icon" :class="{ active: sortKey === 'title' }">{{ sortKey === 'title' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span></th>
              <th class="sortable" @click="sort('created_at')">Fecha <span class="sort-icon" :class="{ active: sortKey === 'created_at' }">{{ sortKey === 'created_at' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span></th>
              <th class="sortable" @click="sort('city')">Ciudad <span class="sort-icon" :class="{ active: sortKey === 'city' }">{{ sortKey === 'city' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span></th>
              <th class="sortable" @click="sort('price')">Precio <span class="sort-icon" :class="{ active: sortKey === 'price' }">{{ sortKey === 'price' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span></th>
              <th>Asesor</th>
              <th class="sortable" @click="sort('status')">Estado <span class="sort-icon" :class="{ active: sortKey === 'status' }">{{ sortKey === 'status' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span></th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in filtered" :key="p.id">
              <td class="td-thumb">
                <img :src="getPropertyImage(p) || propertyFallback" :alt="p.title" @error="(e) => { e.target.src = propertyFallback }" />
              </td>
              <td class="td-title">{{ p.title }}</td>
              <td class="registered-at">{{ formatRegisteredAt(p.created_at) }}</td>
              <td>{{ p.city }}</td>
              <td>${{ Number(p.price).toLocaleString('es-MX') }}</td>
              <td class="advisor-cell">
                <span
                  :class="['advisor-badge', p.advisor_id ? 'assigned' : 'unassigned']"
                  @click="p.advisor_id ? toggleAdvisorPopover($event, p) : null"
                >
                  {{ getAdvisorName(p) }}
                  <span v-if="p.advisor_id" class="advisor-info-icon">?</span>
                </span>
                <div
                  v-if="activeAdvisorPopover === p.id"
                  class="advisor-popover"
                >
                  <div v-if="advisorLoading" class="popover-loading">Cargando...</div>
                  <template v-else>
                    <div class="popover-header">{{ advisorDetails.name }}</div>
                    <div class="popover-body">
                      <div v-if="advisorDetails.agency" class="popover-item">
                        <span class="popover-icon">🏢</span>
                        <span>{{ advisorDetails.agency }}</span>
                      </div>
                      <div v-if="advisorDetails.licenseNumber" class="popover-item">
                        <span class="popover-icon">📋</span>
                        <span>{{ advisorDetails.licenseNumber }}</span>
                      </div>
                      <div v-if="advisorDetails.email" class="popover-item">
                        <span class="popover-icon">📧</span>
                        <a :href="'mailto:' + advisorDetails.email" class="popover-link">
                          {{ advisorDetails.email }}
                        </a>
                      </div>
                      <div class="popover-item">
                        <span class="popover-icon">📱</span>
                        <template v-if="advisorDetails.phone">
                          <a :href="'tel:' + advisorDetails.phone" class="popover-link">
                            {{ advisorDetails.phone }}
                          </a>
                        </template>
                        <template v-else>
                          <span class="popover-unavailable">No disponible</span>
                        </template>
                      </div>
                    </div>
                  </template>
                </div>
              </td>
              <td><span :class="['badge', statusMap[p.status]?.cls]">{{ statusMap[p.status]?.label ?? p.status }}</span></td>
              <td class="actions">
                <button class="view" title="Ver" @click="handleView(p.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  Ver
                </button>
                <button class="edit" title="Editar" @click="handleEdit(p.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  Editar
                </button>
                <button class="delete" title="Eliminar" :disabled="actionLoading" @click="openConfirm('remove', p)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                  {{ actionLoading ? '...' : 'Eliminar' }}
                </button>
              </td>
            </tr>
            <tr v-if="!filtered.length">
              <td colspan="8" class="empty">No tienes propiedades {{ currentStatus !== 'all' ? currentStatus : '' }}</td>
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
            <button class="btn-confirm remove" :disabled="actionLoading" @click="executeConfirm">
              {{ actionLoading ? 'Eliminando...' : 'Eliminar' }}
            </button>
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
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: var(--color-navy); }
.sort-icon { margin-left: 4px; font-size: 10px; opacity: .4; }
.sort-icon.active { opacity: 1; color: var(--color-gold); }
tr:hover { background: rgba(214, 168, 72, .05); }
.td-thumb { width: 44px; padding-right: 8px; }
.td-thumb img { width: 44px; height: 44px; border-radius: 8px; object-fit: cover; background: #f0ece4; }
.td-title { color: var(--color-navy); font-weight: 700; }
.registered-at { color: var(--color-navy-2); font-weight: 600; white-space: nowrap; }
.badge { padding: 5px 9px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.pendiente { background: #fff3ce; color: #8a5a00; }
.aprobada { background: #dff7e9; color: #166534; }
.rechazada { background: #fee2e2; color: #991b1b; }
.actions { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; align-content: center; min-height: 52px; }
.actions button { border: none; border-radius: 7px; padding: 6px 9px; font-size: 12px; font-weight: 700; transition: .3s ease; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; gap: 4px; }
.actions button:hover { filter: brightness(1.02); transform: translateY(-1px); }
.view { background: #f7efe0; color: var(--color-navy-2); }
.edit { background: #e8edf0; color: var(--color-navy-2); }
.delete { background: var(--color-navy); color: #fff; }
.state { display: flex; justify-content: center; padding: 40px; color: var(--color-muted); }
.error-msg { color: #991b1b; }
.spinner { width: 36px; height: 36px; border: 3px solid #eadfcf; border-top-color: var(--color-gold); border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; color: var(--color-muted); padding: 20px; }

/* Advisor Popover */
.advisor-cell {
  position: relative;
  white-space: nowrap;
}

.advisor-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 7px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s ease;
  border: none;
  background: transparent;
  color: inherit;
}

.advisor-badge.assigned {
  color: var(--color-navy-2);
}

.advisor-badge.unassigned {
  color: var(--color-muted);
  cursor: default;
}

.advisor-badge:hover.assigned {
  color: var(--color-gold);
}

.advisor-info-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(214, 168, 72, 0.12);
  color: var(--color-gold);
  font-size: 10px;
  font-weight: 800;
  transition: 0.2s ease;
}

.advisor-badge.assigned:hover .advisor-info-icon {
  background: var(--color-gold);
  color: var(--color-navy);
}

.advisor-popover {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 100;
  min-width: 260px;
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 10px;
  box-shadow: 0 12px 40px rgba(7, 23, 45, 0.18);
  padding: 14px;
  margin-top: 6px;
  animation: popoverIn 0.15s ease;
}

@keyframes popoverIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.popover-loading {
  text-align: center;
  color: var(--color-muted);
  font-size: 13px;
  padding: 10px;
}

.popover-header {
  font-weight: 700;
  color: var(--color-navy);
  font-size: 14px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-line);
}

.popover-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.popover-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-muted);
}

.popover-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.popover-link {
  color: var(--color-navy-2);
  text-decoration: none;
  font-weight: 500;
  transition: 0.2s ease;
}

.popover-link:hover {
  color: var(--color-gold);
  text-decoration: underline;
}

.popover-unavailable {
  color: var(--color-muted);
  font-style: italic;
  font-size: 12px;
}

/* Pagination */
.pagination { display: flex; align-items: center; gap: 6px; margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--color-line); flex-wrap: wrap; }
.pagination button { padding: 6px 11px; border-radius: 7px; font-weight: 700; font-size: 13px; background: #fff; border: 1px solid rgba(7, 23, 45, .14); color: var(--color-muted); cursor: pointer; transition: .2s ease; }
.pagination button:hover:not(:disabled) { border-color: var(--color-navy); color: var(--color-navy); }
.pagination button.active { background: var(--color-navy); color: #fff; border-color: var(--color-navy); }
.pagination button:disabled { opacity: .4; cursor: not-allowed; }
.pagination .dots { color: var(--color-muted); font-size: 13px; padding: 0 2px; }
.pagination-info { margin-left: auto; color: var(--color-muted); font-size: 13px; }

@media (max-width: 768px) {
  .filters { overflow-x: auto; flex-wrap: nowrap; }
  .filters button { flex: 0 0 auto; }
  .advisor-popover { min-width: 220px; }
}
</style>
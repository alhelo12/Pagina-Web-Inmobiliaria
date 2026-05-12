<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePropertyStore } from '@/stores/propertyStore'
import { useAuthStore } from '@/stores/authStore'
import { storeToRefs } from 'pinia'
import ClientDashboardHeader from '@/components/client/dashboard/ClientDashboardHeader.vue'
import Toast from '@/components/shared/Toast.vue'
import Breadcrumb from '@/components/shared/Breadcrumb.vue'

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
const verifyToast = ref({ show: false })
let verifyToastTimeout = null
const sendingEmail = ref(false)
const emailSent = ref(false)

const needsEmailVerification = computed(() =>
  auth.role === 'client' && auth.isSupabaseUser && !auth.isEmailVerified
)

const resendEmail = async () => {
  sendingEmail.value = true
  emailSent.value = false
  try {
    await auth.resendVerificationEmail(auth.userEmail)
    emailSent.value = true
    setTimeout(() => { emailSent.value = false }, 5000)
  } catch {
    // silent
  } finally {
    sendingEmail.value = false
  }
}

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
const advisorDataCache = ref({})
const advisorLoading = ref(false)
const popoverPosition = ref({ top: 0, left: 0 })

const activeAdvisorData = computed(() => {
  if (!activeAdvisorPopover.value) return null
  const prop = filtered.value.find(p => p.id === activeAdvisorPopover.value)
  if (!prop?.advisor_id) return null
  return advisorDataCache.value[prop.advisor_id] ?? null
})

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
  if (action === 'remove' && needsEmailVerification.value) {
    verifyToast.value = { show: true }
    clearTimeout(verifyToastTimeout)
    verifyToastTimeout = setTimeout(() => { verifyToast.value.show = false }, 5000)
    return
  }
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
    advisorDataCache.value[advisorId] = {
      name: data.user?.full_name || `Asesor #${advisorId}`,
      email: data.user?.email || '',
      phone: data.user?.phone || '',
      agency: data.agency_name || '',
      licenseNumber: data.license_number || ''
    }
  } catch {
    advisorDataCache.value[advisorId] = { name: 'Error', email: '', phone: '', agency: '' }
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

  const el = document.getElementById(`advisor-badge-${property.id}`)
  if (el) {
    const rect = el.getBoundingClientRect()
    const scrollY = window.scrollY || document.documentElement.scrollTop
    popoverPosition.value = {
      top: rect.bottom + scrollY + 6,
      left: Math.min(rect.left, window.innerWidth - 300)
    }
  }

  activeAdvisorPopover.value = property.id

  if (!advisorDataCache.value[property.advisor_id]) {
    await fetchAdvisorDetails(property.advisor_id)
  }
}

const closeAdvisorPopover = () => {
  activeAdvisorPopover.value = null
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
                  v-if="p.advisor_id"
                  :id="`advisor-badge-${p.id}`"
                  class="advisor-badge"
                  @click="toggleAdvisorPopover($event, p)"
                >
                  {{ getAdvisorName(p) }}
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                </span>
                <span v-else class="advisor-badge unassigned">Sin asignar</span>
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

      <!-- Mobile cards -->
      <div class="mobile-cards">
        <div v-for="p in filtered" :key="p.id" class="mobile-card">
          <div class="mc-header">
            <img :src="getPropertyImage(p) || propertyFallback" :alt="p.title" class="mc-thumb" @error="(e) => { e.target.src = propertyFallback }" />
            <div class="mc-title-group">
              <strong class="mc-title">{{ p.title }}</strong>
              <small class="mc-date">{{ formatRegisteredAt(p.created_at) }}</small>
            </div>
            <span :class="['badge', statusMap[p.status]?.cls]">{{ statusMap[p.status]?.label ?? p.status }}</span>
          </div>
          <div class="mc-body">
            <span><strong>Ciudad:</strong> {{ p.city }}</span>
            <span><strong>Precio:</strong> ${{ Number(p.price).toLocaleString('es-MX') }}</span>
            <span class="advisor-cell"><strong>Asesor:</strong> {{ getAdvisorName(p) }}</span>
          </div>
          <div class="mc-actions">
            <button class="view" @click="handleView(p.id)">Ver</button>
            <button class="edit" @click="handleEdit(p.id)">Editar</button>
            <button class="delete" :disabled="actionLoading" @click="openConfirm('remove', p)">Eliminar</button>
          </div>
        </div>
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
      <div
        v-if="activeAdvisorPopover"
        class="advisor-popover"
        :style="{ top: popoverPosition.top + 'px', left: popoverPosition.left + 'px' }"
        @click.stop
      >
        <div class="popover-header">
          <strong>{{ activeAdvisorData?.name }}</strong>
          <button class="popover-close" @click="closeAdvisorPopover">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div v-if="advisorLoading" class="popover-loading">Cargando...</div>
        <template v-else>
          <div class="popover-body">
            <div v-if="activeAdvisorData?.agency" class="popover-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
              <span>{{ activeAdvisorData.agency }}</span>
            </div>
            <div v-if="activeAdvisorData?.licenseNumber" class="popover-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
              <span>{{ activeAdvisorData.licenseNumber }}</span>
            </div>
            <div v-if="activeAdvisorData?.email" class="popover-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              <a :href="'mailto:' + activeAdvisorData.email" class="popover-link">{{ activeAdvisorData.email }}</a>
            </div>
            <div class="popover-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              <a v-if="activeAdvisorData?.phone" :href="'tel:' + activeAdvisorData.phone" class="popover-link">{{ activeAdvisorData.phone }}</a>
              <span v-else class="popover-unavailable">No disponible</span>
            </div>
          </div>
        </template>
      </div>
    </Teleport>

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

    <div v-if="verifyToast.show" class="verify-toast">
      <div class="verify-toast-content">
        <strong>Debes verificar tu correo</strong> para eliminar propiedades.
        <button class="verify-toast-btn" :disabled="sendingEmail" @click="resendEmail">
          {{ sendingEmail ? '...' : emailSent ? '¡Enviado!' : 'Reenviar verificación' }}
        </button>
      </div>
    </div>

    <Toast :visible="toastState.show" :message="toastState.message" :type="toastState.type" @close="toastState.show = false" />
  </section>
</template>

<style scoped>
.my-properties { font-family: 'Poppins', sans-serif; display: grid; gap: 16px; }

.table-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 16px; }
.filters { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.filters button { border: 1px solid rgba(7, 23, 45, .14); background: #fff; padding: 7px 12px; border-radius: 999px; font-weight: 700; color: var(--color-muted); transition: .3s ease; cursor: pointer; }
.filters button.active, .filters button:hover { background: var(--color-navy); color: #fff; border-color: var(--color-navy); }
.table-wrap {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  scrollbar-color: rgba(16, 46, 79, .35) transparent;
}
.table-wrap::-webkit-scrollbar { height: 8px; }
.table-wrap::-webkit-scrollbar-thumb { background: rgba(16, 46, 79, .35); border-radius: 999px; }
table { width: max(100%, 980px); border-collapse: collapse; table-layout: auto; }
th, td { padding: 12px; font-size: 14px; text-align: left; border-bottom: 1px solid rgba(7, 23, 45, .08); white-space: nowrap; vertical-align: middle; }
th { font-size: 12px; color: var(--color-muted); text-transform: uppercase; letter-spacing: .08em; }
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: var(--color-navy); }
.sort-icon { margin-left: 4px; font-size: 10px; opacity: .4; }
.sort-icon.active { opacity: 1; color: var(--color-gold); }
tr:hover { background: rgba(214, 168, 72, .05); }
.td-thumb { width: 44px; padding-right: 8px; }
.td-thumb img { width: 44px; height: 44px; border-radius: 8px; object-fit: cover; background: #f0ece4; }
.td-title { color: var(--color-navy); font-weight: 700; min-width: 220px; white-space: normal; }
.registered-at { color: var(--color-navy-2); font-weight: 600; white-space: nowrap; }
.badge { padding: 5px 9px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.pendiente { background: #fff3ce; color: #8a5a00; }
.aprobada { background: #dff7e9; color: #166534; }
.rechazada { background: #fee2e2; color: #991b1b; }
.actions { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; align-content: center; min-height: 52px; min-width: 210px; }
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
  gap: 5px;
  padding: 4px 10px;
  border-radius: 7px;
  font-size: 12px;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  transition: 0.2s ease;
  border: none;
  background: rgba(214, 168, 72, 0.1);
  color: var(--color-navy-2);
}
.advisor-badge:hover { background: rgba(214, 168, 72, 0.2); color: var(--color-gold); }
.advisor-badge.unassigned { background: transparent; color: var(--color-muted); cursor: default; }
.advisor-badge svg { color: var(--color-gold); flex-shrink: 0; }

.advisor-popover {
  position: fixed;
  z-index: 2000;
  min-width: 280px;
  max-width: 320px;
  background: #fff;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  box-shadow: 0 16px 48px rgba(7, 23, 45, 0.2);
  overflow: hidden;
  animation: popoverIn 0.15s ease;
}

@keyframes popoverIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

.popover-loading { text-align: center; color: var(--color-muted); font-size: 13px; padding: 16px; }
.popover-body { display: flex; flex-direction: column; gap: 0; }
.popover-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--color-muted);
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-line);
}
.popover-item:last-child { border-bottom: none; }
.popover-item svg { color: var(--color-gold); flex-shrink: 0; }
.popover-link { color: var(--color-navy-2); text-decoration: none; font-weight: 500; transition: 0.2s ease; }
.popover-link:hover { color: var(--color-gold); text-decoration: underline; }
.popover-unavailable { color: var(--color-muted); font-style: italic; font-size: 12px; }

.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-line);
  background: #f7efe0;
}
.popover-header strong { color: var(--color-navy); font-size: 14px; }
.popover-close {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: none;
  background: rgba(7, 23, 45, 0.08);
  color: var(--color-navy);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: 0.2s ease;
  flex-shrink: 0;
}
.popover-close:hover { background: rgba(153, 27, 27, 0.12); color: #991b1b; }

/* Pagination */
.pagination { display: flex; align-items: center; gap: 6px; margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--color-line); flex-wrap: wrap; }
.pagination button { padding: 6px 11px; border-radius: 7px; font-weight: 700; font-size: 13px; background: #fff; border: 1px solid rgba(7, 23, 45, .14); color: var(--color-muted); cursor: pointer; transition: .2s ease; }
.pagination button:hover:not(:disabled) { border-color: var(--color-navy); color: var(--color-navy); }
.pagination button.active { background: var(--color-navy); color: #fff; border-color: var(--color-navy); }
.pagination button:disabled { opacity: .4; cursor: not-allowed; }
.pagination .dots { color: var(--color-muted); font-size: 13px; padding: 0 2px; }
.pagination-info { margin-left: auto; color: var(--color-muted); font-size: 13px; }

.verify-toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); z-index: 9999; background: #fef2f2; border: 1px solid #fecaca; border-radius: 12px; padding: 16px 24px; box-shadow: 0 16px 48px rgba(7,23,45,0.2); max-width: 480px; }
.verify-toast-content { display: flex; align-items: center; gap: 12px; font-size: 14px; color: #991b1b; flex-wrap: wrap; }
.verify-toast-btn { border: none; border-radius: 8px; padding: 8px 16px; background: var(--color-gold); color: var(--color-navy); font-weight: 700; font-size: 13px; cursor: pointer; white-space: nowrap; }
.verify-toast-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.mobile-cards { display: none; }
.mobile-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; padding: 14px; }
.mc-header { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 10px; }
.mc-thumb { width: 48px; height: 48px; border-radius: 8px; object-fit: cover; background: #f0ece4; flex-shrink: 0; }
.mc-title-group { flex: 1; min-width: 0; }
.mc-title { display: block; color: var(--color-navy); font-size: 14px; }
.mc-date { display: block; color: var(--color-muted); font-size: 11px; margin-top: 2px; }
.mc-body { display: flex; flex-direction: column; gap: 6px; padding: 8px 0; font-size: 13px; color: var(--color-navy); }
.mc-body span strong { color: var(--color-muted); font-weight: 600; }
.mc-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.mc-actions button { border: none; border-radius: 7px; padding: 6px 10px; font-size: 12px; font-weight: 700; cursor: pointer; font-family: inherit; }

@media (max-width: 768px) {
  .table-wrap { display: none; }
  .mobile-cards { display: flex; flex-direction: column; gap: 12px; }
  .filters { flex-wrap: wrap; }
  .filters button { font-size: 12px; padding: 6px 10px; }
  .advisor-popover { min-width: 220px; }
  .pagination-info { width: 100%; text-align: center; margin-left: 0; }
}
@media (max-width: 480px) {
  .my-properties { gap: 12px; }
  .table-card { padding: 12px; }
  .pagination { justify-content: center; }
  .verify-toast { left: 16px; right: 16px; transform: none; max-width: none; }
  .verify-toast-content { flex-direction: column; text-align: center; }
}
</style>

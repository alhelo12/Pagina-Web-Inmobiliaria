<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePropertyStore } from '@/stores/propertyStore'
import { useAuthStore } from '@/stores/authStore'
import { storeToRefs } from 'pinia'
import AdminDashboardHeader from '@/components/admin/dashboard/AdminDashboardHeader.vue'
import { useToast } from '@/composables/useToast'
import Breadcrumb from '@/components/shared/Breadcrumb.vue'

const { addToast } = useToast()
const store = usePropertyStore()
const auth = useAuthStore()
const { properties, availableProperties, loading, error, total } = storeToRefs(store)
const router = useRouter()

const currentSection = ref('my-properties')
const currentStatus = ref('all')

const search = ref('')
const debouncedSearch = ref('')
let searchTimeout = null

const page = ref(1)
const perPage = ref(20)
const totalItems = ref(0)

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

const totalPages = computed(() => Math.max(1, Math.ceil(totalItems.value / perPage.value)))

const myProperties = computed(() => {
  const q = debouncedSearch.value.trim().toLowerCase()
  let filtered = properties.value.filter(p => p.advisor_id !== null)
  if (q) {
    filtered = filtered.filter(p =>
      p.title?.toLowerCase().includes(q) || p.city?.toLowerCase().includes(q)
    )
  }
  return filtered
})

const counts = computed(() => ({
  my:        myProperties.value.length,
  pending:   myProperties.value.filter(p => p.status === 'pending').length,
  approved:  myProperties.value.filter(p => p.status === 'approved').length,
  rejected:  myProperties.value.filter(p => p.status === 'rejected').length,
  sold:      myProperties.value.filter(p => p.status === 'sold').length
}))

const filtered = computed(() => {
  if (currentSection.value === 'available') return availableProperties.value
  if (currentStatus.value === 'all') return myProperties.value
  return myProperties.value.filter(p => p.status === currentStatus.value)
})

const statusMap = {
  pending: { label: 'Pendiente', cls: 'pendiente' },
  approved: { label: 'Aprobada', cls: 'aprobada' },
  rejected: { label: 'Rechazada', cls: 'rechazada' },
  sold: { label: 'Vendida', cls: 'vendida' }
}

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
  if (sortKey.value) { params.sort_by = sortKey.value; params.sort_dir = sortDir.value }
  store.fetch({ mode: 'advisor', ...params }).then(() => {
    totalItems.value = total.value
  })
}

const changeFilter = (f) => {
  currentStatus.value = f
  page.value = 1
}

const changeSection = (section) => {
  currentSection.value = section
  if (section === 'my-properties') {
    currentStatus.value = 'all'
  }
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
    if (action === 'approve') await store.approve(propertyId)
    else if (action === 'reject') await store.reject(propertyId)
    else if (action === 'sold') await store.markSold(propertyId)
    else if (action === 'remove') await store.remove(propertyId)
    fetchPage()
    const messages = {
      approve: 'Propiedad aprobada correctamente',
      reject: 'Propiedad rechazada',
      sold: 'Propiedad marcada como vendida',
      remove: 'Propiedad eliminada'
    }
    addToast({ message: messages[action] || 'Acción completada', type: 'success' })
  } catch (err) {
    addToast({ message: err.response?.data?.detail ?? 'Error al ejecutar acción', type: 'error' })
  } finally {
    actionLoading.value = false
  }
}

const handleTake = async (property) => {
  try {
    await store.takeProperty(property.id)
    await store.fetch({ mode: 'stats' })
    addToast({ message: 'Propiedad tomada correctamente', type: 'success' })
  } catch (err) {
    addToast({ message: err.response?.data?.detail ?? 'Error al tomar propiedad', type: 'error' })
  }
}

const exportCsv = () => {
  const headers = ['Título', 'Registrado por', 'Email', 'Registrada', 'Ciudad', 'Precio', 'Estado']
  const rows = filtered.value.map(p => [
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
  a.href = url; a.download = 'mis-propiedades.csv'; a.click()
  URL.revokeObjectURL(url)
}

onMounted(fetchPage)
onUnmounted(() => { clearTimeout(searchTimeout) })
</script>

<template>
  <section class="properties-advisor">
    <AdminDashboardHeader
      v-model:search="search"
      eyebrow="Gestión de propiedades"
      title="Mis Propiedades"
      add-label="Agregar propiedad"
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Asesor'"
      :profile-email="auth.userEmail || ''"
      @add="router.push('/advisor/publicar')"
      @export="exportCsv"
    />

    <Breadcrumb :crumbs="[{ label: 'Mis Propiedades', path: '/advisor/panel' }]" />

    <div class="section-tabs">
      <button
        :class="{ active: currentSection === 'my-properties' }"
        @click="changeSection('my-properties')"
      >
        Mis Propiedades ({{ counts.my }})
      </button>
      <button
        :class="{ active: currentSection === 'available' }"
        @click="changeSection('available')"
      >
        Disponibles para Tomar ({{ availableProperties.length }})
      </button>
    </div>

    <template v-if="currentSection === 'my-properties'">
      <article class="table-card">
        <div class="filters">
          <button :class="{ active: currentStatus === 'all' }" @click="changeFilter('all')">Todas</button>
          <button :class="{ active: currentStatus === 'pending' }" @click="changeFilter('pending')">Pendientes</button>
          <button :class="{ active: currentStatus === 'approved' }" @click="changeFilter('approved')">Aprobadas</button>
          <button :class="{ active: currentStatus === 'rejected' }" @click="changeFilter('rejected')">Rechazadas</button>
          <button :class="{ active: currentStatus === 'sold' }" @click="changeFilter('sold')">Vendidas</button>
        </div>

        <div v-if="loading" class="state"><div class="spinner"></div></div>
        <div v-else-if="error" class="state error-msg">{{ error }}</div>

        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th></th>
                <th class="sortable" @click="sort('title')">Título <span class="sort-icon" :class="{ active: sortKey === 'title' }">{{ sortKey === 'title' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span></th>
                <th>Registrado por</th>
                <th class="sortable" @click="sort('created_at')">Registrada <span class="sort-icon" :class="{ active: sortKey === 'created_at' }">{{ sortKey === 'created_at' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span></th>
                <th class="sortable" @click="sort('city')">Ciudad <span class="sort-icon" :class="{ active: sortKey === 'city' }">{{ sortKey === 'city' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span></th>
                <th class="sortable" @click="sort('price')">Precio <span class="sort-icon" :class="{ active: sortKey === 'price' }">{{ sortKey === 'price' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span></th>
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
                <td>
                  <span class="owner-name">{{ ownerName(p) }}</span>
                  <small class="owner-email">{{ ownerEmail(p) }}</small>
                </td>
                <td class="registered-at">{{ formatRegisteredAt(p.created_at) }}</td>
                <td>{{ p.city }}</td>
                <td>${{ Number(p.price).toLocaleString('es-MX') }}</td>
                <td><span :class="['badge', statusMap[p.status]?.cls]">{{ statusMap[p.status]?.label ?? p.status }}</span></td>
                <td class="actions">
                  <button class="view" title="Ver" @click="router.push(`/propiedades/${p.id}`)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    Ver
                  </button>
                  <button class="edit" title="Editar" @click="router.push(`/admin/propiedades/${p.id}/editar`)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    Editar
                  </button>
                  <button v-if="p.status === 'pending'" class="approve" title="Aprobar" @click="openConfirm('approve', p)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                    Aprobar
                  </button>
                  <button v-if="p.status === 'pending'" class="reject" title="Rechazar" @click="openConfirm('reject', p)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    Rechazar
                  </button>
                  <button v-if="p.status === 'approved'" class="sold" title="Marcar vendida" @click="openConfirm('sold', p)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                    Vendida
                  </button>
                  <button class="delete" title="Eliminar" @click="openConfirm('remove', p)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                    Eliminar
                  </button>
                </td>
              </tr>
              <tr v-if="!filtered.length">
                <td colspan="8" class="empty">Sin propiedades</td>
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
                <span class="mc-owner">{{ ownerName(p) }}</span>
                <small class="mc-email">{{ ownerEmail(p) }}</small>
              </div>
              <span :class="['badge', statusMap[p.status]?.cls]">{{ statusMap[p.status]?.label ?? p.status }}</span>
            </div>
            <div class="mc-body">
              <span><strong>Ciudad:</strong> {{ p.city }}</span>
              <span><strong>Precio:</strong> ${{ Number(p.price).toLocaleString('es-MX') }}</span>
              <span><strong>Registrada:</strong> {{ formatRegisteredAt(p.created_at) }}</span>
            </div>
            <div class="mc-actions">
              <button class="view" @click="router.push(`/propiedades/${p.id}`)">Ver</button>
              <button class="edit" @click="router.push(`/admin/propiedades/${p.id}/editar`)">Editar</button>
              <button v-if="p.status === 'pending'" class="approve" @click="openConfirm('approve', p)">Aprobar</button>
              <button v-if="p.status === 'pending'" class="reject" @click="openConfirm('reject', p)">Rechazar</button>
              <button v-if="p.status === 'approved'" class="sold" @click="openConfirm('sold', p)">Vendida</button>
              <button class="delete" @click="openConfirm('remove', p)">Eliminar</button>
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
          <span class="pagination-info">Mostrando {{ filtered.length }} de {{ totalItems }} propiedades</span>
        </div>
      </article>
    </template>

    <template v-else-if="currentSection === 'available'">
      <article class="table-card">
        <div v-if="availableProperties.length" class="available-list">
          <div v-for="p in availableProperties" :key="p.id" class="available-row">
            <div class="prop-info">
              <strong>{{ p.title }}</strong>
              <span>{{ p.city || 'Sin ciudad' }}</span>
            </div>
            <div class="prop-price">${{ Number(p.price || 0).toLocaleString('es-MX') }}</div>
            <button class="take-btn" @click="handleTake(p)">Tomar</button>
          </div>
        </div>
        <p v-else class="empty">No hay propiedades disponibles para tomar.</p>
      </article>
    </template>

    <Teleport to="body">
      <div v-if="confirmModal.show" class="modal-overlay" @click.self="confirmModal.show = false">
        <div class="modal">
          <h2>{{ confirmModal.action === 'remove' ? 'Eliminar' : confirmModal.action === 'approve' ? 'Aprobar' : confirmModal.action === 'reject' ? 'Rechazar' : 'Marcar vendida' }} propiedad</h2>
          <p class="modal-desc">¿Confirmas que deseas <strong>{{ confirmModal.action === 'remove' ? 'eliminar' : confirmModal.action === 'approve' ? 'aprobar' : confirmModal.action === 'reject' ? 'rechazar' : 'marcar como vendida' }}</strong> la propiedad <strong>"{{ confirmModal.title }}"</strong>?</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="confirmModal.show = false">Cancelar</button>
            <button :class="['btn-confirm', confirmModal.action]" :disabled="actionLoading" @click="executeConfirm">
              {{ actionLoading ? '...' : confirmModal.action === 'approve' ? 'Aprobar' : confirmModal.action === 'reject' ? 'Rechazar' : confirmModal.action === 'sold' ? 'Vendida' : 'Eliminar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </section>
</template>

<style scoped>
.properties-advisor { font-family: 'Poppins', sans-serif; display: grid; gap: 16px; }

.section-tabs { display: flex; gap: 10px; }
.section-tabs button {
  padding: 12px 20px; border: 1px solid var(--color-line); border-radius: 10px;
  background: var(--color-card); color: var(--color-muted); font-weight: 600;
  cursor: pointer; transition: .2s;
}
.section-tabs button.active { background: var(--color-navy); color: white; border-color: var(--color-navy); }

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
th, td { padding: 12px; font-size: 14px; text-align: left; border-bottom: 1px solid rgba(7, 23, 45, .08); }
th { font-size: 12px; color: var(--color-muted); text-transform: uppercase; letter-spacing: .08em; white-space: nowrap; vertical-align: middle; }
td { vertical-align: top; }
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: var(--color-navy); }
.sort-icon { margin-left: 4px; font-size: 10px; opacity: .4; }
.sort-icon.active { opacity: 1; color: var(--color-gold); }
tr:hover { background: rgba(214, 168, 72, .05); }
.td-thumb { width: 44px; padding-right: 8px; }
.td-thumb img { width: 44px; height: 44px; border-radius: 8px; object-fit: cover; background: #f0ece4; max-width: none; }
.td-title { color: var(--color-navy); font-weight: 700; min-width: 220px; white-space: normal; }
.owner-name { display: block; color: var(--color-navy); font-weight: 700; }
.owner-email { display: block; color: var(--color-muted); font-size: 12px; margin-top: 2px; white-space: normal; }
.registered-at { color: var(--color-navy-2); font-weight: 600; white-space: nowrap; }
.badge { padding: 5px 9px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.pendiente { background: #fff3ce; color: #8a5a00; }
.aprobada { background: #dff7e9; color: #166534; }
.rechazada { background: #fee2e2; color: #991b1b; }
.vendida { background: #e8edf0; color: var(--color-navy-2); }
.actions { vertical-align: top; white-space: nowrap; }
.actions button { display: inline-flex; align-items: center; gap: 4px; border: none; border-radius: 7px; padding: 6px 9px; font-size: 12px; font-weight: 700; transition: .3s ease; cursor: pointer; margin-right: 6px; }
.actions button:last-child { margin-right: 0; }
.actions button:hover { filter: brightness(1.02); transform: translateY(-1px); }
.view { background: #f7efe0; color: var(--color-navy-2); }
.edit { background: #e8edf0; color: var(--color-navy-2); }
.approve { background: #dff7e9; color: #166534; }
.reject { background: #fee2e2; color: #991b1b; }
.sold { background: #f2eadc; color: var(--color-navy-2); }
.delete { background: var(--color-navy); color: #fff; }
.state { display: flex; justify-content: center; padding: 40px; color: var(--color-muted); }
.error-msg { color: #991b1b; }
.spinner { width: 36px; height: 36px; border: 3px solid #eadfcf; border-top-color: var(--color-gold); border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; color: var(--color-muted); padding: 20px; }

.available-list { display: flex; flex-direction: column; gap: 10px; }
.available-row { display: flex; align-items: center; gap: 16px; padding: 14px 16px; border-radius: 10px; border: 1px solid var(--color-line); background: #fff; }
.prop-info { flex: 1; }
.prop-info strong { display: block; color: var(--color-navy); font-size: 14px; }
.prop-info span { display: block; margin-top: 4px; color: var(--color-muted); font-size: 12px; }
.prop-price { color: var(--color-navy); font-weight: 700; font-size: 14px; }
.take-btn { padding: 8px 16px; border-radius: 8px; background: var(--color-gold); color: var(--color-navy); font-weight: 600; border: none; cursor: pointer; transition: .2s; }
.take-btn:hover { filter: brightness(1.05); }

.clients-list { display: flex; flex-direction: column; gap: 10px; }
.client-row { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-radius: 10px; border: 1px solid var(--color-line); background: #fff; }
.client-info { flex: 1; }
.client-info strong { display: block; color: var(--color-navy); font-size: 14px; }
.client-info span { display: block; margin-top: 4px; color: var(--color-muted); font-size: 12px; }
.client-info small { display: block; margin-top: 4px; color: var(--color-muted); font-size: 11px; }
.client-stats { text-align: right; }
.property-count { display: inline-block; padding: 6px 12px; border-radius: 20px; background: #f7efe0; color: var(--color-navy-2); font-size: 12px; font-weight: 700; }

.pagination { display: flex; align-items: center; gap: 6px; margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--color-line); flex-wrap: wrap; }
.pagination button { padding: 6px 11px; border-radius: 999px; font-weight: 700; font-size: 13px; background: #fff; border: 1px solid rgba(7, 23, 45, .14); color: var(--color-muted); cursor: pointer; transition: .2s ease; }
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

.mobile-cards { display: none; }
.mobile-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; padding: 14px; }
.mc-header { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 10px; }
.mc-thumb { width: 48px; height: 48px; border-radius: 8px; object-fit: cover; background: #f0ece4; flex-shrink: 0; }
.mc-title-group { flex: 1; min-width: 0; }
.mc-title { display: block; color: var(--color-navy); font-size: 14px; }
.mc-owner { display: block; color: var(--color-muted); font-size: 12px; margin-top: 2px; }
.mc-email { display: block; color: var(--color-muted); font-size: 11px; }
.mc-body { display: flex; flex-direction: column; gap: 6px; padding: 8px 0; font-size: 13px; color: var(--color-navy); }
.mc-body span strong { color: var(--color-muted); font-weight: 600; }
.mc-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.mc-actions button { border: none; border-radius: 7px; padding: 6px 10px; font-size: 12px; font-weight: 700; cursor: pointer; font-family: inherit; }

@media (max-width: 900px) {
  .table-wrap table th:nth-child(4),
  .table-wrap table td:nth-child(4) { display: none; }
}
@media (max-width: 768px) {
  .table-wrap { display: none; }
  .mobile-cards { display: flex; flex-direction: column; gap: 12px; }
  .section-tabs { flex-wrap: wrap; }
  .section-tabs button { padding: 10px 14px; font-size: 13px; }
  .filters { flex-wrap: wrap; }
  .filters button { font-size: 12px; padding: 6px 10px; }
  .available-row { flex-direction: column; align-items: flex-start; gap: 10px; }
  .prop-price { font-size: 13px; }
  .take-btn { width: 100%; }
  .modal { padding: 24px 20px; }
  .modal h2 { font-size: 20px; }
}
@media (max-width: 480px) {
  .properties-advisor { gap: 12px; }
  .table-card { padding: 12px; }
  .pagination { justify-content: center; }
  .pagination-info { width: 100%; text-align: center; margin-left: 0; }
}
</style>

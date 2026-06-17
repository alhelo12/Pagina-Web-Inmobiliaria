<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { usersApi } from '@/api/users'
import { authApi } from '@/api/auth'
import { advisorsApi } from '@/api/advisors'
import { useAuthStore } from '@/stores/authStore'
import DashboardHeader from '@/components/shared/dashboard/DashboardHeader.vue'
import { useToast } from '@/composables/useToast'
import Breadcrumb from '@/components/shared/Breadcrumb.vue'

const { addToast } = useToast()
const auth = useAuthStore()
const route = useRoute()

const users = ref([])
const loading = ref(false)
const error = ref('')
const filterRole = ref('all')
const filterStatus = ref('all')
const search = ref('')
const debouncedSearch = ref('')
let searchTimeout = null

const page = ref(1)
const perPage = ref(20)
const totalItems = ref(0)

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
  load()
}

const showModal = ref(false)
const saving = ref(false)
const modalError = ref('')
const editingUser = ref(null)
const newUser = ref({ full_name: '', email: '', password: '', phone: '', role_name: 'advisor', license_number: '', agency_name: '' })

const confirmModal = ref({ show: false, type: '', user: null })

const actionLoading = ref(null)

const roleMap = { admin: 1, advisor: 2, client: 3 }
const roleLabel = { admin: 'Admin', advisor: 'Asesor', client: 'Cliente' }

const totalPages = computed(() => Math.max(1, Math.ceil(totalItems.value / perPage.value)))

const filtered = computed(() => {
  const q = debouncedSearch.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter(u =>
    u.full_name?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q)
  )
})

watch(search, (val) => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { debouncedSearch.value = val }, 300)
})

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = { skip: (page.value - 1) * perPage.value, limit: perPage.value }
    if (filterRole.value !== 'all') params.role_name = filterRole.value
    if (filterStatus.value === 'active') params.is_active = true
    else if (filterStatus.value === 'inactive') params.is_active = false
    if (sortKey.value) { params.sort_by = sortKey.value; params.sort_dir = sortDir.value }
    const { data } = await usersApi.getAll(params)
    users.value = data.users ?? data.items ?? data
    totalItems.value = data.total ?? users.value.length
  } catch (err) {
    console.error('[UsersView] load error:', err)
    error.value = err.response?.data?.detail ?? 'Error al cargar usuarios'
  } finally {
    loading.value = false
  }
}

const changeFilterRole = (f) => {
  filterRole.value = f
  page.value = 1
  load()
}

const changeFilterStatus = (f) => {
  filterStatus.value = f
  page.value = 1
  load()
}

const goToPage = (p) => {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  load()
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' })
}

const openModal = (user = null) => {
  if (user) {
    editingUser.value = user
    newUser.value = {
      full_name: user.full_name,
      email: user.email,
      phone: user.phone || '',
      password: '',
      role_name: user.role?.name || 'client',
      license_number: user.advisor?.license_number || '',
      agency_name: user.advisor?.agency_name || ''
    }
  } else {
    editingUser.value = null
    newUser.value = { full_name: '', email: '', password: '', phone: '', role_name: 'advisor', license_number: '', agency_name: '' }
  }
  modalError.value = ''
  showModal.value = true
}

const saveUser = async () => {
  modalError.value = ''
  if (!newUser.value.full_name.trim()) {
    modalError.value = 'El nombre completo es obligatorio'
    return
  }
  if (!/.+@.+\..+/.test(newUser.value.email)) {
    modalError.value = 'Email inválido'
    return
  }
  if (!editingUser.value && newUser.value.password.length < 6) {
    modalError.value = 'La contraseña debe tener al menos 6 caracteres'
    return
  }
  saving.value = true
  try {
    if (editingUser.value) {
      const payload = {
        full_name: newUser.value.full_name,
        email: newUser.value.email,
        phone: newUser.value.phone || undefined
      }
      if (newUser.value.password) payload.password = newUser.value.password
      const { data } = await usersApi.update(editingUser.value.id, payload)
      const idx = users.value.findIndex(u => u.id === editingUser.value.id)
      if (idx !== -1) users.value[idx] = data
      if (newUser.value.role_name === 'advisor' && editingUser.value.advisor?.id) {
        await advisorsApi.update(editingUser.value.advisor.id, {
          license_number: newUser.value.license_number || undefined,
          agency_name: newUser.value.agency_name || undefined
        })
      }
      showModal.value = false
      addToast({ message: 'Usuario actualizado correctamente', type: 'success' })
    } else {
      const { data } = await authApi.register({
        full_name: newUser.value.full_name,
        email: newUser.value.email,
        password: newUser.value.password,
        phone: newUser.value.phone || undefined,
        role_id: roleMap[newUser.value.role_name]
      })
      if (newUser.value.role_name === 'advisor') {
        await advisorsApi.create(data.id, {
          license_number: newUser.value.license_number || undefined,
          agency_name: newUser.value.agency_name || undefined
        })
      }
      users.value.push(data)
      totalItems.value++
      showModal.value = false
      addToast({ message: 'Usuario creado correctamente', type: 'success' })
    }
  } catch (err) {
    modalError.value = err.response?.data?.detail ?? 'Error al guardar usuario'
  } finally {
    saving.value = false
  }
}

const openConfirm = (type, user) => {
  confirmModal.value = { show: true, type, user }
}

const executeConfirm = async () => {
  const { type, user } = confirmModal.value
  confirmModal.value.show = false
  actionLoading.value = `${type}-${user.id}`
  try {
    if (type === 'delete') {
      await usersApi.remove(user.id)
      users.value = users.value.filter(u => u.id !== user.id)
      totalItems.value = Math.max(0, totalItems.value - 1)
      addToast({ message: 'Usuario eliminado correctamente', type: 'success' })
    } else if (type === 'toggle') {
      const { data } = user.is_active
        ? await usersApi.deactivate(user.id)
        : await usersApi.activate(user.id)
      const idx = users.value.findIndex(u => u.id === user.id)
      if (idx !== -1) users.value[idx] = data
      addToast({ message: `Usuario ${user.is_active ? 'desactivado' : 'activado'} correctamente`, type: 'success' })
    }
  } catch (err) {
    addToast({ message: err.response?.data?.detail ?? 'Error al ejecutar acción', type: 'error' })
  } finally {
    actionLoading.value = null
  }
}
onMounted(() => {
  if (route.query.role) {
    filterRole.value = route.query.role
  }
  load()
})

onUnmounted(() => { clearTimeout(searchTimeout) })
</script>

<template>
  <section class="admin-users">
    <DashboardHeader
      v-model:search="search"
      eyebrow="Equipo y clientes"
      title="Usuarios"
      :show-search="true"
      :show-export="false"
      :show-profile="true"
      add-label="Agregar usuario"
      search-placeholder="Buscar por nombre o email..."
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Admin'"
      :profile-email="auth.userEmail || ''"
      @add="openModal()"
    />

    <Breadcrumb :crumbs="[{ label: 'Usuarios', path: '/admin/usuarios' }]" />

    <div class="filters-bar">
      <div class="filters-group">
        <span class="filter-label">Rol:</span>
        <div class="filters">
          <button :class="{ active: filterRole === 'all' }" @click="changeFilterRole('all')">Todos</button>
          <button :class="{ active: filterRole === 'admin' }" @click="changeFilterRole('admin')">Administradores</button>
          <button :class="{ active: filterRole === 'advisor' }" @click="changeFilterRole('advisor')">Asesores</button>
          <button :class="{ active: filterRole === 'client' }" @click="changeFilterRole('client')">Clientes</button>
        </div>
      </div>
      <div class="filters-group">
        <span class="filter-label">Estado:</span>
        <div class="filters">
          <button :class="{ active: filterStatus === 'all' }" @click="changeFilterStatus('all')">Todos</button>
          <button :class="{ active: filterStatus === 'active' }" @click="changeFilterStatus('active')">Activos</button>
          <button :class="{ active: filterStatus === 'inactive' }" @click="changeFilterStatus('inactive')">Inactivos</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="state"><div class="spinner"></div></div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <div v-else class="table-container">
      <table>
          <thead>
            <tr>
              <th class="sortable" @click="sort('full_name')">
                Nombre <span class="sort-icon" :class="{ active: sortKey === 'full_name' }">{{ sortKey === 'full_name' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span>
              </th>
              <th>Email</th>
              <th>Teléfono</th>
              <th class="sortable" @click="sort('role_name')">
                Rol <span class="sort-icon" :class="{ active: sortKey === 'role_name' }">{{ sortKey === 'role_name' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span>
              </th>
              <th class="sortable" @click="sort('is_active')">
                Estado <span class="sort-icon" :class="{ active: sortKey === 'is_active' }">{{ sortKey === 'is_active' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span>
              </th>
              <th class="sortable" @click="sort('created_at')">
                Creación <span class="sort-icon" :class="{ active: sortKey === 'created_at' }">{{ sortKey === 'created_at' ? (sortDir === 'asc' ? '↑' : '↓') : '↕' }}</span>
              </th>
              <th>Acciones</th>
            </tr>
          </thead>
        <tbody>
          <tr v-for="u in filtered" :key="u.id">
            <td class="td-name">{{ u.full_name }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.phone ?? '-' }}</td>
            <td><span class="role-badge">{{ roleLabel[u.role?.name] ?? u.role?.name }}</span></td>
            <td><span :class="['status', u.is_active ? 'on' : 'off']">{{ u.is_active ? 'Activo' : 'Inactivo' }}</span></td>
            <td class="td-date">{{ formatDate(u.created_at) }}</td>
            <td class="actions">
              <button class="edit" :disabled="actionLoading" @click="openModal(u)">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                Editar
              </button>
              <button class="toggle" :disabled="actionLoading === `toggle-${u.id}`" @click="openConfirm('toggle', u)">
                {{ actionLoading === `toggle-${u.id}` ? '...' : u.is_active ? 'Desactivar' : 'Activar' }}
              </button>
              <button class="delete" :disabled="actionLoading === `delete-${u.id}`" @click="openConfirm('delete', u)">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                Eliminar
              </button>
            </td>
          </tr>
          <tr v-if="!filtered.length">
            <td colspan="7" class="empty">Sin usuarios</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile cards -->
    <div class="mobile-cards">
      <div v-for="u in filtered" :key="u.id" class="mobile-card">
        <div class="mc-header">
          <div class="mc-avatar">{{ u.full_name?.charAt(0) }}</div>
          <div class="mc-title-group">
            <strong class="mc-name">{{ u.full_name }}</strong>
            <span class="mc-email">{{ u.email }}</span>
            <small class="mc-phone">{{ u.phone ?? 'Sin teléfono' }}</small>
          </div>
          <span :class="['status', u.is_active ? 'on' : 'off']">{{ u.is_active ? 'Activo' : 'Inactivo' }}</span>
        </div>
        <div class="mc-body">
          <span><strong>Rol:</strong> <span class="role-badge">{{ roleLabel[u.role?.name] ?? u.role?.name }}</span></span>
          <span><strong>Creación:</strong> {{ formatDate(u.created_at) }}</span>
        </div>
        <div class="mc-actions">
          <button class="edit" :disabled="actionLoading" @click="openModal(u)">Editar</button>
          <button class="toggle" :disabled="actionLoading === `toggle-${u.id}`" @click="openConfirm('toggle', u)">{{ u.is_active ? 'Desactivar' : 'Activar' }}</button>
          <button class="delete" :disabled="actionLoading === `delete-${u.id}`" @click="openConfirm('delete', u)">Eliminar</button>
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
      <span class="pagination-info">{{ filtered.length }} de {{ totalItems }} usuarios</span>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h2>{{ editingUser ? 'Editar usuario' : 'Agregar usuario' }}</h2>
        <div v-if="modalError" class="alert-error">{{ modalError }}</div>
        <div class="form">
          <div class="field">
            <label for="user-name">Nombre completo</label>
            <input id="user-name" v-model="newUser.full_name" placeholder="Nombre completo" autocomplete="name" />
          </div>
          <div class="field">
            <label for="user-email">Correo electrónico</label>
            <input id="user-email" v-model="newUser.email" type="email" placeholder="Correo electrónico" autocomplete="email" />
          </div>
          <div class="field">
            <label for="user-phone">Teléfono opcional</label>
            <input id="user-phone" v-model="newUser.phone" type="tel" placeholder="Teléfono opcional" autocomplete="tel" />
          </div>
          <div class="field">
            <label for="user-password">{{ editingUser ? 'Nueva contraseña (dejar vacío si no cambia)' : 'Contraseña' }}</label>
            <input id="user-password" v-model="newUser.password" type="password" :placeholder="editingUser ? 'Nueva contraseña (dejar vacío si no cambia)' : 'Contraseña'" autocomplete="new-password" />
          </div>
          <div class="field">
            <label for="user-role">Rol</label>
            <select id="user-role" v-model="newUser.role_name" :disabled="!!editingUser">
              <option value="client">Cliente</option>
              <option value="advisor">Asesor</option>
              <option value="admin">Administrador</option>
            </select>
          </div>
          <template v-if="newUser.role_name === 'advisor'">
            <div class="field">
              <label for="user-license">Número de licencia</label>
              <input id="user-license" v-model="newUser.license_number" placeholder="Número de licencia" autocomplete="off" />
            </div>
            <div class="field">
              <label for="user-agency">Nombre de la agencia</label>
              <input id="user-agency" v-model="newUser.agency_name" placeholder="Nombre de la agencia" autocomplete="off" />
            </div>
          </template>
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showModal = false">Cancelar</button>
          <button class="btn-save" :disabled="saving" @click="saveUser">
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="confirmModal.show" class="modal-overlay" @click.self="confirmModal.show = false">
        <div class="modal">
          <h2>{{ confirmModal.type === 'delete' ? 'Eliminar usuario' : confirmModal.user?.is_active ? 'Desactivar usuario' : 'Activar usuario' }}</h2>
          <p class="modal-desc" v-if="confirmModal.type === 'delete'">
            ¿Eliminar permanentemente a <strong>{{ confirmModal.user?.full_name }}</strong>? Esta acción no se puede deshacer.
          </p>
          <p class="modal-desc" v-else>
            ¿{{ confirmModal.user?.is_active ? 'desactivar' : 'activar' }} a <strong>{{ confirmModal.user?.full_name }}</strong>?
          </p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="confirmModal.show = false">Cancelar</button>
            <button :class="['btn-confirm', confirmModal.type === 'delete' ? 'remove' : 'toggle']" @click="executeConfirm">
              {{ confirmModal.type === 'delete' ? 'Eliminar' : confirmModal.user?.is_active ? 'Desactivar' : 'Activar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </section>
</template>

<style scoped>
.admin-users { display: grid; gap: 18px; }

.filters-bar { display: flex; gap: 20px; flex-wrap: wrap; padding: 14px 18px; background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); }
.filters-group { display: flex; align-items: center; gap: 10px; }
.filter-label { font-size: 13px; font-weight: 700; color: #65717e; white-space: nowrap; }
.filters { display: flex; gap: 8px; flex-wrap: wrap; }
.filters button { padding: 9px 14px; border-radius: 999px; border: 1px solid rgba(7,23,45,.12); background: white; color: #40566e; font-weight: 800; cursor: pointer; transition: .3s ease; }
.filters button.active { background: #07172d; color: white; }

.state { display: flex; justify-content: center; padding: 40px; color: #65717e; }
.error-msg { color: #991b1b; }
.spinner { width: 36px; height: 36px; border: 3px solid #eadfcf; border-top-color: #d6a848; border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.table-container {
  width: 100%;
  background: #fffdf8;
  border-radius: 10px;
  box-shadow: var(--shadow-soft);
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  scrollbar-color: rgba(16, 46, 79, .35) transparent;
}
.table-container::-webkit-scrollbar { height: 8px; }
.table-container::-webkit-scrollbar-thumb { background: rgba(16, 46, 79, .35); border-radius: 999px; }
table { width: max(100%, 980px); border-collapse: collapse; table-layout: auto; }
th, td { padding: 15px 16px; text-align: left; font-size: 14px; border-bottom: 1px solid #eee7dc; }
th { color: #65717e; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; white-space: nowrap; vertical-align: middle; }
td { vertical-align: top; }
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: var(--color-navy); }
.sort-icon { margin-left: 4px; font-size: 10px; opacity: .4; }
.sort-icon.active { opacity: 1; color: var(--color-gold); }
tr:hover { background: rgba(214, 168, 72, .05); }
.td-name { font-weight: 900; color: #07172d; min-width: 220px; white-space: normal; }
.td-date { color: #65717e; font-size: 13px; }
.empty { text-align: center; color: #999; padding: 30px !important; }

.role-badge, .status { padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 900; }
.role-badge { background: #eef4fb; color: #40566e; }
.status.on { background: #dff7e9; color: #166534; }
.status.off { background: #fee2e2; color: #991b1b; }

.actions { vertical-align: top; white-space: nowrap; }
.actions button { display: inline-flex; align-items: center; gap: 4px; padding: 7px 10px; border-radius: 7px; font-weight: 900; border: none; cursor: pointer; transition: .3s ease; margin-right: 6px; }
.actions button:last-child { margin-right: 0; }
.actions button:hover { filter: brightness(1.05); }
.edit { background: #e8edf0; color: #102e4f; }
.toggle { background: #eef4fb; color: #102e4f; }
.delete { background: #07172d; color: white; }

.pagination { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.pagination button { padding: 6px 11px; border-radius: 7px; font-weight: 700; font-size: 13px; background: #fff; border: 1px solid rgba(7, 23, 45, .14); color: #65717e; cursor: pointer; transition: .2s ease; }
.pagination button:hover:not(:disabled) { border-color: #07172d; color: #07172d; }
.pagination button.active { background: #07172d; color: #fff; border-color: #07172d; }
.pagination button:disabled { opacity: .4; cursor: not-allowed; }
.pagination .dots { color: #65717e; font-size: 13px; padding: 0 2px; }
.pagination-info { margin-left: auto; color: #65717e; font-size: 13px; }

.modal-overlay { position: fixed; inset: 0; background: rgba(7,23,45,.56); display: flex; align-items: center; justify-content: center; z-index: 2000; padding: 20px; }
.modal { background: #fffdf8; border-radius: 10px; padding: 30px; width: 100%; max-width: 460px; box-shadow: var(--shadow-strong); }
.modal h2 { font-family: 'Poppins', sans-serif; color: #07172d; font-size: 26px; margin-bottom: 18px; }
.modal-desc { color: #65717e; line-height: 1.6; margin-bottom: 24px; }
.alert-error { background: #fee2e2; color: #991b1b; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 14px; }
.form { display: grid; gap: 14px; margin-bottom: 24px; }
.field { display: grid; gap: 5px; }
.field label { font-size: 13px; font-weight: 700; color: var(--color-navy); }
.form input, .form select { padding: 12px; border-radius: 8px; border: 1px solid #d9d2c5; background: white; font: inherit; }
.form input:focus, .form select:focus { outline: none; border-color: #d6a848; }
.form select:disabled { opacity: .5; cursor: not-allowed; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
.btn-cancel { padding: 0 18px; min-height: 44px; background: #eee7dc; border-radius: 8px; color: #40566e; font-weight: 900; cursor: pointer; border: none; }
.btn-save { min-height: 44px; padding: 0 18px; background: #d6a848; color: #07172d; border-radius: 8px; font-weight: 900; cursor: pointer; border: none; }
.btn-save:disabled { opacity: .6; cursor: not-allowed; }
.btn-confirm { padding: 0 18px; min-height: 44px; border-radius: 8px; font-weight: 900; cursor: pointer; border: none; }
.btn-confirm.remove { background: #07172d; color: #fff; }
.btn-confirm.toggle { background: #eef4fb; color: #102e4f; }

.mobile-cards { display: none; }
.mobile-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; padding: 14px; }
.mc-header { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 10px; }
.mc-avatar { width: 42px; height: 42px; border-radius: 50%; background: var(--color-navy); color: var(--color-gold); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; flex-shrink: 0; }
.mc-title-group { flex: 1; min-width: 0; }
.mc-name { display: block; color: var(--color-navy); font-size: 14px; }
.mc-email { display: block; color: var(--color-muted); font-size: 12px; margin-top: 2px; word-break: break-all; }
.mc-phone { display: block; color: var(--color-muted); font-size: 11px; }
.mc-body { display: flex; flex-direction: column; gap: 6px; padding: 8px 0; font-size: 13px; color: var(--color-navy); }
.mc-body span strong { color: var(--color-muted); font-weight: 600; }
.mc-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.mc-actions button { border: none; border-radius: 7px; padding: 6px 10px; font-size: 12px; font-weight: 700; cursor: pointer; font-family: inherit; }

@media (max-width: 900px) {
  .table-container table th:nth-child(3),
  .table-container table td:nth-child(3),
  .table-container table th:nth-child(6),
  .table-container table td:nth-child(6) { display: none; }
}
@media (max-width: 768px) {
  .table-container { display: none; }
  .mobile-cards { display: flex; flex-direction: column; gap: 12px; }
}
@media (max-width: 640px) {
  .filters-bar { flex-direction: column; align-items: stretch; gap: 12px; }
  .filters-group { flex-wrap: wrap; }
  .filters button { font-size: 12px; padding: 7px 10px; }
  .pagination-info { width: 100%; text-align: center; margin-left: 0; }
  .modal { padding: 24px 20px; }
  .modal h2 { font-size: 20px; }
  .modal-actions { flex-direction: column; }
  .btn-cancel, .btn-confirm, .btn-save { width: 100%; justify-content: center; }
}
</style>

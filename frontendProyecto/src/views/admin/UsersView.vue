<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { usersApi } from '@/api/users'
import { authApi } from '@/api/auth'
import { advisorsApi } from '@/api/advisors'
import { useAuthStore } from '@/stores/authStore'
import AdminDashboardHeader from '@/components/admin/dashboard/AdminDashboardHeader.vue'
import Toast from '@/components/shared/Toast.vue'

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

const showModal = ref(false)
const saving = ref(false)
const modalError = ref('')
const editingUser = ref(null)
const newUser = ref({ full_name: '', email: '', password: '', phone: '', role_name: 'advisor', license_number: '', agency_name: '' })

const confirmModal = ref({ show: false, type: '', user: null })

const toastState = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

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

const showToast = (message, type = 'success') => {
  clearTimeout(toastTimeout)
  toastState.value = { show: true, message, type }
  toastTimeout = setTimeout(() => { toastState.value.show = false }, 3000)
}

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
      showToast('Usuario actualizado correctamente')
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
      showToast('Usuario creado correctamente')
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
  try {
    if (type === 'delete') {
      await usersApi.remove(user.id)
      users.value = users.value.filter(u => u.id !== user.id)
      totalItems.value = Math.max(0, totalItems.value - 1)
      showToast('Usuario eliminado correctamente')
    } else if (type === 'toggle') {
      const { data } = user.is_active
        ? await usersApi.deactivate(user.id)
        : await usersApi.activate(user.id)
      const idx = users.value.findIndex(u => u.id === user.id)
      if (idx !== -1) users.value[idx] = data
      showToast(`Usuario ${user.is_active ? 'desactivado' : 'activado'} correctamente`)
    }
  } catch (err) {
    showToast(err.response?.data?.detail ?? 'Error al ejecutar acción', 'error')
  }
}
onMounted(() => {
  if (route.query.role) {
    filterRole.value = route.query.role
  }
  load()
})

onUnmounted(() => { clearTimeout(searchTimeout); clearTimeout(toastTimeout) })
</script>

<template>
  <section class="admin-users">
    <AdminDashboardHeader
      v-model:search="search"
      eyebrow="Equipo y clientes"
      title="Usuarios"
      add-label="Agregar usuario"
      search-placeholder="Buscar por nombre o email..."
      :show-export="false"
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Admin'"
      :profile-email="auth.userEmail || ''"
      @add="openModal()"
    />

    <div class="filters-group">
      <div class="filter-label">Rol:</div>
      <div class="filters">
        <button :class="{ active: filterRole === 'all' }" @click="changeFilterRole('all')">Todos</button>
        <button :class="{ active: filterRole === 'admin' }" @click="changeFilterRole('admin')">Administradores</button>
        <button :class="{ active: filterRole === 'advisor' }" @click="changeFilterRole('advisor')">Asesores</button>
        <button :class="{ active: filterRole === 'client' }" @click="changeFilterRole('client')">Clientes</button>
      </div>
    </div>
    <div class="filters-group">
      <div class="filter-label">Estado:</div>
      <div class="filters">
        <button :class="{ active: filterStatus === 'all' }" @click="changeFilterStatus('all')">Todos</button>
        <button :class="{ active: filterStatus === 'active' }" @click="changeFilterStatus('active')">Activos</button>
        <button :class="{ active: filterStatus === 'inactive' }" @click="changeFilterStatus('inactive')">Inactivos</button>
      </div>
    </div>

    <div v-if="loading" class="state"><div class="spinner"></div></div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th>Nombre</th><th>Email</th><th>Teléfono</th>
            <th>Rol</th><th>Estado</th><th>Creación</th><th>Acciones</th>
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
              <button class="edit" @click="openModal(u)">Editar</button>
              <button class="toggle" @click="openConfirm('toggle', u)">
                {{ u.is_active ? 'Desactivar' : 'Activar' }}
              </button>
              <button class="delete" @click="openConfirm('delete', u)">Eliminar</button>
            </td>
          </tr>
          <tr v-if="!filtered.length">
            <td colspan="7" class="empty">Sin usuarios</td>
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
      <span class="pagination-info">{{ filtered.length }} de {{ totalItems }} usuarios</span>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h2>{{ editingUser ? 'Editar usuario' : 'Agregar usuario' }}</h2>
        <div v-if="modalError" class="alert-error">{{ modalError }}</div>
        <div class="form">
          <input v-model="newUser.full_name" placeholder="Nombre completo" autocomplete="name" />
          <input v-model="newUser.email" type="email" placeholder="Correo electrónico" autocomplete="email" />
          <input v-model="newUser.phone" type="tel" placeholder="Teléfono opcional" autocomplete="tel" />
          <input v-model="newUser.password" type="password" :placeholder="editingUser ? 'Nueva contraseña (dejar vacío si no cambia)' : 'Contraseña'" autocomplete="new-password" />
          <select v-model="newUser.role_name" :disabled="!!editingUser" autocomplete="off">
            <option value="client">Cliente</option>
            <option value="advisor">Asesor</option>
            <option value="admin">Administrador</option>
          </select>
          <template v-if="newUser.role_name === 'advisor'">
            <input v-model="newUser.license_number" placeholder="Número de licencia" autocomplete="off" />
            <input v-model="newUser.agency_name" placeholder="Nombre de la agencia" autocomplete="off" />
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

    <Toast :visible="toastState.show" :message="toastState.message" :type="toastState.type" @close="toastState.show = false" />
  </section>
</template>

<style scoped>
.admin-users { display: grid; gap: 18px; }

.filters-group { display: flex; align-items: center; gap: 10px; }
.filter-label { font-size: 13px; font-weight: 700; color: #65717e; }
.filters { display: flex; gap: 10px; flex-wrap: wrap; }
.filters button { padding: 9px 14px; border-radius: 999px; border: 1px solid rgba(7,23,45,.12); background: white; color: #40566e; font-weight: 800; cursor: pointer; transition: .3s ease; }
.filters button.active { background: #07172d; color: white; }

.state { display: flex; justify-content: center; padding: 40px; color: #65717e; }
.error-msg { color: #991b1b; }
.spinner { width: 36px; height: 36px; border: 3px solid #eadfcf; border-top-color: #d6a848; border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.table-container { background: #fffdf8; border-radius: 10px; box-shadow: var(--shadow-soft); overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 15px 16px; text-align: left; font-size: 14px; border-bottom: 1px solid #eee7dc; }
th { color: #65717e; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
.td-name { font-weight: 900; color: #07172d; }
.td-date { color: #65717e; font-size: 13px; }
.empty { text-align: center; color: #999; padding: 30px !important; }

.role-badge, .status { padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 900; }
.role-badge { background: #eef4fb; color: #40566e; }
.status.on { background: #dff7e9; color: #166534; }
.status.off { background: #fee2e2; color: #991b1b; }

.actions { display: flex; gap: 8px; }
.actions button { padding: 7px 10px; border-radius: 7px; font-weight: 900; border: none; cursor: pointer; transition: .3s ease; }
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
.form { display: grid; gap: 12px; margin-bottom: 24px; }
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
</style>

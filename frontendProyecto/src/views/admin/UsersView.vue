<script setup>
import { ref, computed, onMounted } from 'vue'
import { usersApi } from '@/api/users'
import { authApi } from '@/api/auth'

const users   = ref([])
const loading = ref(false)
const error   = ref('')
const filter  = ref('all')

// Modal nuevo usuario
const showModal  = ref(false)
const saving     = ref(false)
const modalError = ref('')
const newUser = ref({ full_name: '', email: '', password: '', phone: '', role_name: 'advisor' })

const filtered = computed(() => {
  if (filter.value === 'active')   return users.value.filter(u => u.is_active)
  if (filter.value === 'inactive') return users.value.filter(u => !u.is_active)
  return users.value
})

const load = async () => {
  loading.value = true
  error.value   = ''
  try {
    const { data } = await usersApi.getAll()
    // El backend devuelve { total, page, per_page, users: [...] }
    users.value = data.users ?? data.items ?? data
  } catch {
    error.value = 'Error al cargar usuarios'
  } finally {
    loading.value = false
  }
}

const toggleActive = async (user) => {
  try {
    const { data } = user.is_active
      ? await usersApi.deactivate(user.id)
      : await usersApi.activate(user.id)
    const idx = users.value.findIndex(u => u.id === user.id)
    if (idx !== -1) users.value[idx] = data
  } catch {
    alert('Error al actualizar usuario')
  }
}

const deleteUser = async (id) => {
  if (!window.confirm('¿Eliminar este usuario permanentemente?')) return
  try {
    await usersApi.remove(id)
    users.value = users.value.filter(u => u.id !== id)
  } catch {
    alert('Error al eliminar usuario')
  }
}

const openModal = () => {
  newUser.value  = { full_name: '', email: '', password: '', phone: '', role_name: 'advisor' }
  modalError.value = ''
  showModal.value  = true
}

const roleMap = { admin: 1, advisor: 2, client: 3 }

const saveUser = async () => {
  modalError.value = ''
  saving.value     = true
  try {
    // /auth/register acepta role_id — correcto para admin/advisor/client
    const { data } = await authApi.register({
      full_name: newUser.value.full_name,
      email:     newUser.value.email,
      password:  newUser.value.password,
      phone:     newUser.value.phone || undefined,
      role_id:   roleMap[newUser.value.role_name]
    })
    // Nota: register/client siempre asigna rol client; para admin/advisor
    // el backend tiene /auth/register que acepta role_id
    users.value.push(data)
    showModal.value = false
  } catch (err) {
    modalError.value = err.response?.data?.detail ?? 'Error al crear usuario'
  } finally {
    saving.value = false
  }
}

const roleLabel = { admin: 'Admin', advisor: 'Asesor', client: 'Cliente' }

onMounted(load)
</script>

<template>
  <section class="admin-users">
    <div class="header">
      <h1>Usuarios</h1>
      <button class="btn-add" @click="openModal">+ Agregar usuario</button>
    </div>

    <div class="filters">
      <button :class="{ active: filter==='all' }"      @click="filter='all'">Todos</button>
      <button :class="{ active: filter==='active' }"   @click="filter='active'">Activos</button>
      <button :class="{ active: filter==='inactive' }" @click="filter='inactive'">Inactivos</button>
    </div>

    <div v-if="loading" class="state"><div class="spinner"></div></div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th>Nombre</th><th>Email</th><th>Teléfono</th>
            <th>Rol</th><th>Estado</th><th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in filtered" :key="u.id">
            <td class="td-name">{{ u.full_name }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.phone ?? '—' }}</td>
            <td><span class="role-badge">{{ roleLabel[u.role?.name] ?? u.role?.name }}</span></td>
            <td>
              <span :class="['status', u.is_active ? 'on' : 'off']">
                {{ u.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="actions">
              <button class="toggle" @click="toggleActive(u)">
                {{ u.is_active ? 'Desactivar' : 'Activar' }}
              </button>
              <button class="delete" @click="deleteUser(u.id)">Eliminar</button>
            </td>
          </tr>
          <tr v-if="!filtered.length">
            <td colspan="6" class="empty">Sin usuarios</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- MODAL NUEVO USUARIO -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h2>Agregar usuario</h2>

        <div v-if="modalError" class="alert-error">{{ modalError }}</div>

        <div class="form">
          <input v-model="newUser.full_name" placeholder="Nombre completo" required />
          <input v-model="newUser.email"     type="email" placeholder="Correo electrónico" required />
          <input v-model="newUser.phone"     type="tel"   placeholder="Teléfono (opcional)" />
          <input v-model="newUser.password"  type="password" placeholder="Contraseña" required />

          <select v-model="newUser.role_name">
            <option value="client">Cliente</option>
            <option value="advisor">Asesor</option>
            <option value="admin">Administrador</option>
          </select>
        </div>

        <div class="modal-actions">
          <button class="btn-cancel" @click="showModal = false">Cancelar</button>
          <button class="btn-save" :disabled="saving" @click="saveUser">
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.admin-users { padding: 40px; font-family: 'Poppins', sans-serif; }

.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
h1 { font-size: 26px; margin: 0; }

.btn-add {
  background: #0d2c54; color: white; border: none;
  padding: 10px 20px; border-radius: 8px; cursor: pointer;
  font-weight: 600; font-family: inherit; transition: background .2s;
}
.btn-add:hover { background: #1e3a5f; }

.filters { display: flex; gap: 10px; margin-bottom: 20px; }
.filters button {
  padding: 8px 14px; border-radius: 20px; border: 1px solid #ddd;
  background: white; cursor: pointer; font-family: inherit; transition: .2s;
}
.filters button.active { background: #111; color: white; border-color: #111; }

.state { display: flex; justify-content: center; padding: 40px; color: #666; }
.error-msg { color: #991b1b; }
.spinner {
  width: 36px; height: 36px; border: 3px solid #f3f3f3;
  border-top-color: #f59e0b; border-radius: 50%; animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.table-container { background: white; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,.06); overflow: hidden; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 16px; text-align: left; font-size: 14px; }
thead { background: #f9fafb; }
tr:not(:last-child) { border-bottom: 1px solid #eee; }
.td-name { font-weight: 600; }
.empty { text-align: center; color: #999; padding: 30px !important; }

.role-badge { background: #f3f4f6; padding: 3px 10px; border-radius: 12px; font-size: 12px; }

.status { padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
.status.on  { background: #dcfce7; color: #166534; }
.status.off { background: #fee2e2; color: #991b1b; }

.actions { display: flex; gap: 8px; }
.actions button { border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 13px; font-family: inherit; }
.toggle { background: #e5e7eb; }
.delete { background: #ef4444; color: white; }

/* MODAL */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.modal {
  background: white; border-radius: 16px; padding: 32px;
  width: 100%; max-width: 440px; box-shadow: 0 20px 60px rgba(0,0,0,.2);
}
.modal h2 { font-size: 20px; margin-bottom: 20px; }

.alert-error {
  background: #fee2e2; color: #991b1b;
  padding: 10px 14px; border-radius: 8px;
  font-size: 13px; margin-bottom: 14px;
}

.form { display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px; }
.form input, .form select {
  padding: 11px 12px; border-radius: 8px; border: 1px solid #ddd;
  font-size: 14px; font-family: inherit;
}
.form input:focus, .form select:focus { outline: none; border-color: #f59e0b; }

.modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
.btn-cancel {
  padding: 10px 18px; background: #f3f4f6; border: none;
  border-radius: 8px; cursor: pointer; font-family: inherit;
}
.btn-save {
  padding: 10px 20px; background: #f59e0b; color: white;
  border: none; border-radius: 8px; cursor: pointer;
  font-weight: 600; font-family: inherit;
}
.btn-save:disabled { opacity: .6; cursor: not-allowed; }
</style>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usersApi } from '@/api/users'
import { authApi } from '@/api/auth'

const users = ref([])
const loading = ref(false)
const error = ref('')
const filter = ref('all')
const showModal = ref(false)
const saving = ref(false)
const modalError = ref('')
const newUser = ref({ full_name: '', email: '', password: '', phone: '', role_name: 'advisor' })

const filtered = computed(() => {
  if (filter.value === 'active') return users.value.filter(u => u.is_active)
  if (filter.value === 'inactive') return users.value.filter(u => !u.is_active)
  return users.value
})

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await usersApi.getAll()
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
  if (!window.confirm('Eliminar este usuario permanentemente?')) return
  try {
    await usersApi.remove(id)
    users.value = users.value.filter(u => u.id !== id)
  } catch {
    alert('Error al eliminar usuario')
  }
}

const openModal = () => {
  newUser.value = { full_name: '', email: '', password: '', phone: '', role_name: 'advisor' }
  modalError.value = ''
  showModal.value = true
}

const roleMap = { admin: 1, advisor: 2, client: 3 }
const roleLabel = { admin: 'Admin', advisor: 'Asesor', client: 'Cliente' }

const saveUser = async () => {
  modalError.value = ''
  saving.value = true
  try {
    const { data } = await authApi.register({
      full_name: newUser.value.full_name,
      email: newUser.value.email,
      password: newUser.value.password,
      phone: newUser.value.phone || undefined,
      role_id: roleMap[newUser.value.role_name]
    })
    users.value.push(data)
    showModal.value = false
  } catch (err) {
    modalError.value = err.response?.data?.detail ?? 'Error al crear usuario'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="admin-users">
    <div class="header">
      <div>
        <p>Equipo y clientes</p>
        <h1>Usuarios</h1>
      </div>
      <button class="btn-add" @click="openModal">Agregar usuario</button>
    </div>

    <div class="filters">
      <button :class="{ active: filter==='all' }" @click="filter='all'">Todos</button>
      <button :class="{ active: filter==='active' }" @click="filter='active'">Activos</button>
      <button :class="{ active: filter==='inactive' }" @click="filter='inactive'">Inactivos</button>
    </div>

    <div v-if="loading" class="state"><div class="spinner"></div></div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th>Nombre</th><th>Email</th><th>Telefono</th>
            <th>Rol</th><th>Estado</th><th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in filtered" :key="u.id">
            <td class="td-name">{{ u.full_name }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.phone ?? '-' }}</td>
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

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h2>Agregar usuario</h2>
        <div v-if="modalError" class="alert-error">{{ modalError }}</div>
        <div class="form">
          <input v-model="newUser.full_name" placeholder="Nombre completo" required />
          <input v-model="newUser.email" type="email" placeholder="Correo electronico" required />
          <input v-model="newUser.phone" type="tel" placeholder="Telefono opcional" />
          <input v-model="newUser.password" type="password" placeholder="Contrasena" required />
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
.admin-users {
  display: grid;
  gap: 22px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  padding: 28px;
  border-radius: 16px;
  background: #fffdf8;
  box-shadow: var(--shadow-soft);
}

.header p {
  color: #d6a848;
  font-weight: 900;
  letter-spacing: .16em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

h1,
h2 {
  font-family: Georgia, 'Times New Roman', serif;
  color: #07172d;
}

h1 {
  font-size: 42px;
}

.btn-add,
.btn-save {
  min-height: 44px;
  padding: 0 18px;
  background: #d6a848;
  color: #07172d;
  border-radius: 8px;
  font-weight: 900;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filters button {
  padding: 9px 14px;
  border-radius: 999px;
  border: 1px solid rgba(7,23,45,.12);
  background: white;
  color: #40566e;
  font-weight: 800;
}

.filters button.active {
  background: #07172d;
  color: white;
}

.state {
  display: flex;
  justify-content: center;
  padding: 40px;
  color: #65717e;
}
.error-msg { color: #991b1b; }
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #eadfcf;
  border-top-color: #d6a848;
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.table-container {
  background: #fffdf8;
  border-radius: 16px;
  box-shadow: var(--shadow-soft);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 15px 16px;
  text-align: left;
  font-size: 14px;
  border-bottom: 1px solid #eee7dc;
}

th {
  color: #65717e;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .08em;
}

.td-name {
  font-weight: 900;
  color: #07172d;
}

.empty {
  text-align: center;
  color: #999;
  padding: 30px !important;
}

.role-badge,
.status {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.role-badge { background: #eef4fb; color: #40566e; }
.status.on { background: #dff7e9; color: #166534; }
.status.off { background: #fee2e2; color: #991b1b; }

.actions {
  display: flex;
  gap: 8px;
}
.actions button {
  padding: 7px 10px;
  border-radius: 7px;
  font-weight: 900;
}
.toggle { background: #eef4fb; color: #102e4f; }
.delete { background: #07172d; color: white; }

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(7,23,45,.56);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal {
  background: #fffdf8;
  border-radius: 16px;
  padding: 30px;
  width: 100%;
  max-width: 460px;
  box-shadow: var(--shadow-strong);
}

.modal h2 {
  font-size: 26px;
  margin-bottom: 18px;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 14px;
}

.form {
  display: grid;
  gap: 12px;
  margin-bottom: 24px;
}

.form input,
.form select {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #d9d2c5;
  background: white;
  font: inherit;
}

.form input:focus,
.form select:focus {
  outline: none;
  border-color: #d6a848;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-cancel {
  padding: 0 18px;
  min-height: 44px;
  background: #eee7dc;
  border-radius: 8px;
  color: #40566e;
  font-weight: 900;
}

.btn-save:disabled {
  opacity: .6;
  cursor: not-allowed;
}

@media (max-width: 680px) {
  .header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>

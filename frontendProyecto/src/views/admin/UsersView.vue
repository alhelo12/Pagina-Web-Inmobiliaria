<script setup>
import { ref, computed, onMounted } from 'vue'
import { usersApi } from '@/api/users'

const users   = ref([])
const loading = ref(false)
const error   = ref('')
const filter  = ref('all')

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
    users.value = data.items ?? data
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
  if (!window.confirm('¿Eliminar este usuario?')) return
  try {
    await usersApi.remove(id)
    users.value = users.value.filter(u => u.id !== id)
  } catch {
    alert('Error al eliminar usuario')
  }
}

const roleLabel = { admin: 'Admin', advisor: 'Asesor', client: 'Cliente' }

onMounted(load)
</script>

<template>
  <section class="admin-users">
    <h1>Usuarios</h1>

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
            <th>Nombre</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Acciones</th>
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
            <td colspan="6" style="text-align:center;color:#999;padding:30px">Sin usuarios</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.admin-users { padding: 40px; font-family: 'Poppins', sans-serif; }
h1 { margin-bottom: 20px; font-size: 26px; }

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

.role-badge { background: #f3f4f6; padding: 3px 10px; border-radius: 12px; font-size: 12px; }

.status { padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
.status.on  { background: #dcfce7; color: #166534; }
.status.off { background: #fee2e2; color: #991b1b; }

.actions { display: flex; gap: 8px; }
.actions button { border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 13px; font-family: inherit; }
.toggle { background: #e5e7eb; }
.delete { background: #ef4444; color: white; }
</style>

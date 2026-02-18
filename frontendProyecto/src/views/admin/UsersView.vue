<script setup>
import { ref, computed } from 'vue'

// ===== DATA DEMO =====
const users = ref([
  { id: 1, name: 'Juan Pérez', email: 'juan@mail.com', role: 'advisor', active: true },
  { id: 2, name: 'María López', email: 'maria@mail.com', role: 'client', active: true },
  { id: 3, name: 'Carlos Ruiz', email: 'carlos@mail.com', role: 'advisor', active: false }
])

// ===== FILTRO =====
const filter = ref('all')

const filteredUsers = computed(() => {
  if (filter.value === 'active') return users.value.filter(u => u.active)
  if (filter.value === 'inactive') return users.value.filter(u => !u.active)
  return users.value
})

// ===== ACTIONS =====
const toggleActive = (user) => {
  user.active = !user.active
}

const deleteUser = (id) => {
  users.value = users.value.filter(u => u.id !== id)
}
</script>

<template>
  <section class="admin-users">
    <h1>Usuarios</h1>

    <!-- ===== FILTROS ===== -->
    <div class="filters">
      <button :class="{ active: filter==='all' }" @click="filter='all'">Todos</button>
      <button :class="{ active: filter==='active' }" @click="filter='active'">Activos</button>
      <button :class="{ active: filter==='inactive' }" @click="filter='inactive'">Inactivos</button>
    </div>

    <!-- ===== TABLA ===== -->
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="u in filteredUsers" :key="u.id">
            <td>{{ u.name }}</td>
            <td>{{ u.email }}</td>
            <td class="role">{{ u.role }}</td>

            <td>
              <span :class="['status', u.active ? 'on' : 'off']">
                {{ u.active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>

            <td class="actions">
              <button class="toggle" @click="toggleActive(u)">
                {{ u.active ? 'Desactivar' : 'Activar' }}
              </button>

              <button class="delete" @click="deleteUser(u.id)">
                Eliminar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.admin-users {
  padding: 40px;
}

h1 {
  margin-bottom: 20px;
}

/* ===== FILTROS ===== */
.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.filters button {
  padding: 8px 14px;
  border-radius: 20px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
}

.filters button.active {
  background: #111;
  color: white;
  border-color: #111;
}

/* ===== TABLA ===== */
.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0,0,0,.06);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 14px 16px;
  text-align: left;
}

thead {
  background: #f9fafb;
}

tr:not(:last-child) {
  border-bottom: 1px solid #eee;
}

/* ===== ESTADO ===== */
.status {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status.on {
  background: #dcfce7;
  color: #166534;
}

.status.off {
  background: #fee2e2;
  color: #991b1b;
}

/* ===== ACCIONES ===== */
.actions {
  display: flex;
  gap: 8px;
}

button {
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.toggle {
  background: #e5e7eb;
}

.delete {
  background: #ef4444;
  color: white;
}
</style>

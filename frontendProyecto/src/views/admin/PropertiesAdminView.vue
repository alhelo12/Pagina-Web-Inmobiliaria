<script setup>
import { ref, computed, onMounted } from 'vue'

const properties = ref([])
const filter = ref('todos')

onMounted(() => {
  // 🔹 luego esto vendrá de tu API
  properties.value = [
    { id: 1, title: 'Casa moderna', city: 'Querétaro', price: 2500000, status: 'pendiente' },
    { id: 2, title: 'Departamento céntrico', city: 'CDMX', price: 1800000, status: 'aprobada' },
    { id: 3, title: 'Casa residencial', city: 'Monterrey', price: 3200000, status: 'rechazada' },
    { id: 4, title: 'Loft moderno', city: 'Guadalajara', price: 2100000, status: 'vendida' }
  ]
})

// ===== FILTRO =====
const filteredProperties = computed(() => {
  if (filter.value === 'todos') return properties.value
  return properties.value.filter(p => p.status === filter.value)
})

// ===== ACCIONES ADMIN =====
const approve = (p) => (p.status = 'aprobada')
const reject = (p) => (p.status = 'rechazada')
const sold = (p) => (p.status = 'vendida')
const remove = (id) => (properties.value = properties.value.filter(p => p.id !== id))
</script>

<template>
  <section class="admin">
    <h1>Administrar Propiedades</h1>

    <!-- ===== FILTROS SUPERIORES ===== -->
    <div class="filters">
      <button :class="{ active: filter === 'todos' }" @click="filter = 'todos'">Todos</button>
      <button :class="{ active: filter === 'pendiente' }" @click="filter = 'pendiente'">Pendientes</button>
      <button :class="{ active: filter === 'aprobada' }" @click="filter = 'aprobada'">Aprobadas</button>
      <button :class="{ active: filter === 'rechazada' }" @click="filter = 'rechazada'">Rechazadas</button>
      <button :class="{ active: filter === 'vendida' }" @click="filter = 'vendida'">Vendidas</button>
    </div>

    <!-- ===== TABLA ===== -->
    <table>
      <thead>
        <tr>
          <th>Título</th>
          <th>Ciudad</th>
          <th>Precio</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="p in filteredProperties" :key="p.id">
          <td>{{ p.title }}</td>
          <td>{{ p.city }}</td>
          <td>${{ p.price.toLocaleString() }}</td>

          <!-- ESTADO -->
          <td>
            <span :class="['badge', p.status]">{{ p.status }}</span>
          </td>

          <!-- ACCIONES -->
          <td class="actions">
            <button class="edit">Editar</button>
            <button class="delete" @click="remove(p.id)">Eliminar</button>

            <button v-if="p.status === 'pendiente'" class="approve" @click="approve(p)">Aprobar</button>
            <button v-if="p.status === 'pendiente'" class="reject" @click="reject(p)">Rechazar</button>
            <button v-if="p.status === 'aprobada'" class="sold" @click="sold(p)">Vendida</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.admin {
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
  flex-wrap: wrap;
}

.filters button {
  border: 1px solid #e5e7eb;
  background: white;
  padding: 8px 14px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  transition: 0.2s;
}

.filters button:hover {
  background: #f9fafb;
}

.filters button.active {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

/* ===== TABLA ===== */
table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
}

th,
td {
  padding: 14px;
  text-align: left;
}

thead {
  background: #f3f4f6;
}

tbody tr:hover {
  background: #fafafa;
}

/* ===== BADGES ===== */
.badge {
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.pendiente {
  background: #fef3c7;
  color: #92400e;
}

.aprobada {
  background: #dcfce7;
  color: #166534;
}

.rechazada {
  background: #fee2e2;
  color: #991b1b;
}

.vendida {
  background: #e0e7ff;
  color: #3730a3;
}

/* ===== BOTONES ===== */
.actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

button {
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}

.edit {
  background: #e5e7eb;
}

.delete {
  background: #fecaca;
}

.approve {
  background: #bbf7d0;
}

.reject {
  background: #fca5a5;
}

.sold {
  background: #c7d2fe;
}
</style>

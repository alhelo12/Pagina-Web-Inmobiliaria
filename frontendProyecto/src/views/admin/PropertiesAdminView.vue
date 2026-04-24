<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePropertyStore } from '@/stores/propertyStore'
import { storeToRefs } from 'pinia'

const store = usePropertyStore()
const { properties, loading, error } = storeToRefs(store)

const filter = ref('todos')

const statusMap = {
  pending:  { label: 'Pendiente', cls: 'pendiente' },
  approved: { label: 'Aprobada',  cls: 'aprobada'  },
  rejected: { label: 'Rechazada', cls: 'rechazada' },
  sold:     { label: 'Vendida',   cls: 'vendida'   }
}

const filtered = computed(() => {
  if (filter.value === 'todos') return properties.value
  return properties.value.filter(p => p.status === filter.value)
})

const confirm = async (action, id) => {
  if (!window.confirm('¿Confirmas esta acción?')) return
  await store[action](id)
}

onMounted(() => store.fetchProperties())
</script>

<template>
  <section class="admin">
    <h1>Administrar Propiedades</h1>

    <!-- FILTROS -->
    <div class="filters">
      <button :class="{ active: filter === 'todos' }"    @click="filter = 'todos'">Todos</button>
      <button :class="{ active: filter === 'pending' }"  @click="filter = 'pending'">Pendientes</button>
      <button :class="{ active: filter === 'approved' }" @click="filter = 'approved'">Aprobadas</button>
      <button :class="{ active: filter === 'rejected' }" @click="filter = 'rejected'">Rechazadas</button>
      <button :class="{ active: filter === 'sold' }"     @click="filter = 'sold'">Vendidas</button>
    </div>

    <!-- ESTADO -->
    <div v-if="loading" class="state"><div class="spinner"></div></div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <!-- TABLA -->
    <table v-else>
      <thead>
        <tr>
          <th>Título</th>
          <th>Ciudad</th>
          <th>Precio</th>
          <th>Tipo</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in filtered" :key="p.id">
          <td class="td-title">{{ p.title }}</td>
          <td>{{ p.city }}</td>
          <td>${{ Number(p.price).toLocaleString('es-MX') }}</td>
          <td>{{ p.property_type }}</td>
          <td>
            <span :class="['badge', statusMap[p.status]?.cls]">
              {{ statusMap[p.status]?.label ?? p.status }}
            </span>
          </td>
          <td class="actions">
            <button v-if="p.status === 'pending'" class="approve" @click="confirm('approve', p.id)">Aprobar</button>
            <button v-if="p.status === 'pending'" class="reject"  @click="confirm('reject',  p.id)">Rechazar</button>
            <button v-if="p.status === 'approved'" class="sold"   @click="confirm('markSold',p.id)">Vendida</button>
            <button class="delete" @click="confirm('remove', p.id)">Eliminar</button>
          </td>
        </tr>
        <tr v-if="!filtered.length">
          <td colspan="6" style="text-align:center; color:#999; padding:30px">Sin propiedades</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.admin { padding: 40px; font-family: 'Poppins', sans-serif; }
h1     { margin-bottom: 20px; font-size: 26px; }

.filters { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.filters button {
  border: 1px solid #e5e7eb; background: white; padding: 8px 14px;
  border-radius: 20px; cursor: pointer; font-size: 13px; transition: .2s; font-family: inherit;
}
.filters button.active { background: #f59e0b; color: white; border-color: #f59e0b; }

/* STATE */
.state { display: flex; justify-content: center; padding: 40px; color: #666; }
.error-msg { color: #991b1b; }
.spinner {
  width: 36px; height: 36px; border: 3px solid #f3f3f3;
  border-top-color: #f59e0b; border-radius: 50%; animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 6px 20px rgba(0,0,0,.06); }
th, td { padding: 14px; text-align: left; font-size: 14px; }
thead  { background: #f3f4f6; }
tbody tr:hover { background: #fafafa; }
.td-title { font-weight: 600; max-width: 220px; }

.badge { padding: 5px 10px; border-radius: 8px; font-size: 12px; font-weight: 600; }
.pendiente { background: #fef3c7; color: #92400e; }
.aprobada  { background: #dcfce7; color: #166534; }
.rechazada { background: #fee2e2; color: #991b1b; }
.vendida   { background: #e0e7ff; color: #3730a3; }

.actions { display: flex; gap: 6px; flex-wrap: wrap; }
.actions button { border: none; padding: 6px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; font-family: inherit; }
.approve { background: #bbf7d0; color: #166534; }
.reject  { background: #fca5a5; color: #991b1b; }
.sold    { background: #c7d2fe; color: #3730a3; }
.delete  { background: #fecaca; color: #991b1b; }
</style>

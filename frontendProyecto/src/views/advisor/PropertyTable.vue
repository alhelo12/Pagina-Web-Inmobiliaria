<script setup>
defineProps({
  items: Array
})

const emit = defineEmits(['approve', 'reject', 'sold'])
</script>

<template>
  <!-- ===== TABLA DESKTOP ===== -->
  <div class="table-wrapper">
    <table class="table">
      <thead>
        <tr>
          <th>Propiedad</th>
          <th>Ciudad</th>
          <th>Precio</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="p in items" :key="p.id">
          <td class="title">{{ p.title }}</td>
          <td>{{ p.city }}</td>
          <td class="price">${{ p.price }}</td>
          <td>
            <span class="badge" :class="p.status">{{ p.status }}</span>
          </td>

          <td class="actions">
            <template v-if="p.status === 'pending'">
              <button class="approve" @click="emit('approve', p)">Aprobar</button>
              <button class="reject" @click="emit('reject', p)">Rechazar</button>
            </template>

            <template v-else-if="p.status === 'approved'">
              <button class="sold" @click="emit('sold', p)">Vendida</button>
            </template>

            <span v-else class="no-actions">Sin acciones</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- ===== TARJETAS MOBILE ===== -->
  <div class="mobile-cards">
    <div v-for="p in items" :key="p.id" class="card">
      <h3>{{ p.title }}</h3>

      <p><strong>Ciudad:</strong> {{ p.city }}</p>
      <p><strong>Precio:</strong> ${{ p.price }}</p>

      <span class="badge" :class="p.status">{{ p.status }}</span>

      <div class="card-actions">
        <template v-if="p.status === 'pending'">
          <button class="approve" @click="emit('approve', p)">Aprobar</button>
          <button class="reject" @click="emit('reject', p)">Rechazar</button>
        </template>

        <template v-else-if="p.status === 'approved'">
          <button class="sold" @click="emit('sold', p)">Vendida</button>
        </template>
      </div>
    </div>
  </div>
</template>


<style scoped>

/* ===== CONTENEDOR ===== */
.table-wrapper {
  overflow-x: auto;
}

/* ===== TABLA ===== */
.table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}

th {
  background: #0d2c54;
  color: white;
  text-align: left;
  padding: 14px;
  font-size: 14px;
}

td {
  padding: 14px;
  border-bottom: 1px solid #eee;
  font-size: 14px;
}

.title {
  font-weight: 600;
}

.price {
  font-weight: bold;
  color: #0d2c54;
}

/* ===== BADGES ===== */
.badge {
  padding: 6px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.pending { background: #fff3cd; color: #856404; }
.approved { background: #d4edda; color: #155724; }
.rejected { background: #f8d7da; color: #721c24; }
.sold { background: #d1ecf1; color: #0c5460; }

/* ===== BOTONES ===== */
.actions button,
.card-actions button {
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  margin-right: 6px;
  transition: 0.2s;
}

.approve { background: #2ecc71; color: white; }
.reject { background: #e74c3c; color: white; }
.sold { background: #3498db; color: white; }

button:hover {
  transform: translateY(-1px);
  opacity: 0.9;
}

.no-actions {
  color: #999;
  font-style: italic;
}

/* ===== MOBILE CARDS ===== */
.mobile-cards {
  display: none;
}

.card {
  background: white;
  border-radius: 14px;
  padding: 16px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}

.card h3 {
  margin-bottom: 8px;
}

.card-actions {
  margin-top: 12px;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .table-wrapper {
    display: none;
  }

  .mobile-cards {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
}

</style>

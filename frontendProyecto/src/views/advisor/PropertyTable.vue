<script setup>
defineProps({ items: Array })
const emit = defineEmits(['approve', 'reject', 'sold'])

const typeLabel = { house: 'Casa', apartment: 'Depto.', land: 'Terreno', commercial: 'Local' }
</script>

<template>
  <!-- TABLA DESKTOP -->
  <div class="table-wrapper">
    <table class="table">
      <thead>
        <tr>
          <th>Propiedad</th><th>Ciudad</th><th>Precio</th><th>Tipo</th><th>Estado</th><th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in items" :key="p.id">
          <td class="title">{{ p.title }}</td>
          <td>{{ p.city }}</td>
          <td class="price">${{ Number(p.price).toLocaleString('es-MX') }}</td>
          <td>{{ typeLabel[p.property_type] ?? p.property_type }}</td>
          <td><span class="badge" :class="p.status">{{ p.status }}</span></td>
          <td class="actions">
            <template v-if="p.status === 'pending'">
              <button class="approve" @click="emit('approve', p)">Aprobar</button>
              <button class="reject"  @click="emit('reject', p)">Rechazar</button>
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

  <!-- TARJETAS MOBILE -->
  <div class="mobile-cards">
    <div v-for="p in items" :key="p.id" class="card">
      <h3>{{ p.title }}</h3>
      <p><strong>Ciudad:</strong> {{ p.city }}</p>
      <p><strong>Precio:</strong> ${{ Number(p.price).toLocaleString('es-MX') }}</p>
      <span class="badge" :class="p.status">{{ p.status }}</span>
      <div class="card-actions">
        <template v-if="p.status === 'pending'">
          <button class="approve" @click="emit('approve', p)">Aprobar</button>
          <button class="reject"  @click="emit('reject', p)">Rechazar</button>
        </template>
        <template v-else-if="p.status === 'approved'">
          <button class="sold" @click="emit('sold', p)">Vendida</button>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.table-wrapper { overflow-x: auto; }
.table {
  width: 100%; border-collapse: collapse; background: white;
  border-radius: 14px; overflow: hidden; box-shadow: 0 4px 14px rgba(0,0,0,.05);
}
th { background: #0d2c54; color: white; text-align: left; padding: 14px; font-size: 14px; }
td { padding: 14px; border-bottom: 1px solid #eee; font-size: 14px; }
.title { font-weight: 600; }
.price { font-weight: bold; color: #0d2c54; }

.badge { padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: capitalize; }
.pending  { background: #fff3cd; color: #856404; }
.approved { background: #d4edda; color: #155724; }
.rejected { background: #f8d7da; color: #721c24; }
.sold     { background: #d1ecf1; color: #0c5460; }

.actions, .card-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.actions button, .card-actions button {
  border: none; padding: 7px 12px; border-radius: 8px;
  cursor: pointer; font-weight: 600; transition: .2s; font-family: inherit; font-size: 13px;
}
.approve { background: #2ecc71; color: white; }
.reject  { background: #e74c3c; color: white; }
.sold    { background: #3498db; color: white; }
button:hover { opacity: .88; transform: translateY(-1px); }
.no-actions  { color: #999; font-style: italic; font-size: 13px; }

.mobile-cards { display: none; }
.card { background: white; border-radius: 14px; padding: 16px; box-shadow: 0 4px 14px rgba(0,0,0,.05); }
.card h3 { margin-bottom: 8px; }
.card-actions { margin-top: 12px; }

@media (max-width: 768px) {
  .table-wrapper { display: none; }
  .mobile-cards  { display: flex; flex-direction: column; gap: 12px; }
}
</style>

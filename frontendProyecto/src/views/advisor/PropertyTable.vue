<script setup>
defineProps({ items: Array })
const emit = defineEmits(['approve', 'reject', 'sold'])

const typeLabel = { house: 'Casa', apartment: 'Depto.', land: 'Terreno', commercial: 'Local' }

const ownerName = (property) => property.owner?.full_name || `Usuario #${property.submitted_by_user_id}`
const ownerEmail = (property) => property.owner?.email || 'Sin email'
const formatRegisteredAt = (value) => {
  if (!value) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(new Date(value))
}

const getPropertyImage = (property) => {
  const img = property.images?.find(i => i.is_main) ?? property.images?.[0]
  if (img) {
    const url = img.image_url ?? img.url
    if (!url) return null
    if (/^(https?:|blob:|data:)/.test(url)) return url
    const base = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
    return `${base}${url.startsWith('/') ? '' : '/'}${url}`
  }
  return null
}

const propertyFallback = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgdmlld0JveD0iMCAwIDY0IDY0IiBzdHlsZT0iZGlzcGxheTpibG9jazsiIGNsYXNzPSJhIiBmaWxsPSIjZWRlY2VkIj48cmVjdCB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHJ4PSIxMiIgc3R5bGU9ImZpbGw6I2VkZWNlZCIgc3BhY2Y9Im5vbmUiLz48cGF0aCBkPSJNMjIgMzZoMjBjLTEuMSAwLTIgLjktMiAyIDAgMS4xLjkgMiAyIDIgMCAxLjEtLjkgMi0yIDJoLTIwYzEuMSAwIDItLjkgMi0yIDAtMS4xLS45LTItMi0yeiIgZmlsbD0iI2RkYzJkNSIvPjwvc3ZnPg=='
</script>

<template>
  <!-- TABLA DESKTOP -->
  <div class="table-wrapper">
    <table class="table">
      <thead>
        <tr>
          <th></th>
          <th>Propiedad</th><th>Registrado por</th><th>Registrada</th><th>Ciudad</th><th>Precio</th><th>Tipo</th><th>Estado</th><th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in items" :key="p.id">
          <td class="td-thumb">
            <img :src="getPropertyImage(p) || propertyFallback" :alt="p.title" @error="(e) => { e.target.src = propertyFallback }" />
          </td>
          <td class="title">{{ p.title }}</td>
          <td>
            <span class="owner-name">{{ ownerName(p) }}</span>
            <small class="owner-email">{{ ownerEmail(p) }}</small>
          </td>
          <td class="registered-at">{{ formatRegisteredAt(p.created_at) }}</td>
          <td>{{ p.city }}</td>
          <td class="price">${{ Number(p.price).toLocaleString('es-MX') }}</td>
          <td>{{ typeLabel[p.property_type] ?? p.property_type }}</td>
          <td><span class="badge" :class="p.status">{{ p.status }}</span></td>
          <td class="actions">
            <template v-if="p.status === 'pending'">
              <button class="approve" @click="emit('approve', p)">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                Aprobar
              </button>
              <button class="reject" @click="emit('reject', p)">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                Rechazar
              </button>
            </template>
            <template v-else-if="p.status === 'approved'">
              <button class="sold" @click="emit('sold', p)">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                Vendida
              </button>
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
      <div class="card-thumb">
        <img :src="getPropertyImage(p) || propertyFallback" :alt="p.title" @error="(e) => { e.target.src = propertyFallback }" />
      </div>
      <h3>{{ p.title }}</h3>
      <p><strong>Registrado por:</strong> {{ ownerName(p) }}</p>
      <p class="owner-email">{{ ownerEmail(p) }}</p>
      <p><strong>Registrada:</strong> {{ formatRegisteredAt(p.created_at) }}</p>
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
th { background: var(--color-navy); color: white; text-align: left; padding: 14px; font-size: 14px; }
td { padding: 14px; border-bottom: 1px solid var(--color-line); font-size: 14px; }
tr:hover { background: rgba(214, 168, 72, .05); }
.td-thumb { width: 44px; padding-right: 8px; }
.td-thumb img { width: 44px; height: 44px; border-radius: 8px; object-fit: cover; background: #f0ece4; }
.title { font-weight: 600; color: var(--color-navy); }
.price { font-weight: bold; color: var(--color-navy); }
.owner-name { display: block; font-weight: 600; color: var(--color-navy); }
.owner-email { display: block; color: var(--color-muted); font-size: 12px; margin-top: 2px; }
.registered-at { color: var(--color-navy-2); font-weight: 600; white-space: nowrap; }

.badge { padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: capitalize; }
.pending  { background: #fff3cd; color: #856404; }
.approved { background: #d4edda; color: #155724; }
.rejected { background: #f8d7da; color: #721c24; }
.sold     { background: #d1ecf1; color: #0c5460; }

.actions, .card-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.actions button, .card-actions button {
  border: none; padding: 7px 10px; border-radius: 8px;
  cursor: pointer; font-weight: 600; transition: .2s; font-family: inherit; font-size: 13px;
  display: flex; align-items: center; gap: 4px;
}
.approve { background: #2ecc71; color: white; }
.reject  { background: #e74c3c; color: white; }
.sold    { background: #3498db; color: white; }
button:hover { opacity: .88; transform: translateY(-1px); }
.no-actions  { color: #999; font-style: italic; font-size: 13px; }

.mobile-cards { display: none; }
.card { background: white; border-radius: 14px; padding: 16px; box-shadow: 0 4px 14px rgba(0,0,0,.05); }
.card-thumb { width: 100%; height: 120px; border-radius: 10px; overflow: hidden; background: #f0ece4; margin-bottom: 10px; }
.card-thumb img { width: 100%; height: 100%; object-fit: cover; }
.card h3 { margin-bottom: 8px; color: var(--color-navy); }
.card-actions { margin-top: 12px; }

@media (max-width: 768px) {
  .table-wrapper { display: none; }
  .mobile-cards  { display: flex; flex-direction: column; gap: 12px; }
}
</style>

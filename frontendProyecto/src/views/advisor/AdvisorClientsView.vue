<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { usePropertyStore } from '@/stores/propertyStore'
import { storeToRefs } from 'pinia'
import AdvisorDashboardHeader from '@/components/advisor/dashboard/AdvisorDashboardHeader.vue'
import Breadcrumb from '@/components/shared/Breadcrumb.vue'

const store = usePropertyStore()
const { properties, loading, error } = storeToRefs(store)

const search = ref('')
const debouncedSearch = ref('')
let searchTimeout = null

watch(search, (val) => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { debouncedSearch.value = val }, 300)
})

const myProperties = computed(() => {
  return properties.value.filter(p => p.advisor_id !== null)
})

const myClients = computed(() => {
  const q = debouncedSearch.value.trim().toLowerCase()
  const clientsMap = new Map()
  
  myProperties.value.forEach(p => {
    const ownerId = p.submitted_by_user_id
    if (ownerId && !clientsMap.has(ownerId)) {
      clientsMap.set(ownerId, {
        id: ownerId,
        name: p.owner?.full_name || `Cliente #${ownerId}`,
        email: p.owner?.email || 'Sin email',
        phone: p.owner?.phone || 'Sin teléfono',
        properties: []
      })
    }
    if (clientsMap.has(ownerId)) {
      clientsMap.get(ownerId).properties.push(p)
    }
  })
  
  let clients = Array.from(clientsMap.values())
  
  if (q) {
    clients = clients.filter(c =>
      c.name?.toLowerCase().includes(q) ||
      c.email?.toLowerCase().includes(q)
    )
  }
  
  return clients
})

onMounted(() => {
  store.fetchByAdvisor()
})
</script>

<template>
  <section class="clients-view">
    <AdvisorDashboardHeader
      eyebrow="Gestión de clientes"
      title="Mis Clientes"
      :show-add="false"
    />

    <div class="filters-bar">
      <div class="search-wrap">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input v-model="search" type="search" placeholder="Buscar por nombre o email..." />
      </div>
      <span class="result-count">{{ myClients.length }} cliente{{ myClients.length !== 1 ? 's' : '' }}</span>
    </div>

    <Breadcrumb :crumbs="[{ label: 'Clientes', path: '/advisor/clientes' }]" />

    <article class="table-card">
      <div v-if="loading" class="state"><div class="spinner"></div></div>
      <div v-else-if="error" class="state error-msg">{{ error }}</div>

      <div v-else-if="myClients.length" class="clients-list">
        <div v-for="client in myClients" :key="client.id" class="client-row">
          <div class="client-info">
            <div class="client-avatar">
              {{ client.name.charAt(0).toUpperCase() }}
            </div>
            <div class="client-details">
              <strong>{{ client.name }}</strong>
              <span>{{ client.email }}</span>
              <small>{{ client.phone }}</small>
            </div>
          </div>
          <div class="client-properties">
            <span class="property-count">{{ client.properties.length }} propiedad{{ client.properties.length !== 1 ? 'es' : '' }}</span>
            <div class="property-tags">
              <span v-for="prop in client.properties.slice(0, 3)" :key="prop.id" class="property-tag">
                {{ prop.city || 'Sin ciudad' }}
              </span>
              <span v-if="client.properties.length > 3" class="property-tag more">
                +{{ client.properties.length - 3 }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <p v-else class="empty">No tienes clientes aún.</p>
    </article>
  </section>
</template>

<style scoped>
.clients-view { font-family: 'Poppins', sans-serif; display: grid; gap: 16px; }

.filters-bar { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; padding: 14px 18px; background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); }
.search-wrap { display: flex; align-items: center; gap: 8px; flex: 1; min-width: 200px; background: #fff; border: 1px solid var(--color-line); border-radius: 8px; padding: 8px 12px; }
.search-wrap svg { color: var(--color-muted); flex-shrink: 0; }
.search-wrap input { border: none; outline: none; flex: 1; font-size: 14px; color: var(--color-navy); background: transparent; font-family: inherit; }
.result-count { color: var(--color-muted); font-size: 13px; font-weight: 600; white-space: nowrap; }

.table-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 16px; }

.state { display: flex; justify-content: center; padding: 40px; color: var(--color-muted); }
.error-msg { color: #991b1b; }
.spinner { width: 36px; height: 36px; border: 3px solid #eadfcf; border-top-color: var(--color-gold); border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; color: var(--color-muted); padding: 40px 20px; font-size: 14px; }

.clients-list { display: flex; flex-direction: column; gap: 12px; }
.client-row { display: flex; justify-content: space-between; align-items: center; padding: 16px; border-radius: 10px; border: 1px solid var(--color-line); background: #fff; transition: .2s; }
.client-row:hover { box-shadow: 0 4px 12px rgba(7, 23, 45, 0.08); }

.client-info { display: flex; align-items: center; gap: 14px; }
.client-avatar { width: 48px; height: 48px; border-radius: 50%; background: var(--color-navy); color: var(--color-gold); display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; }
.client-details strong { display: block; color: var(--color-navy); font-size: 15px; margin-bottom: 2px; }
.client-details span { display: block; color: var(--color-muted); font-size: 13px; }
.client-details small { display: block; color: var(--color-muted); font-size: 12px; margin-top: 2px; }

.client-properties { text-align: right; }
.property-count { display: inline-block; padding: 6px 12px; border-radius: 20px; background: #f7efe0; color: var(--color-navy-2); font-size: 12px; font-weight: 700; margin-bottom: 6px; }
.property-tags { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.property-tag { padding: 3px 8px; border-radius: 6px; background: #e8edf0; color: var(--color-navy-2); font-size: 11px; }
.property-tag.more { background: var(--color-navy); color: #fff; }

@media (max-width: 768px) {
  .client-row { flex-direction: column; align-items: flex-start; gap: 12px; }
  .client-properties { text-align: left; }
  .property-tags { justify-content: flex-start; }
}
@media (max-width: 480px) {
  .filters-bar { flex-direction: column; align-items: stretch; gap: 10px; }
  .search-wrap { min-width: 0; }
  .result-count { text-align: right; }
  .table-card { padding: 12px; }
  .client-avatar { width: 40px; height: 40px; font-size: 15px; }
  .client-row { padding: 12px; }
}
</style>
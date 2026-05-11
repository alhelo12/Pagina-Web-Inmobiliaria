<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from '@/components/shared/AppIcon.vue'

const props = defineProps({
  clients: { type: Array, default: () => [] },
  stats: { type: Object, default: () => ({}) }
})

const router = useRouter()

const totalClients = computed(() => props.clients?.length || 0)
const activeClients = computed(() => props.clients?.filter(c => c.is_active).length || 0)
</script>

<template>
  <div class="relationship-panel">
    <div class="panel-header">
      <h3>Mis Clientes</h3>
      <span class="client-count">{{ totalClients }} total</span>
    </div>

    <div class="stats-row">
      <div class="stat">
        <span class="stat-value">{{ totalClients }}</span>
        <span class="stat-label">Clientes</span>
      </div>
      <div class="stat">
        <span class="stat-value">{{ activeClients }}</span>
        <span class="stat-label">Activos</span>
      </div>
      <div class="stat">
        <span class="stat-value">{{ stats.appointments || 0 }}</span>
        <span class="stat-label">Citas</span>
      </div>
    </div>

    <div v-if="clients.length" class="clients-list">
      <div v-for="client in clients.slice(0, 4)" :key="client.id" class="client-item">
        <div class="client-avatar">{{ client.name?.charAt(0) || 'C' }}</div>
        <div class="client-info">
          <span class="client-name">{{ client.name || 'Cliente' }}</span>
          <span class="client-email">{{ client.email || '' }}</span>
        </div>
      </div>
    </div>
    <div v-else class="no-clients">
      <p>No tienes clientes aún</p>
    </div>

    <div class="quick-actions">
      <RouterLink to="/advisor/clientes" class="action-link">
        <span class="action-icon"><AppIcon name="user" :size="16" /></span>
        <span>Ver Clientes</span>
      </RouterLink>
      <RouterLink to="/advisor/citas" class="action-link">
        <span class="action-icon"><AppIcon name="calendar" :size="16" /></span>
        <span>Ver Citas</span>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.relationship-panel {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
  padding: 20px;
}
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.panel-header h3 { font-size: 14px; font-weight: 700; color: var(--color-navy); text-transform: uppercase; letter-spacing: .5px; margin: 0; }
.client-count { font-size: 12px; color: var(--color-muted); }

.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
.stat { text-align: center; padding: 12px; background: #f8f9fa; border-radius: 8px; }
.stat-value { display: block; font-size: 20px; font-weight: 800; color: var(--color-navy); }
.stat-label { font-size: 11px; color: var(--color-muted); text-transform: uppercase; }

.clients-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }
.client-item { display: flex; align-items: center; gap: 10px; padding: 8px; background: #f8f9fa; border-radius: 8px; }
.client-avatar { width: 32px; height: 32px; border-radius: 50%; background: #4b5563; color: white; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 13px; }
.client-info { display: flex; flex-direction: column; overflow: hidden; }
.client-name { font-weight: 600; font-size: 13px; color: var(--color-navy); }
.client-email { font-size: 11px; color: var(--color-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.no-clients { text-align: center; padding: 16px; background: #f8f9fa; border-radius: 8px; margin-bottom: 16px; }
.no-clients p { margin: 0; color: var(--color-muted); font-size: 13px; }

.quick-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.action-link { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: 8px; border: 1px solid var(--color-line); background: white; color: var(--color-navy); text-decoration: none; font-weight: 600; font-size: 13px; transition: .2s; }
.action-link:hover { border-color: var(--color-gold); background: #fdfcf8; }
.action-icon { font-size: 16px; }
</style>
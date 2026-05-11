<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  advisor: Object,
  stats: Object
})

const router = useRouter()

const advisorName = computed(() => props.advisor?.name || 'Sin asesor asignado')
const advisorEmail = computed(() => props.advisor?.email || '')
const advisorPhone = computed(() => props.advisor?.phone || 'Sin teléfono')
</script>

<template>
  <div class="relationship-panel">
    <div class="panel-header">
      <h3>Tu Asesor</h3>
      <span class="status-badge" v-if="advisor">Activo</span>
    </div>

    <div v-if="advisor" class="advisor-info">
      <div class="advisor-avatar">{{ advisorName.charAt(0) }}</div>
      <div class="advisor-details">
        <span class="advisor-name">{{ advisorName }}</span>
        <span class="advisor-contact">{{ advisorEmail }}</span>
      </div>
    </div>

    <div v-else class="no-advisor">
      <p>No tienes un asesor asignado</p>
      <small>Contacta para solicitar uno</small>
    </div>

    <div v-if="stats" class="stats-row">
      <div class="stat">
        <span class="stat-value">{{ stats.appointments || 0 }}</span>
        <span class="stat-label">Citas</span>
      </div>
      <div class="stat">
        <span class="stat-value">{{ stats.messages || 0 }}</span>
        <span class="stat-label">Mensajes</span>
      </div>
      <div class="stat">
        <span class="stat-value">{{ stats.properties || 0 }}</span>
        <span class="stat-label">Propiedades</span>
      </div>
    </div>

    <div class="quick-actions">
      <RouterLink to="/cliente/citas" class="action-link">
        <span class="action-icon">📅</span>
        <span>Ver Citas</span>
      </RouterLink>
      <RouterLink to="/cliente/mensajes" class="action-link">
        <span class="action-icon">💬</span>
        <span>Enviar Mensaje</span>
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
.status-badge { font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 4px; background: #d1fae5; color: #059669; }

.advisor-info { display: flex; align-items: center; gap: 12px; padding: 12px; background: #f8f9fa; border-radius: 10px; margin-bottom: 16px; }
.advisor-avatar { width: 44px; height: 44px; border-radius: 50%; background: var(--color-gold); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 18px; }
.advisor-details { display: flex; flex-direction: column; }
.advisor-name { font-weight: 600; color: var(--color-navy); }
.advisor-contact { font-size: 13px; color: var(--color-muted); }

.no-advisor { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px; margin-bottom: 16px; }
.no-advisor p { font-weight: 600; color: var(--color-navy); margin: 0 0 4px; }
.no-advisor small { color: var(--color-muted); font-size: 13px; }

.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
.stat { text-align: center; padding: 12px; background: #f8f9fa; border-radius: 8px; }
.stat-value { display: block; font-size: 20px; font-weight: 800; color: var(--color-navy); }
.stat-label { font-size: 11px; color: var(--color-muted); text-transform: uppercase; }

.quick-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.action-link { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: 8px; border: 1px solid var(--color-line); background: white; color: var(--color-navy); text-decoration: none; font-weight: 600; font-size: 13px; transition: .2s; }
.action-link:hover { border-color: var(--color-gold); background: #fdfcf8; }
.action-icon { font-size: 16px; }
</style>
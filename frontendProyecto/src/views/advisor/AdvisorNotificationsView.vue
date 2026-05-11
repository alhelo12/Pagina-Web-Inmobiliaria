<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { storeToRefs } from 'pinia'
import AdvisorDashboardHeader from '@/components/advisor/dashboard/AdvisorDashboardHeader.vue'

const store = useNotificationsStore()
const { notifications, unreadCount, loading } = storeToRefs(store)

const filter = ref('all')

const filteredNotifications = computed(() => {
  if (filter.value === 'unread') {
    return notifications.value.filter(n => !n.is_read)
  }
  return notifications.value
})

const totalCount = computed(() => notifications.value.length)
const unreadCountVal = computed(() => unreadCount.value)

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Ahora mismo'
  if (minutes < 60) return `Hace ${minutes} min`
  if (hours < 24) return `Hace ${hours} h`
  if (days < 7) return `Hace ${days} días`
  return d.toLocaleDateString('es-MX', { day: 'numeric', month: 'short' })
}

const getNotificationIcon = (type) => {
  const icons = {
    appointment: '📅',
    property_update: '🏠',
    property_approved: '✅',
    property_rejected: '❌',
    property_sold: '🏆',
    message: '💬',
    default: '🔔'
  }
  return icons[type] || icons.default
}

const getNotificationTitle = (notification) => {
  const titles = {
    appointment: 'Nueva cita programada',
    property_update: 'Propiedad actualizada',
    property_approved: 'Propiedad aprobada',
    property_rejected: 'Propiedad rechazada',
    property_sold: '¡Propiedad vendida!',
    message: 'Nuevo mensaje',
    default: 'Notificación'
  }
  return titles[notification.type] || titles.default
}

const markAsRead = async (id) => {
  await store.markAsRead(id)
}

const markAllAsRead = async () => {
  await store.markAllAsRead()
}

onMounted(() => {
  store.fetchNotifications()
})
</script>

<template>
  <div class="notifications-page">
    <AdvisorDashboardHeader title="Notificaciones" subtitle="Mantente al día con tus clientes" />

    <div class="metrics-row">
      <div class="metric-card">
        <span class="metric-value">{{ totalCount }}</span>
        <span class="metric-label">Total</span>
      </div>
      <div class="metric-card unread">
        <span class="metric-value">{{ unreadCountVal }}</span>
        <span class="metric-label">Sin leer</span>
      </div>
    </div>

    <div class="filters">
      <button 
        :class="['filter-btn', { active: filter === 'all' }]" 
        @click="filter = 'all'"
      >
        Todas
      </button>
      <button 
        :class="['filter-btn', { active: filter === 'unread' }]" 
        @click="filter = 'unread'"
      >
        Sin leer
      </button>
    </div>

    <div v-if="unreadCountVal > 0" class="mark-all">
      <button @click="markAllAsRead" class="mark-all-btn">
        Marcar todas como leídas
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando notificaciones...</p>
    </div>

    <div v-else-if="filteredNotifications.length === 0" class="empty-state">
      <div class="empty-icon">🔔</div>
      <h3>No hay notificaciones</h3>
      <p>Las notificaciones de tus clientes aparecerán aquí</p>
    </div>

    <div v-else class="notifications-list">
      <div 
        v-for="notif in filteredNotifications" 
        :key="notif.id"
        :class="['notification-card', { unread: !notif.is_read }]"
        @click="markAsRead(notif.id)"
      >
        <div class="notif-icon">{{ getNotificationIcon(notif.type) }}</div>
        <div class="notif-content">
          <div class="notif-header">
            <h4>{{ getNotificationTitle(notif) }}</h4>
            <span class="notif-time">{{ formatDate(notif.created_at) }}</span>
          </div>
          <p class="notif-message">{{ notif.message }}</p>
          <div v-if="notif.data?.property_title" class="notif-property">
            <span class="property-label">Propiedad:</span>
            <span class="property-value">{{ notif.data.property_title }}</span>
          </div>
        </div>
        <div v-if="!notif.is_read" class="unread-dot"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notifications-page { padding: 32px; max-width: 800px; margin: 0 auto; }
.metrics-row { display: flex; gap: 16px; margin-bottom: 24px; }
.metric-card { flex: 1; background: var(--color-card); border: 1px solid var(--color-line); border-radius: 12px; padding: 20px; text-align: center; }
.metric-value { display: block; font-size: 28px; font-weight: 800; color: var(--color-navy); }
.metric-card.unread .metric-value { color: #dc2626; }
.metric-label { font-size: 13px; color: var(--color-muted); }

.filters { display: flex; gap: 12px; margin-bottom: 20px; }
.filter-btn { padding: 10px 20px; border-radius: 8px; border: 1px solid var(--color-line); background: var(--color-card); color: var(--color-muted); font-weight: 600; cursor: pointer; transition: .2s; }
.filter-btn:hover, .filter-btn.active { background: var(--color-gold); color: white; border-color: var(--color-gold); }

.mark-all { margin-bottom: 16px; }
.mark-all-btn { padding: 8px 16px; border-radius: 6px; background: transparent; color: var(--color-gold); border: 1px solid var(--color-gold); font-weight: 600; cursor: pointer; transition: .2s; }
.mark-all-btn:hover { background: var(--color-gold); color: white; }

.loading-state, .empty-state { text-align: center; padding: 60px 20px; color: var(--color-muted); }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.spinner { width: 40px; height: 40px; border: 3px solid var(--color-line); border-top-color: var(--color-gold); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }

.notifications-list { display: flex; flex-direction: column; gap: 12px; }
.notification-card { display: flex; gap: 16px; padding: 16px; background: var(--color-card); border: 1px solid var(--color-line); border-radius: 12px; cursor: pointer; transition: .2s; position: relative; }
.notification-card:hover { border-color: var(--color-gold); }
.notification-card.unread { background: #fefcf7; border-left: 3px solid var(--color-gold); }
.notif-icon { width: 44px; height: 44px; border-radius: 50%; background: #f3f4f6; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.notif-content { flex: 1; }
.notif-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
.notif-header h4 { font-size: 14px; font-weight: 700; color: var(--color-navy); margin: 0; }
.notif-time { font-size: 12px; color: var(--color-muted); }
.notif-message { font-size: 13px; color: var(--color-muted); margin: 0; line-height: 1.5; }
.notif-property { margin-top: 8px; font-size: 12px; }
.property-label { color: var(--color-muted); }
.property-value { font-weight: 600; color: var(--color-navy); margin-left: 4px; }
.unread-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--color-gold); position: absolute; top: 16px; right: 16px; }
</style>
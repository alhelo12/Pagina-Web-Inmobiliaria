<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { storeToRefs } from 'pinia'

const router = useRouter()
const store = useNotificationsStore()
const { notifications, loading, unreadCount } = storeToRefs(store)

const activeFilter = ref('all')

const typeIcons = {
  advisor_assigned: { icon: '👤', color: '#d6a848', label: 'Asesor asignado' },
  approved: { icon: '✅', color: '#22c55e', label: 'Aprobada' },
  rejected: { icon: '❌', color: '#dc2626', label: 'Rechazada' },
  sold: { icon: '🏠', color: '#7c3aed', label: 'Vendida' },
  property_updated: { icon: '✏️', color: '#3b82f6', label: 'Actualizada' }
}

const filters = [
  { key: 'all', label: 'Todas' },
  { key: 'unread', label: 'No leídas' },
  { key: 'approved', label: 'Aprobadas' },
  { key: 'rejected', label: 'Rechazadas' },
  { key: 'sold', label: 'Vendidas' }
]

const filteredNotifications = computed(() => {
  let result = notifications.value

  if (activeFilter.value === 'unread') {
    result = result.filter(n => !n.is_read)
  } else if (activeFilter.value !== 'all') {
    result = result.filter(n => n.type === activeFilter.value)
  }

  return result
})

const stats = computed(() => ({
  total: notifications.value.length,
  unread: unreadCount.value,
  approved: notifications.value.filter(n => n.type === 'approved').length,
  rejected: notifications.value.filter(n => n.type === 'rejected').length,
  sold: notifications.value.filter(n => n.type === 'sold').length
}))

const formatDate = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleDateString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    await store.markAsRead(notification.id)
  }
  if (notification.property_id) {
    router.push(`/propiedades/${notification.property_id}`)
  }
}

const handleMarkAllRead = async () => {
  await store.markAllAsRead()
}

onMounted(() => {
  store.fetchNotifications({ limit: 100 })
})
</script>

<template>
  <div class="notifications-page">
    <header class="page-header">
      <div>
        <p class="kicker">PANEL DE CLIENTE</p>
        <h1>Notificaciones</h1>
      </div>
      <button v-if="unreadCount > 0" class="mark-all-btn" @click="handleMarkAllRead">
        Marcar todas como leídas
      </button>
    </header>

    <div class="stats-row">
      <div class="stat-card">
        <span class="stat-value">{{ stats.total }}</span>
        <span class="stat-label">Total</span>
      </div>
      <div class="stat-card highlight">
        <span class="stat-value">{{ stats.unread }}</span>
        <span class="stat-label">Sin leer</span>
      </div>
      <div class="stat-card green">
        <span class="stat-value">{{ stats.approved }}</span>
        <span class="stat-label">Aprobadas</span>
      </div>
      <div class="stat-card red">
        <span class="stat-value">{{ stats.rejected }}</span>
        <span class="stat-label">Rechazadas</span>
      </div>
      <div class="stat-card purple">
        <span class="stat-value">{{ stats.sold }}</span>
        <span class="stat-label">Vendidas</span>
      </div>
    </div>

    <div class="filters">
      <button
        v-for="filter in filters"
        :key="filter.key"
        :class="['filter-btn', { active: activeFilter === filter.key }]"
        @click="activeFilter = filter.key"
      >
        {{ filter.label }}
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Cargando notificaciones...</p>
    </div>

    <div v-else-if="!filteredNotifications.length" class="empty-state">
      <span class="empty-icon">🔔</span>
      <h3>No hay notificaciones</h3>
      <p>No tienes notificaciones que coincidan con el filtro seleccionado.</p>
    </div>

    <div v-else class="notifications-list">
      <article
        v-for="notification in filteredNotifications"
        :key="notification.id"
        :class="['notification-card', { unread: !notification.is_read }]"
        @click="handleNotificationClick(notification)"
      >
        <div
          class="type-icon"
          :style="{ backgroundColor: typeIcons[notification.type]?.color + '20', color: typeIcons[notification.type]?.color }"
        >
          {{ typeIcons[notification.type]?.icon || '📢' }}
        </div>

        <div class="notification-content">
          <div class="notification-header">
            <h3>{{ notification.title }}</h3>
            <span
              class="type-badge"
              :style="{ backgroundColor: typeIcons[notification.type]?.color + '15', color: typeIcons[notification.type]?.color }"
            >
              {{ typeIcons[notification.type]?.label || notification.type }}
            </span>
          </div>
          <p>{{ notification.message }}</p>
          <div class="notification-meta">
            <span class="date">{{ formatDate(notification.created_at) }}</span>
            <span v-if="!notification.is_read" class="unread-dot"></span>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.notifications-page {
  padding: 32px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.page-header p {
  margin: 0 0 4px;
  color: var(--color-gold);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.page-header h1 {
  margin: 0;
  color: var(--color-navy);
  font-size: 28px;
  font-weight: 800;
}

.mark-all-btn {
  background: var(--color-navy);
  color: var(--color-gold);
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: 0.3s ease;
}

.mark-all-btn:hover {
  background: #0a1525;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 10px;
  padding: 16px;
  text-align: center;
  transition: 0.3s ease;
}

.stat-card:hover {
  border-color: var(--color-gold);
}

.stat-value {
  display: block;
  color: var(--color-navy);
  font-size: 24px;
  font-weight: 800;
}

.stat-label {
  color: var(--color-muted);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.stat-card.highlight {
  background: #fef3c7;
  border-color: #fcd34d;
}

.stat-card.highlight .stat-value {
  color: #b45309;
}

.stat-card.green {
  background: #dcfce7;
  border-color: #86efac;
}

.stat-card.green .stat-value {
  color: #15803d;
}

.stat-card.red {
  background: #fee2e2;
  border-color: #fca5a5;
}

.stat-card.red .stat-value {
  color: #dc2626;
}

.stat-card.purple {
  background: #ede9fe;
  border-color: #c4b5fd;
}

.stat-card.purple .stat-value {
  color: #7c3aed;
}

.filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-line);
}

.filter-btn {
  background: transparent;
  border: 1px solid var(--color-line);
  color: var(--color-muted);
  padding: 8px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s ease;
}

.filter-btn:hover {
  border-color: var(--color-gold);
  color: var(--color-navy);
}

.filter-btn.active {
  background: var(--color-navy);
  border-color: var(--color-navy);
  color: var(--color-gold);
}

.loading {
  text-align: center;
  padding: 60px;
  color: var(--color-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-line);
  border-top-color: var(--color-gold);
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px;
  color: var(--color-navy);
  font-size: 18px;
}

.empty-state p {
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-card {
  display: flex;
  gap: 16px;
  padding: 18px;
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 10px;
  cursor: pointer;
  transition: 0.3s ease;
}

.notification-card:hover {
  border-color: var(--color-gold);
  box-shadow: 0 4px 12px rgba(214, 168, 72, 0.12);
}

.notification-card.unread {
  background: #fdfefb;
  border-color: #d6a848;
}

.type-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 22px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 6px;
}

.notification-header h3 {
  margin: 0;
  color: var(--color-navy);
  font-size: 15px;
  font-weight: 700;
}

.type-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  white-space: nowrap;
}

.notification-content p {
  margin: 0 0 10px;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.5;
}

.notification-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date {
  color: var(--color-muted);
  font-size: 12px;
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-gold);
}

@media (max-width: 768px) {
  .notifications-page {
    padding: 20px;
  }

  .stats-row {
    grid-template-columns: repeat(3, 1fr);
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .page-header h1 {
    font-size: 22px;
  }

  .mark-all-btn {
    width: 100%;
  }
}
</style>
<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { storeToRefs } from 'pinia'

const router = useRouter()
const store = useNotificationsStore()
const { notifications, loading } = storeToRefs(store)

const typeIcons = {
  advisor_assigned: { icon: '👤', color: '#d6a848', label: 'Asesor asignado' },
  approved: { icon: '✅', color: '#22c55e', label: 'Aprobada' },
  rejected: { icon: '❌', color: '#dc2626', label: 'Rechazada' },
  sold: { icon: '🏠', color: '#7c3aed', label: 'Vendida' },
  property_updated: { icon: '✏️', color: '#3b82f6', label: 'Actualizada' }
}

const formatRelativeTime = (timestamp) => {
  if (!timestamp) return ''
  const diff = Date.now() - new Date(timestamp).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'hace un momento'
  if (mins < 60) return `hace ${mins} min`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `hace ${hrs}h`
  const days = Math.floor(hrs / 24)
  if (days < 30) return `hace ${days}d`
  return new Date(timestamp).toLocaleDateString('es-MX', { day: '2-digit', month: 'short' })
}

const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    await store.markAsRead(notification.id)
  }
  if (notification.property_id) {
    router.push(`/propiedades/${notification.property_id}`)
  }
}

onMounted(() => {
  store.fetchNotifications({ limit: 10 })
})
</script>

<template>
  <article class="activity-panel">
    <div class="panel-head">
      <div>
        <p>Notificaciones</p>
        <h3>Actividad Reciente</h3>
      </div>
      <span v-if="store.unreadCount > 0" class="unread-badge">{{ store.unreadCount }} nuevas</span>
    </div>

    <div v-if="loading" class="loading">Cargando...</div>

    <div v-else-if="!notifications.length" class="empty">
      <span class="empty-icon">🔔</span>
      <p>No tienes actividad reciente</p>
      <small>Las notificaciones sobre tus propiedades aparecerán aquí</small>
    </div>

    <div v-else class="activity-list">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="['activity-item', { unread: !notification.is_read }]"
        @click="handleNotificationClick(notification)"
      >
        <div
          class="type-icon"
          :style="{ backgroundColor: typeIcons[notification.type]?.color + '20', color: typeIcons[notification.type]?.color }"
        >
          {{ typeIcons[notification.type]?.icon || '📢' }}
        </div>
        <div class="activity-content">
          <div class="activity-header">
            <strong>{{ notification.title }}</strong>
            <span class="time">{{ formatRelativeTime(notification.created_at) }}</span>
          </div>
          <p>{{ notification.message }}</p>
          <span class="type-label" :style="{ color: typeIcons[notification.type]?.color }">
            {{ typeIcons[notification.type]?.label }}
          </span>
        </div>
      </div>
    </div>

    <div class="panel-footer">
      <RouterLink to="/cliente/notificaciones" class="view-all">
        Ver todas las notificaciones
      </RouterLink>
    </div>
  </article>
</template>

<style scoped>
.activity-panel {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 10px;
  box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08);
  padding: 18px;
  display: flex;
  flex-direction: column;
  max-height: 500px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.panel-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.panel-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; }

.unread-badge {
  background: #fee2e2;
  color: #dc2626;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 999px;
}

.loading, .empty {
  padding: 24px;
  text-align: center;
  color: var(--color-muted);
}

.empty { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.empty-icon { font-size: 32px; }
.empty p { margin: 0; color: var(--color-navy); font-weight: 600; }
.empty small { font-size: 12px; }

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  flex: 1;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid var(--color-line);
  background: #fff;
  cursor: pointer;
  transition: .2s ease;
}

.activity-item:hover { border-color: var(--color-gold); background: #fdfcf8; }

.activity-item.unread {
  background: #f0f9ff;
  border-color: #bfdbfe;
}

.activity-item.unread:hover { background: #e0f2fe; }

.type-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 18px;
  flex-shrink: 0;
}

.activity-content { flex: 1; min-width: 0; }

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 4px;
}

.activity-header strong {
  color: var(--color-navy);
  font-size: 13px;
}

.time {
  color: var(--color-muted);
  font-size: 11px;
  white-space: nowrap;
}

.activity-content p {
  margin: 0 0 8px;
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.type-label {
  font-size: 11px;
  font-weight: 700;
}

.panel-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-line);
  text-align: center;
}

.view-all {
  color: var(--color-navy);
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}

.view-all:hover { color: var(--color-gold); }
</style>
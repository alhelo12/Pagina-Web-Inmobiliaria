<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { storeToRefs } from 'pinia'
import ClientDashboardHeader from '@/components/client/dashboard/ClientDashboardHeader.vue'

const router = useRouter()
const auth = useAuthStore()
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
  { key: 'unread', label: 'No leídas' }
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

const metrics = computed(() => ({
  total: stats.value.total,
  unread: stats.value.unread,
  approved: stats.value.approved,
  rejected: stats.value.rejected,
  sold: stats.value.sold
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
  <section class="notifications-page">
    <ClientDashboardHeader
      eyebrow="Panel de Cliente"
      title="Notificaciones"
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Cliente'"
      :profile-email="auth.userEmail || ''"
    />

    <div class="section-header">
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
      <button v-if="unreadCount > 0" class="mark-all-btn" @click="handleMarkAllRead">
        Marcar todas como leídas
      </button>
    </div>

    <section class="metrics">
      <article class="card">
        <div class="card-icon total-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        </div>
        <span>Total</span>
        <strong>{{ metrics.total }}</strong>
        <small>Notificaciones</small>
      </article>
      <article class="card highlight">
        <div class="card-icon unread-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        </div>
        <span>Sin leer</span>
        <strong>{{ metrics.unread }}</strong>
        <small>Nuevas</small>
      </article>
    </section>

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
  </section>
</template>

<style scoped>
.notifications-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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

.mark-all-btn {
  background: var(--color-gold);
  color: var(--color-navy);
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: 0.3s ease;
}

.mark-all-btn:hover {
  filter: brightness(1.03);
  box-shadow: 0 10px 18px rgba(7, 23, 45, 0.12);
}

.metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.card {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 10px 24px rgba(7, 23, 45, 0.08);
  transition: 0.3s ease;
  position: relative;
  overflow: hidden;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 32px rgba(7, 23, 45, 0.12);
}

.card-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.total-icon { background: #e8edf0; color: var(--color-navy-2); }
.unread-icon { background: #fef3c7; color: #b45309; }

.card span {
  color: var(--color-muted);
  font-size: 13px;
  font-weight: 600;
}

.card strong {
  display: block;
  margin-top: 8px;
  color: var(--color-navy);
  font-size: 30px;
  font-weight: 700;
}

.card small {
  color: #87909b;
  font-size: 12px;
}

.highlight {
  background: linear-gradient(150deg, rgba(214, 168, 72, 0.2) 0%, var(--color-card) 100%);
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

@media (max-width: 600px) {
  .metrics {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .metrics {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
  }

  .mark-all-btn {
    width: 100%;
  }
}
</style>
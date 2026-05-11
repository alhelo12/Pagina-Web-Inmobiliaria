<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { storeToRefs } from 'pinia'
import AdvisorDashboardHeader from '@/components/advisor/dashboard/AdvisorDashboardHeader.vue'
import AppIcon from '@/components/shared/AppIcon.vue'

const store = useNotificationsStore()
const { notifications, unreadCount, loading } = storeToRefs(store)

const filter = ref('all')

const filteredNotifications = computed(() => {
  if (filter.value === 'unread') {
    return notifications.value.filter(n => !n.is_read)
  }
  return notifications.value
})

const filters = [
  { key: 'all', label: 'Todas' },
  { key: 'unread', label: 'No leídas' }
]

const formatDate = (timestamp) => {
  if (!timestamp) return ''
  const diff = Date.now() - new Date(timestamp).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Ahora mismo'
  if (mins < 60) return `Hace ${mins} min`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `Hace ${hrs}h`
  const days = Math.floor(hrs / 24)
  if (days < 7) return `Hace ${days}d`
  return new Date(timestamp).toLocaleDateString('es-MX', { day: '2-digit', month: 'short' })
}

const typeIcons = {
  appointment: { icon: 'calendar', color: '#d6a848', label: 'Cita' },
  property_update: { icon: 'pencil', color: '#3b82f6', label: 'Actualizada' },
  property_approved: { icon: 'check', color: '#22c55e', label: 'Aprobada' },
  property_rejected: { icon: 'x-circle', color: '#dc2626', label: 'Rechazada' },
  property_sold: { icon: 'home', color: '#7c3aed', label: 'Vendida' },
  message: { icon: 'chat', color: '#6366f1', label: 'Mensaje' }
}

const markAsRead = async (id) => {
  await store.markAsRead(id)
}

const markAllAsRead = async () => {
  await store.markAllAsRead()
}

const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    await store.markAsRead(notification.id)
  }
}

onMounted(() => {
  store.fetchNotifications()
})
</script>

<template>
  <section class="notifications-page">
    <AdvisorDashboardHeader eyebrow="Panel del Asesor" title="Notificaciones" />

    <div class="section-header">
      <div class="filters">
        <button
          v-for="f in filters"
          :key="f.key"
          :class="['filter-btn', { active: filter === f.key }]"
          @click="filter = f.key"
        >
          {{ f.label }}
        </button>
      </div>
      <button v-if="unreadCount > 0" class="mark-all-btn" @click="markAllAsRead">
        Marcar todas como leídas
      </button>
    </div>

    <section class="metrics">
      <article class="card">
        <div class="card-icon total-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        </div>
        <span>Total</span>
        <strong>{{ notifications.length }}</strong>
        <small>Notificaciones</small>
      </article>
      <article class="card highlight">
        <div class="card-icon unread-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        </div>
        <span>Sin leer</span>
        <strong>{{ unreadCount }}</strong>
        <small>Nuevas</small>
      </article>
    </section>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Cargando notificaciones...</p>
    </div>

    <div v-else-if="!filteredNotifications.length" class="empty-state">
      <div class="empty-icon"><AppIcon name="bell" :size="48" /></div>
      <h3>No hay notificaciones</h3>
      <p>Tu actividad aparecerá aquí.</p>
    </div>

    <div v-else class="notifications-list">
      <article
        v-for="notif in filteredNotifications"
        :key="notif.id"
        :class="['notification-card', { unread: !notif.is_read }]"
        @click="handleNotificationClick(notif)"
      >
        <div
          class="type-icon"
          :style="{ backgroundColor: typeIcons[notif.type]?.color + '20', color: typeIcons[notif.type]?.color }"
        >
          <AppIcon :name="typeIcons[notif.type]?.icon || 'megaphone'" :size="22" />
        </div>

        <div class="notification-content">
          <div class="notification-header">
            <h3>{{ notif.title || typeIcons[notif.type]?.label || 'Notificación' }}</h3>
            <span
              class="type-badge"
              :style="{ backgroundColor: typeIcons[notif.type]?.color + '15', color: typeIcons[notif.type]?.color }"
            >
              {{ typeIcons[notif.type]?.label || notif.type }}
            </span>
          </div>
          <p>{{ notif.message }}</p>
          <div class="notification-meta">
            <span class="date">{{ formatDate(notif.created_at) }}</span>
            <span v-if="!notif.is_read" class="unread-dot"></span>
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
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-line);
  border-top-color: var(--color-gold);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
}

.empty-icon { color: var(--color-gold); display: block; margin-bottom: 16px; }

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
  .metrics { grid-template-columns: 1fr; }
  .section-header { flex-direction: column; align-items: stretch; }
  .mark-all-btn { width: 100%; }
}
</style>
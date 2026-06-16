<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { storeToRefs } from 'pinia'
import AdvisorDashboardHeader from '@/components/advisor/dashboard/AdvisorDashboardHeader.vue'
import AppIcon from '@/components/shared/AppIcon.vue'
import Breadcrumb from '@/components/shared/Breadcrumb.vue'
import NotificationSkeleton from '@/components/shared/NotificationSkeleton.vue'
import NotificationPreferences from '@/components/shared/NotificationPreferences.vue'
import {
  getNotificationMeta,
  getTypeFilters,
  groupByDate,
  formatDate
} from '@/constants/notifications'

const router = useRouter()
const store = useNotificationsStore()
const { notifications, unreadCount, loading } = storeToRefs(store)

const activeFilter = ref('all')
const showPreferences = ref(false)
const role = 'advisor'
const typeFilters = computed(() => getTypeFilters(role))

const filters = computed(() => [
  { key: 'all', label: 'Todas' },
  { key: 'unread', label: 'No leídas' },
  ...typeFilters.value.map(t => ({ key: t.key, label: t.label }))
])

const filteredNotifications = computed(() => {
  let result = notifications.value

  if (activeFilter.value === 'unread') {
    result = result.filter(n => !n.is_read)
  } else if (activeFilter.value !== 'all') {
    result = result.filter(n => n.type === activeFilter.value)
  }

  return result
})

const groupedNotifications = computed(() => {
  if (!Array.isArray(filteredNotifications.value)) return []
  return groupByDate(filteredNotifications.value)
})

const markAllAsRead = async () => {
  await store.markAllAsRead()
}

const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    await store.markAsRead(notification.id)
  }
  if (notification.property_id) {
    router.push(`/propiedades/${notification.property_id}`)
  } else {
    router.push('/advisor/notificaciones')
  }
}

const handleDelete = async (notificationId) => {
  await store.deleteNotification(notificationId)
}

onMounted(() => {
  store.fetchNotifications()
})
</script>

<template>
  <section class="notifications-page">
    <AdvisorDashboardHeader eyebrow="Panel del Asesor" title="Notificaciones" />
    <Breadcrumb :crumbs="[{ label: 'Notificaciones', path: '/advisor/notificaciones' }]" />

    <div class="section-header">
      <div class="filters">
        <button
          v-for="f in filters"
          :key="f.key"
          :class="['filter-btn', { active: activeFilter === f.key }]"
          @click="activeFilter = f.key"
        >
          {{ f.label }}
        </button>
      </div>
      <div class="header-actions-row">
        <button v-if="unreadCount > 0" class="mark-all-btn" @click="markAllAsRead">
          Marcar todas como leídas
        </button>
        <button class="prefs-btn" title="Preferencias" @click="showPreferences = true">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </button>
      </div>
    </div>
    <NotificationPreferences v-if="showPreferences" @close="showPreferences = false" />

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
      <NotificationSkeleton :count="4" />
    </div>

    <div v-else-if="!filteredNotifications.length" class="empty-state">
      <div class="empty-icon"><AppIcon name="bell" :size="48" /></div>
      <h3>No hay notificaciones</h3>
      <p>Tu actividad aparecerá aquí.</p>
    </div>

    <div v-else class="notifications-list">
      <template v-for="section in groupedNotifications" :key="section.group">
        <div class="date-group-header">{{ section.group }}</div>
        <article
          v-for="notif in section.items"
          :key="notif.id"
          :class="['notification-card', { unread: !notif.is_read }]"
          @click="handleNotificationClick(notif)"
        >
          <div
            class="type-icon"
            :style="{
              backgroundColor: getNotificationMeta(notif.type).color + '20',
              color: getNotificationMeta(notif.type).color
            }"
          >
            <AppIcon :name="getNotificationMeta(notif.type).icon" :size="22" />
          </div>

          <div class="notification-content">
            <div class="notification-header">
              <h3>{{ notif.title }}</h3>
              <div class="header-actions">
                <span
                  class="type-badge"
                  :style="{
                    backgroundColor: getNotificationMeta(notif.type).color + '15',
                    color: getNotificationMeta(notif.type).color
                  }"
                >
                  {{ getNotificationMeta(notif.type).label }}
                </span>
                <button
                  class="delete-btn"
                  title="Eliminar"
                  @click.stop="handleDelete(notif.id)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </button>
              </div>
            </div>
            <p>{{ notif.message }}</p>
            <div class="notification-meta">
              <span class="date">{{ formatDate(notif.created_at) }}</span>
              <span v-if="!notif.is_read" class="unread-dot"></span>
            </div>
          </div>
        </article>
      </template>
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

.header-actions-row {
  display: flex;
  align-items: center;
  gap: 8px;
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

.prefs-btn {
  background: transparent;
  border: 1px solid var(--color-line);
  color: var(--color-muted);
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: 0.3s ease;
}

.prefs-btn:hover {
  border-color: var(--color-gold);
  color: var(--color-navy);
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
  padding: 4px;
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
}

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

.date-group-header {
  font-size: 13px;
  font-weight: 700;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 4px 4px 0;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.type-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  white-space: nowrap;
}

.delete-btn {
  background: transparent;
  border: none;
  color: #d1d5db;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: color 0.2s ease, background 0.2s ease;
}

.delete-btn:hover {
  color: #dc2626;
  background: #fef2f2;
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
  .notification-card { flex-direction: column; gap: 12px; }
  .type-icon { width: 36px; height: 36px; }
  .notification-header { flex-direction: column; gap: 6px; }
  .notification-header h3 { font-size: 14px; }
  .card strong { font-size: 24px; }
}
</style>

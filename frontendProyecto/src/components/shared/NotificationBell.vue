<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { useAuthStore } from '@/stores/authStore'
import { storeToRefs } from 'pinia'
import AppIcon from '@/components/shared/AppIcon.vue'
import { useNotificationWebSocket } from '@/composables/useNotificationWebSocket'
import {
  getNotificationMeta,
  groupByDate,
  formatRelativeTime
} from '@/constants/notifications'

const router = useRouter()
const store = useNotificationsStore()
const auth = useAuthStore()
const { notifications, unreadCount, loading } = storeToRefs(store)

const { connect: wsConnect, disconnect: wsDisconnect } = useNotificationWebSocket()
const dropdownOpen = ref(false)
const dropdownRef = ref(null)
let pollInterval = null

const role = computed(() => auth.role)
const basePath = computed(() => {
  if (role.value === 'advisor') return '/advisor/notificaciones'
  return '/cliente/notificaciones'
})

const grouped = computed(() => {
  if (!Array.isArray(notifications.value)) return []
  return groupByDate(notifications.value.slice(0, 10))
})

const handleOutsideClick = (event) => {
  if (!dropdownRef.value || !dropdownRef.value.contains(event.target)) {
    dropdownOpen.value = false
  }
}

const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    await store.markAsRead(notification.id)
  }
  dropdownOpen.value = false
  if (notification.property_id) {
    router.push(`/propiedades/${notification.property_id}`)
  } else {
    router.push(basePath.value)
  }
}

const handleBellClick = () => {
  dropdownOpen.value = !dropdownOpen.value
}

const handleDelete = async (event, notificationId) => {
  event.stopPropagation()
  await store.deleteNotification(notificationId)
}

const handleMarkAllRead = async () => {
  await store.markAllAsRead()
}

const safeWsConnect = () => {
  try {
    wsConnect()
  } catch (e) {
    // WebSocket connection failed — polling fallback will handle it
  }
}

onMounted(() => {
  if (!auth.isLogged || !auth.token) return
  store.fetchNotifications()
  store.fetchUnreadCount()
  safeWsConnect()
  // Polling fallback cada 60s por si WebSocket falla
  pollInterval = setInterval(() => {
    store.fetchUnreadCount()
  }, 60000)
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
  wsDisconnect()
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<template>
  <div ref="dropdownRef" class="notification-bell">
    <button class="bell-btn" @click="handleBellClick">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
      </svg>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
    </button>

    <transition name="dropdown">
      <div v-if="dropdownOpen" class="dropdown">
        <div class="dropdown-header">
          <h4>Notificaciones</h4>
          <button v-if="unreadCount > 0" class="mark-all-btn" @click="handleMarkAllRead">
            Marcar todas como leídas
          </button>
        </div>

        <div v-if="loading" class="loading">Cargando...</div>

        <div v-else-if="!notifications.length" class="empty">
          No tienes notificaciones
        </div>

        <div v-else class="notifications-list">
          <template v-for="section in grouped" :key="section.group">
            <div class="date-group-label">{{ section.group }}</div>
            <div
              v-for="notification in section.items"
              :key="notification.id"
              :class="['notification-item', { unread: !notification.is_read }]"
              @click="handleNotificationClick(notification)"
            >
              <span
                class="icon"
                :style="{
                  backgroundColor: getNotificationMeta(notification.type).color + '20',
                  color: getNotificationMeta(notification.type).color
                }"
              >
                <AppIcon :name="getNotificationMeta(notification.type).icon" :size="16" />
              </span>
              <div class="content">
                <strong>{{ notification.title }}</strong>
                <p>{{ notification.message }}</p>
                <small>{{ formatRelativeTime(notification.created_at) }}</small>
              </div>
              <button
                class="delete-btn"
                title="Eliminar"
                @click="handleDelete($event, notification.id)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </template>
        </div>

        <div class="dropdown-footer">
          <RouterLink :to="basePath" @click="dropdownOpen = false">
            Ver todas las notificaciones
          </RouterLink>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.notification-bell {
  position: relative;
}

.bell-btn {
  position: relative;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.92);
  cursor: pointer;
  padding: 8px;
  display: grid;
  place-items: center;
  transition: color 0.3s ease;
}

.bell-btn:hover {
  color: #f7d9a6;
}

.badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background: #dc2626;
  color: white;
  font-size: 10px;
  font-weight: 900;
  min-width: 16px;
  height: 16px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  padding: 0 4px;
}

.dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 360px;
  max-height: 480px;
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 20px 35px rgba(15, 23, 42, 0.16);
  border: 1px solid #e7ebf3;
  display: flex;
  flex-direction: column;
  z-index: 1000;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e7ebf3;
}

.dropdown-header h4 {
  margin: 0;
  color: #07172d;
  font-size: 16px;
  font-weight: 700;
}

.mark-all-btn {
  background: transparent;
  border: none;
  color: #3b82f6;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.mark-all-btn:hover {
  text-decoration: underline;
}

.loading, .empty {
  padding: 32px;
  text-align: center;
  color: #65717e;
}

.notifications-list {
  overflow-y: auto;
  flex: 1;
}

.date-group-label {
  padding: 8px 16px 4px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #9ca3af;
  background: #ffffff;
  position: sticky;
  top: 0;
  z-index: 1;
}

.notification-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s ease;
  border-bottom: 1px solid #f0f0f0;
  align-items: flex-start;
}

.notification-item:hover {
  background: #f8fafc;
}

.notification-item.unread {
  background: #f0f9ff;
}

.notification-item.unread:hover {
  background: #e0f2fe;
}

.notification-item .icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 18px;
  flex-shrink: 0;
}

.notification-item .content {
  flex: 1;
  min-width: 0;
}

.notification-item strong {
  display: block;
  color: #07172d;
  font-size: 13px;
  margin-bottom: 4px;
}

.notification-item p {
  margin: 0 0 4px;
  color: #65717e;
  font-size: 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-item small {
  color: #9ca3af;
  font-size: 11px;
}

.delete-btn {
  background: transparent;
  border: none;
  color: #d1d5db;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  flex-shrink: 0;
  transition: color 0.2s ease, background 0.2s ease;
  opacity: 0;
}

.notification-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #dc2626;
  background: #fef2f2;
}

.dropdown-footer {
  padding: 12px 16px;
  border-top: 1px solid #e7ebf3;
  text-align: center;
}

.dropdown-footer a {
  color: #3b82f6;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}

.dropdown-footer a:hover {
  text-decoration: underline;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 480px) {
  .dropdown {
    width: 100%;
    right: 0;
    left: 0;
  }
}
</style>

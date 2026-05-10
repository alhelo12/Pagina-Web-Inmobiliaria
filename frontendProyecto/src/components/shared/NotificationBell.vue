<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { storeToRefs } from 'pinia'

const router = useRouter()
const store = useNotificationsStore()
const { notifications, unreadCount, loading } = storeToRefs(store)

const dropdownOpen = ref(false)
const dropdownRef = ref(null)
let pollInterval = null

const typeIcons = {
  advisor_assigned: '👤',
  approved: '✅',
  rejected: '❌',
  sold: '🏠',
  property_updated: '✏️'
}

const typeColors = {
  advisor_assigned: '#d6a848',
  approved: '#22c55e',
  rejected: '#dc2626',
  sold: '#7c3aed',
  property_updated: '#3b82f6'
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
  }
}

const handleMarkAllRead = async () => {
  await store.markAllAsRead()
}

onMounted(() => {
  store.fetchNotifications()
  store.fetchUnreadCount()
  pollInterval = setInterval(() => {
    store.fetchUnreadCount()
  }, 30000)
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<template>
  <div ref="dropdownRef" class="notification-bell">
    <button class="bell-btn" @click.stop="dropdownOpen = !dropdownOpen">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
      </svg>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
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
          <div
            v-for="notification in notifications.slice(0, 10)"
            :key="notification.id"
            :class="['notification-item', { unread: !notification.is_read }]"
            @click="handleNotificationClick(notification)"
          >
            <span class="icon" :style="{ backgroundColor: typeColors[notification.type] + '20', color: typeColors[notification.type] }">
              {{ typeIcons[notification.type] || '📢' }}
            </span>
            <div class="content">
              <strong>{{ notification.title }}</strong>
              <p>{{ notification.message }}</p>
              <small>{{ formatRelativeTime(notification.created_at) }}</small>
            </div>
          </div>
        </div>

        <div class="dropdown-footer">
          <RouterLink to="/cliente/notificaciones" @click="dropdownOpen = false">
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

.notification-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s ease;
  border-bottom: 1px solid #f0f0f0;
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
    width: calc(100vw - 32px);
    right: -16px;
  }
}
</style>
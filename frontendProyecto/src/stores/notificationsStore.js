import { defineStore } from 'pinia'
import { notificationsApi } from '@/api/notifications'
import { useAuthStore } from './authStore'

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    notifications: [],
    unreadCount: 0,
    loading: false,
    error: null
  }),

  getters: {
    recentNotifications: (state) => state.notifications.slice(0, 5),
    hasUnread: (state) => state.unreadCount > 0
  },

  actions: {
    async fetchNotifications(params = {}) {
      const auth = useAuthStore()
      if (!auth.isLogged) return

      this.loading = true
      this.error = null
      try {
        const { data } = await notificationsApi.getAll({ user_id: auth.userId, ...params })
        this.notifications = data.notifications ?? []
        this.unreadCount = data.unread_count ?? 0
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar notificaciones'
      } finally {
        this.loading = false
      }
    },

    async fetchUnreadCount() {
      const auth = useAuthStore()
      if (!auth.isLogged) return

      try {
        const { data } = await notificationsApi.getUnreadCount({ user_id: auth.userId })
        this.unreadCount = data.unread_count ?? 0
      } catch (err) {
        console.error('Error al obtener conteo de notificaciones:', err)
      }
    },

    async markAsRead(notificationId) {
      try {
        await notificationsApi.markAsRead(notificationId)
        const notification = this.notifications.find(n => n.id === notificationId)
        if (notification && !notification.is_read) {
          notification.is_read = true
          this.unreadCount = Math.max(0, this.unreadCount - 1)
        }
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al marcar como leída'
      }
    },

    async markAllAsRead() {
      try {
        await notificationsApi.markAllAsRead()
        this.notifications.forEach(n => n.is_read = true)
        this.unreadCount = 0
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al marcar todas como leídas'
      }
    },

    clear() {
      this.notifications = []
      this.unreadCount = 0
      this.error = null
    }
  }
})
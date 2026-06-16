import api from './axios'

export const notificationsApi = {
  getAll(params = {}) {
    return api.get('/notifications', { params })
  },

  getUnreadCount() {
    return api.get('/notifications/unread-count')
  },

  markAsRead(notificationId) {
    return api.patch(`/notifications/${notificationId}/read`)
  },

  markAllAsRead() {
    return api.patch('/notifications/read-all')
  },

  delete(notificationId) {
    return api.delete(`/notifications/${notificationId}`)
  },

  getMeta() {
    return api.get('/notifications/meta')
  }
}
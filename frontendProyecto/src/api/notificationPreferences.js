import api from './axios'

export const notificationPreferencesApi = {
  getAll() {
    return api.get('/notifications/preferences')
  },

  update(type, enabled) {
    return api.put(`/notifications/preferences/${type}`, { enabled })
  }
}

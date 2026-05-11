import { defineStore } from 'pinia'
import api from '@/api/axios'
import { useAuthStore } from './authStore'

export const useMessagesStore = defineStore('messages', {
  state: () => ({
    conversations: [],
    unreadCount: 0,
    loading: false,
    error: null
  }),

  getters: {
    hasUnread: (state) => state.unreadCount > 0
  },

  actions: {
    async fetchConversations() {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.get('/messages/conversations')
        this.conversations = data.items ?? []
        this.unreadCount = this.conversations.reduce((sum, c) => sum + (c.unread_count || 0), 0)
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar conversaciones'
      } finally {
        this.loading = false
      }
    },

    clear() {
      this.conversations = []
      this.unreadCount = 0
      this.error = null
    }
  }
})

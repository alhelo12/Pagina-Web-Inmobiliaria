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

    async markConversationRead(conversationId) {
      const auth = useAuthStore()
      try {
        await api.get(`/messages?conversation_id=${conversationId}`, {
          headers: { ...auth.authHeaders }
        })
        const conv = this.conversations.find(c => c.id === conversationId)
        if (conv) {
          this.unreadCount -= (conv.unread_count || 0)
          conv.unread_count = 0
        }
      } catch (err) {
        console.error('Error al marcar conversación como leída:', err)
      }
    },

    clear() {
      this.conversations = []
      this.unreadCount = 0
      this.error = null
    }
  }
})

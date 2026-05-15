import { defineStore } from 'pinia'
import api from '@/api/axios'
import { useAuthStore } from './authStore'

export const useMessagesStore = defineStore('messages', {
  state: () => ({
    conversations: [],
    totalConversations: 0,
    messages: [],
    totalMessages: 0,
    hasMoreMessages: false,
    unreadCount: 0,
    loading: false,
    error: null,
    searchQuery: '',
    filter: 'all',
    typingUsers: {},
  }),

  getters: {
    hasUnread: (state) => state.unreadCount > 0,

    filteredConversations: (state) => {
      let result = state.conversations

      if (state.searchQuery) {
        const q = state.searchQuery.toLowerCase()
        result = result.filter(c =>
          (c.user_name || '').toLowerCase().includes(q) ||
          (c.advisor_name || '').toLowerCase().includes(q) ||
          (c.last_message || '').toLowerCase().includes(q)
        )
      }

      if (state.filter === 'unread') {
        result = result.filter(c => c.unread_count > 0)
      }

      if (state.filter === 'unread') {
        result.sort((a, b) => {
          if (a.unread_count > 0 && b.unread_count === 0) return -1
          if (a.unread_count === 0 && b.unread_count > 0) return 1
          return 0
        })
      }

      return result
    },

    isTyping: (state) => (conversationId) => {
      return !!state.typingUsers[conversationId]
    },
  },

  actions: {
    async fetchConversations(page = 1, limit = 50) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.get('/messages/conversations', {
          params: { page, limit }
        })
        this.conversations = data.items ?? []
        this.totalConversations = data.total ?? 0
        this.unreadCount = this.conversations.reduce((sum, c) => sum + (c.unread_count || 0), 0)
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar conversaciones'
      } finally {
        this.loading = false
      }
    },

    async fetchMessages(conversationId, { limit = 50, offset = 0, before } = {}) {
      this.loading = true
      this.error = null
      try {
        const params = { conversation_id: conversationId, limit, offset }
        if (before) params.before = before
        const { data } = await api.get('/messages', { params })
        this.messages = data.items ?? []
        this.totalMessages = data.total ?? 0
        this.hasMoreMessages = data.has_more ?? false
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al cargar mensajes'
      } finally {
        this.loading = false
      }
    },

    async markAsRead(conversationId) {
      const auth = useAuthStore()
      try {
        const { data } = await api.post(`/messages/conversations/${conversationId}/read`, {}, {
          headers: { ...auth.authHeaders }
        })
        const conv = this.conversations.find(c => c.id === conversationId)
        if (conv) {
          this.unreadCount -= (conv.unread_count || 0)
          conv.unread_count = 0
        }
        return data
      } catch (err) {
        console.error('Error al marcar conversacion como leida:', err)
      }
    },

    async sendMessageViaRest(conversationId, content) {
      const auth = useAuthStore()
      try {
        const { data } = await api.post('/messages', {
          conversation_id: conversationId,
          content
        }, {
          headers: { ...auth.authHeaders }
        })
        this.messages.push(data)
        const conv = this.conversations.find(c => c.id === conversationId)
        if (conv) {
          conv.last_message = content
          conv.last_message_at = new Date().toISOString()
        }
        return data
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Error al enviar mensaje'
        throw err
      }
    },

    addWebSocketMessage(msgData) {
      const exists = this.messages.some(m => m.id === msgData.id)
      if (!exists) {
        this.messages.push(msgData)
      }
      const conv = this.conversations.find(c => c.id === msgData.conversation_id)
      if (conv) {
        conv.last_message = msgData.content
        conv.last_message_at = msgData.created_at
      }
    },

    setTyping(conversationId, userId, isTyping) {
      if (isTyping) {
        this.typingUsers[conversationId] = userId
      } else {
        if (this.typingUsers[conversationId] === userId) {
          delete this.typingUsers[conversationId]
        }
      }
    },

    setSearchQuery(query) {
      this.searchQuery = query
    },

    setFilter(filter) {
      this.filter = filter
    },

    clear() {
      this.conversations = []
      this.totalConversations = 0
      this.messages = []
      this.totalMessages = 0
      this.hasMoreMessages = false
      this.unreadCount = 0
      this.error = null
      this.searchQuery = ''
      this.filter = 'all'
      this.typingUsers = {}
    }
  }
})

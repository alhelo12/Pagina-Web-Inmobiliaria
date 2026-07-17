import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useWebSocket } from '@/composables/useWebSocket'
import { formatDateGroup } from '@/utils/chatUtils'
import apiClient from '@/api/axios'

export function useChat({ role, roleName, autoConnect = true }) {
  const auth = useAuthStore()
  
  const conversations = ref([])
  const messages = ref([])
  const selectedConversation = ref(null)
  const newMessage = ref('')
  const loading = ref(true)
  const sending = ref(false)
  const sendError = ref(false)
  const showConversations = ref(true)
  const messagesContainer = ref(null)
  const typingTimeout = ref(null)
  const isOtherTyping = ref(false)
  const soundEnabled = ref(false)
  const pollingInterval = ref(null)
  
  // Advisor-specific filters
  const searchQuery = ref('')
  const filterType = ref('all')

  function playNotificationSound() {
    if (!soundEnabled.value) return
    try {
      new Audio('/notification.mp3').play()
    } catch { /* fallback silencioso */ }
  }

  function handleWebSocketMessage(msgData) {
    // Dedupe: quita mensaje optimista duplicado
    messages.value = messages.value.filter(m => 
      !(typeof m.id === 'string' && m.id.startsWith('opt-') && 
        m.conversation_id === msgData.conversation_id && 
        m.content === msgData.content)
    )
    const exists = messages.value.some(m => m.id === msgData.id)
    if (!exists) {
      messages.value.push(msgData)
      if (msgData.sender_id !== auth.userId) {
        playNotificationSound()
      }
      nextTick(() => scrollToBottom())
    }
    const conv = conversations.value.find(c => c.id === msgData.conversation_id)
    if (conv) {
      conv.last_message = msgData.content
      conv.last_message_at = msgData.created_at
    }
  }

  function handleWebSocketTyping(data) {
    if (selectedConversation.value && data.conversation_id === selectedConversation.value.id) {
      isOtherTyping.value = true
      clearTimeout(typingTimeout.value)
      typingTimeout.value = setTimeout(() => {
        isOtherTyping.value = false
      }, 3000)
    }
  }

  const { connected: wsConnected, connect, disconnect, send, sendTyping } = useWebSocket({
    onMessage: handleWebSocketMessage,
    onTyping: handleWebSocketTyping,
    autoConnect: false
  })

  const fetchConversations = async () => {
    try {
      const { data } = await apiClient.get('/messages/conversations')
      conversations.value = data.items || []
    } catch (err) {
      console.error('Error fetching conversations:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchMessages = async (conversationId) => {
    try {
      const { data } = await apiClient.get('/messages', { params: { conversation_id: conversationId } })
      const serverIds = new Set((data.items || []).map(m => m.id))
      const optimisticMsgs = messages.value.filter(m => 
        typeof m.id === 'string' && m.id.startsWith('opt-') && !serverIds.has(m.id)
      )
      messages.value = [...(data.items || []), ...optimisticMsgs]
      nextTick(() => scrollToBottom())
    } catch (err) {
      console.error('Error fetching messages:', err)
    }
  }

  const selectConversation = async (conv) => {
    selectedConversation.value = conv
    showConversations.value = false
    isOtherTyping.value = false
    try {
      await apiClient.post(`/messages/conversations/${conv.id}/read`)
      conv.unread_count = 0
    } catch {
      conv.unread_count = 0
    }
    await fetchMessages(conv.id)
  }

  const backToConversations = () => {
    showConversations.value = true
  }

  const sendMessage = async () => {
    if (!newMessage.value.trim() || !selectedConversation.value || sending.value) return
    sending.value = true
    sendError.value = false

    const content = newMessage.value.trim()
    const userId = Number(auth.userId)
    const optimisticMsg = {
      id: `opt-${Date.now()}`,
      conversation_id: selectedConversation.value.id,
      sender_id: userId,
      content,
      is_read: false,
      created_at: new Date().toISOString(),
      sender: { id: userId, name: roleName === 'advisor' ? 'Tu' : 'Tu', role: role }
    }

    if (wsConnected.value) {
      messages.value.push(optimisticMsg)
      newMessage.value = ''
      nextTick(() => scrollToBottom())

      try {
        const sent = send('message', {
          conversation_id: selectedConversation.value.id,
          content
        })
        if (!sent) {
          messages.value = messages.value.filter(m => m.id !== optimisticMsg.id)
          sendError.value = true
        }
      } catch (err) {
        messages.value = messages.value.filter(m => m.id !== optimisticMsg.id)
        sendError.value = true
        console.error('Error sending message via WS:', err)
      }
    } else {
      try {
        messages.value.push(optimisticMsg)
        newMessage.value = ''
        nextTick(() => scrollToBottom())

        const { data } = await apiClient.post('/messages', {
          conversation_id: selectedConversation.value.id,
          content
        })
        const idx = messages.value.findIndex(m => m.id === optimisticMsg.id)
        if (idx !== -1) {
          messages.value[idx] = data
        } else {
          messages.value.push(data)
        }
      } catch (err) {
        messages.value = messages.value.filter(m => m.id !== optimisticMsg.id)
        sendError.value = true
        console.error('Error sending message:', err)
      }
    }

    sending.value = false
  }

  const handleTyping = () => {
    if (selectedConversation.value && wsConnected.value) {
      sendTyping(selectedConversation.value.id)
    }
  }

  const scrollToBottom = () => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }

  // Helper para nombre del remitente
  const messageSenderName = (msg) => {
    if (msg.sender_id === auth.userId) return 'Tu'
    return msg.sender_name || msg.sender?.name || (selectedConversation.value ? getConversationName(selectedConversation.value) : '')
  }

  // Helper para nombre de la conversación
  const getConversationName = (conv) => {
    return conv.user_name || conv.client_name || conv.other_user_name || 'Usuario'
  }

  // Mensajes agrupados por fecha
  const groupedMessages = computed(() => {
    const groups = []
    let currentGroup = null

    for (const msg of messages.value) {
      const dateLabel = formatDateGroup(msg.created_at)
      if (!currentGroup || currentGroup.label !== dateLabel) {
        currentGroup = { label: dateLabel, messages: [] }
        groups.push(currentGroup)
      }
      currentGroup.messages.push(msg)
    }

    return groups
  })

  // Filtros de asesor
  const filteredConversations = computed(() => {
    let result = conversations.value

    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      result = result.filter(c =>
        (c.user_name || '').toLowerCase().includes(q) ||
        (c.advisor_name || '').toLowerCase().includes(q) ||
        (c.last_message || '').toLowerCase().includes(q)
      )
    }

    if (filterType.value === 'unread') {
      result = result.filter(c => c.unread_count > 0)
      result.sort((a, b) => b.unread_count - a.unread_count)
    }

    return result
  })

  const totalUnread = computed(() =>
    conversations.value.reduce((sum, c) => sum + (c.unread_count || 0), 0)
  )

  // Polling fallback
  function startPolling() {
    stopPolling()
    pollingInterval.value = setInterval(() => {
      if (!wsConnected.value && selectedConversation.value) {
        fetchMessages(selectedConversation.value.id)
      }
    }, 5000)
  }

  function stopPolling() {
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value)
      pollingInterval.value = null
    }
  }

  onMounted(async () => {
    await fetchConversations()
    if (autoConnect) connect()
    startPolling()
  })

  onUnmounted(() => {
    disconnect()
    stopPolling()
  })

  return {
    // State
    conversations,
    messages,
    selectedConversation,
    newMessage,
    loading,
    sending,
    sendError,
    showConversations,
    messagesContainer,
    typingTimeout,
    isOtherTyping,
    soundEnabled,
    pollingInterval,
    searchQuery,
    filterType,
    wsConnected,
    
    // Computed
    groupedMessages,
    filteredConversations,
    totalUnread,
    messageSenderName,
    getConversationName,
    
    // Methods
    fetchConversations,
    fetchMessages,
    selectConversation,
    backToConversations,
    sendMessage,
    handleTyping,
    scrollToBottom,
    playNotificationSound,
  }
}
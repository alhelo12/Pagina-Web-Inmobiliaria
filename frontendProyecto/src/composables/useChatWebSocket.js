import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const MAX_RECONNECT_DELAY = 30000
const BASE_RECONNECT_DELAY = 1000

export function useChatWebSocket(onMessage, onTyping) {
  const auth = useAuthStore()
  const ws = ref(null)
  const wsConnected = ref(false)
  const reconnectAttempts = ref(0)
  let reconnectTimer = null

  function connect() {
    const token = auth.backendToken || auth.token
    if (!token) return

    const wsUrl = `${import.meta.env.VITE_API_URL.replace('http', 'ws')}/ws/messages?token=${token}`
    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      wsConnected.value = true
      reconnectAttempts.value = 0
    }

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'message' && onMessage) {
        onMessage(data.data)
      } else if (data.type === 'typing' && onTyping) {
        onTyping(data)
      }
    }

    ws.value.onclose = () => {
      wsConnected.value = false
      scheduleReconnect()
    }

    ws.value.onerror = () => {
      wsConnected.value = false
    }
  }

  function scheduleReconnect() {
    if (reconnectTimer) return
    const delay = Math.min(BASE_RECONNECT_DELAY * Math.pow(2, reconnectAttempts.value), MAX_RECONNECT_DELAY)
    reconnectAttempts.value++
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      connect()
    }, delay)
  }

  function send(type, payload) {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify({ type, ...payload }))
      return true
    }
    return false
  }

  function sendMessage(conversationId, content) {
    return send('message', { conversation_id: conversationId, content })
  }

  function sendTyping(conversationId) {
    return send('typing', { conversation_id: conversationId })
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    wsConnected.value = false
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    ws,
    wsConnected,
    connect,
    disconnect,
    send,
    sendMessage,
    sendTyping,
  }
}

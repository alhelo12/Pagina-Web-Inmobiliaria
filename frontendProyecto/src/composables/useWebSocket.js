import { ref, onUnmounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const MAX_RECONNECT_DELAY = 30000
const BASE_RECONNECT_DELAY = 1000

export function useWebSocket(options = {}) {
  const {
    onMessage = null,
    onNotification = null,
    onTyping = null,
    heartbeat = true,
    autoConnect = true,
  } = options

  const auth = useAuthStore()
  const ws = ref(null)
  const connected = ref(false)
  const reconnectAttempts = ref(0)
  let reconnectTimer = null
  let heartbeatTimer = null

  function getUrl() {
    const token = auth.backendToken
    if (!token) return null
    const base = import.meta.env.VITE_WS_URL || import.meta.env.VITE_API_URL?.replace('http', 'ws') || 'ws://localhost:8000'
    return `${base}/ws?token=${token}`
  }

  function connect() {
    const url = getUrl()
    if (!url || ws.value) return

    const socket = new WebSocket(url)

    socket.onopen = () => {
      connected.value = true
      reconnectAttempts.value = 0
      if (heartbeat) {
        heartbeatTimer = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'ping' }))
          }
        }, 30000)
      }
    }

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'notification' && onNotification) {
          onNotification(msg.data)
        } else if (msg.type === 'message' && onMessage) {
          onMessage(msg.data)
        } else if (msg.type === 'typing' && onTyping) {
          onTyping(msg)
        }
      } catch { /* ignore parse errors */ }
    }

    socket.onclose = () => {
      connected.value = false
      ws.value = null
      if (heartbeatTimer) clearInterval(heartbeatTimer)
      scheduleReconnect()
    }

    socket.onerror = () => {
      socket.close()
    }

    ws.value = socket
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
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
    if (ws.value) {
      ws.value.onclose = null
      ws.value.close()
      ws.value = null
    }
    connected.value = false
  }

  if (autoConnect) {
    nextTick(connect)
  }

  onUnmounted(disconnect)

  return { ws, connected, connect, disconnect, send, sendMessage, sendTyping }
}

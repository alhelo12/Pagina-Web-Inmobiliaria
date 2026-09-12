import { ref, onUnmounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const MAX_RECONNECT_DELAY = 30000
const BASE_RECONNECT_DELAY = 1000
const MAX_RECONNECT_ATTEMPTS = 10
// 4001/4003: token inválido o usuario inactivo. 1008: política del servidor.
const AUTH_CLOSE_CODES = new Set([4001, 4003, 1008])

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
    const base = import.meta.env.VITE_WS_URL || import.meta.env.VITE_API_URL?.replace('http', 'ws') || 'ws://localhost:8000'
    return `${base}/ws`
  }

  function connect() {
    const token = auth.backendToken
    if (!token || ws.value) return

    // El JWT viaja en el subprotocolo, nunca en la URL (evita logs/APM)
    const socket = new WebSocket(getUrl(), [`bearer.${token}`])

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

    socket.onclose = (event) => {
      connected.value = false
      ws.value = null
      if (heartbeatTimer) clearInterval(heartbeatTimer)
      // Token rechazado: reintentar no sirve y genera storm
      if (AUTH_CLOSE_CODES.has(event.code)) return
      scheduleReconnect()
    }

    socket.onerror = () => {
      socket.close()
    }

    ws.value = socket
  }

  function scheduleReconnect() {
    if (reconnectTimer) return
    if (reconnectAttempts.value >= MAX_RECONNECT_ATTEMPTS) return
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

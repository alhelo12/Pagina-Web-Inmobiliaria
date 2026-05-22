import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { useToast } from '@/composables/useToast'
import { playNotificationSound } from '@/utils/notificationSound'

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export function useNotificationWebSocket() {
  const ws = ref(null)
  const connected = ref(false)
  let reconnectTimer = null
  let heartbeatTimer = null

  const auth = useAuthStore()
  const store = useNotificationsStore()
  const { addToast } = useToast()

  const connect = () => {
    if (!auth.token || ws.value) return

    const url = `${WS_BASE}/ws/notifications?token=${auth.token}`
    const socket = new WebSocket(url)

    socket.onopen = () => {
      connected.value = true
      // Heartbeat every 30s
      heartbeatTimer = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: 'ping' }))
        }
      }, 30000)
    }

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'notification') {
          const notif = msg.data
          store.addNotification(notif)
          playNotificationSound()
          addToast({
            title: notif.title,
            message: notif.message,
            type: 'info',
            duration: 5000
          })
        }
      } catch (e) {
        // ignore parse errors
      }
    }

    socket.onclose = () => {
      connected.value = false
      ws.value = null
      if (heartbeatTimer) clearInterval(heartbeatTimer)
      // Reconnect after 5s
      reconnectTimer = setTimeout(connect, 5000)
    }

    socket.onerror = () => {
      socket.close()
    }

    ws.value = socket
  }

  const disconnect = () => {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (heartbeatTimer) clearInterval(heartbeatTimer)
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    connected.value = false
  }

  onUnmounted(() => {
    disconnect()
  })

  return { connect, disconnect, connected }
}

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import AdvisorDashboardHeader from '@/components/advisor/dashboard/AdvisorDashboardHeader.vue'
import AppIcon from '@/components/shared/AppIcon.vue'

const auth = useAuthStore()

const conversations = ref([])
const messages = ref([])
const selectedConversation = ref(null)
const newMessage = ref('')
const loading = ref(true)
const sending = ref(false)
const polling = ref(null)

const fetchConversations = async () => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/messages/conversations?advisor_id=${auth.userId}`, {
      headers: { ...auth.authHeaders }
    })
    if (res.ok) {
      const data = await res.json()
      conversations.value = data.items || data
    }
  } catch (err) {
    console.error('Error fetching conversations:', err)
  } finally {
    loading.value = false
  }
}

const fetchMessages = async (conversationId) => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/messages?conversation_id=${conversationId}`, {
      headers: { ...auth.authHeaders }
    })
    if (res.ok) {
      const data = await res.json()
      messages.value = data.items || data
      nextTick(() => scrollToBottom())
    }
  } catch (err) {
    console.error('Error fetching messages:', err)
  }
}

const selectConversation = (conv) => {
  selectedConversation.value = conv
  fetchMessages(conv.id)
  startPolling()
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedConversation.value || sending.value) return
  sending.value = true
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/messages`, {
      method: 'POST',
      headers: { ...auth.authHeaders, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversation_id: selectedConversation.value.id,
        sender_id: auth.userId,
        content: newMessage.value.trim()
      })
    })
    if (res.ok) {
      const msg = await res.json()
      messages.value.push(msg)
      newMessage.value = ''
      nextTick(() => scrollToBottom())
    }
  } catch (err) {
    console.error('Error sending message:', err)
  } finally {
    sending.value = false
  }
}

const scrollToBottom = () => {
  const container = document.querySelector('.messages-container')
  if (container) container.scrollTop = container.scrollHeight
}

const startPolling = () => {
  stopPolling()
  if (selectedConversation.value) {
    polling.value = setInterval(() => {
      fetchMessages(selectedConversation.value.id)
    }, 5000)
  }
}

const stopPolling = () => {
  if (polling.value) clearInterval(polling.value)
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
}

const getConversationName = (conv) => {
  if (conv.client) return conv.client.name || 'Cliente'
  return 'Cliente'
}

onMounted(() => {
  fetchConversations()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <div class="chat-page">
    <AdvisorDashboardHeader eyebrow="Panel del Asesor" title="Mensajes" />

    <div class="chat-container">
      <aside class="conversations-list">
        <h3>Conversaciones</h3>
        
        <div v-if="loading" class="loading">Cargando...</div>
        
        <div v-else-if="conversations.length === 0" class="empty">
          <p>No tienes conversaciones</p>
        </div>
        
        <div v-else>
          <div 
            v-for="conv in conversations" 
            :key="conv.id"
            :class="['conversation-item', { active: selectedConversation?.id === conv.id }]"
            @click="selectConversation(conv)"
          >
            <div class="conv-avatar">{{ getConversationName(conv).charAt(0) }}</div>
            <div class="conv-info">
              <span class="conv-name">{{ getConversationName(conv) }}</span>
              <span class="conv-preview">{{ conv.last_message || 'Sin mensajes' }}</span>
            </div>
          </div>
        </div>
      </aside>

      <main class="chat-area">
        <div v-if="!selectedConversation" class="no-selection">
          <div class="no-selection-icon"><AppIcon name="chat" :size="48" /></div>
          <h3>Selecciona una conversación</h3>
          <p>Elige una conversación de la lista para ver los mensajes</p>
        </div>

        <template v-else>
          <header class="chat-header">
            <div class="chat-user">
              <div class="user-avatar">{{ getConversationName(selectedConversation).charAt(0) }}</div>
              <span>{{ getConversationName(selectedConversation) }}</span>
            </div>
          </header>

          <div class="messages-container">
            <div v-if="messages.length === 0" class="no-messages">
              <p>No hay mensajes aún. Envía el primero!</p>
            </div>
            <div v-else v-for="msg in messages" :key="msg.id" :class="['message', { mine: msg.sender_id === auth.userId }]">
              <div class="message-bubble">{{ msg.content }}</div>
              <span class="message-time">{{ formatTime(msg.created_at) }}</span>
            </div>
          </div>

          <footer class="chat-input">
            <input 
              v-model="newMessage" 
              @keyup.enter="sendMessage"
              placeholder="Escribe un mensaje..."
              :disabled="sending"
            />
            <button @click="sendMessage" :disabled="sending || !newMessage.trim()">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </footer>
        </template>
      </main>
    </div>
  </div>
</template>

<style scoped>
.chat-page { display: flex; flex-direction: column; gap: 20px; }
.chat-container { display: grid; grid-template-columns: 320px 1fr; gap: 0; background: var(--color-card); border: 1px solid var(--color-line); border-radius: 16px; overflow: hidden; height: 600px; }

.conversations-list { border-right: 1px solid var(--color-line); padding: 20px; overflow-y: auto; }
.conversations-list h3 { font-size: 14px; color: var(--color-muted); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 16px; }
.conversation-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 10px; cursor: pointer; transition: .2s; }
.conversation-item:hover, .conversation-item.active { background: rgba(214, 168, 72, .1); }
.conv-avatar { width: 44px; height: 44px; border-radius: 50%; background: var(--color-gold); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; flex-shrink: 0; }
.conv-info { display: flex; flex-direction: column; overflow: hidden; }
.conv-name { font-weight: 600; color: var(--color-navy); }
.conv-preview { font-size: 13px; color: var(--color-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.chat-area { display: flex; flex-direction: column; }
.no-selection { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--color-muted); text-align: center; padding: 40px; }
.no-selection-icon { color: var(--color-gold); margin-bottom: 16px; }

.chat-header { padding: 16px 20px; border-bottom: 1px solid var(--color-line); }
.chat-user { display: flex; align-items: center; gap: 12px; font-weight: 600; color: var(--color-navy); }
.user-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--color-gold); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0; }

.messages-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.no-messages { text-align: center; color: var(--color-muted); padding: 40px; }

.message { display: flex; flex-direction: column; max-width: 70%; }
.message.mine { align-self: flex-end; }
.message-bubble { padding: 12px 16px; border-radius: 16px; font-size: 14px; line-height: 1.5; }
.message:not(.mine) .message-bubble { background: #f1f3f5; color: var(--color-navy); border-bottom-left-radius: 4px; }
.message.mine .message-bubble { background: var(--color-gold); color: white; border-bottom-right-radius: 4px; }
.message-time { font-size: 11px; color: var(--color-muted); margin-top: 4px; }
.message.mine .message-time { text-align: right; }

.chat-input { display: flex; gap: 12px; padding: 16px 20px; border-top: 1px solid var(--color-line); }
.chat-input input { flex: 1; padding: 12px 16px; border: 1px solid var(--color-line); border-radius: 24px; font-size: 14px; outline: none; transition: .2s; }
.chat-input input:focus { border-color: var(--color-gold); }
.chat-input button { width: 44px; height: 44px; border-radius: 50%; background: var(--color-gold); color: white; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: .2s; }
.chat-input button:hover:not(:disabled) { background: #c9973d; }
.chat-input button:disabled { opacity: 0.5; cursor: not-allowed; }

.loading, .empty { padding: 20px; text-align: center; color: var(--color-muted); }

@media (max-width: 768px) {
  .chat-container { grid-template-columns: 1fr; }
  .conversations-list { display: none; }
}
</style>
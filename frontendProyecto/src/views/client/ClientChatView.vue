<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { usePropertyStore } from '@/stores/propertyStore'
import { storeToRefs } from 'pinia'
import ClientDashboardHeader from '@/components/client/dashboard/ClientDashboardHeader.vue'
import AppIcon from '@/components/shared/AppIcon.vue'
import Breadcrumb from '@/components/shared/Breadcrumb.vue'

const auth = useAuthStore()
const propertyStore = usePropertyStore()
const { properties } = storeToRefs(propertyStore)

const conversations = ref([])
const messages = ref([])
const selectedConversation = ref(null)
const newMessage = ref('')
const loading = ref(true)
const sending = ref(false)
const polling = ref(null)
const showConversations = ref(true)

const advisorProperties = computed(() => {
  return properties.value.filter(p => p.owner_id === auth.userId && p.advisor_id)
})

const fetchConversations = async () => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/messages/conversations?user_id=${auth.userId}`, {
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
  showConversations.value = false
  fetchMessages(conv.id)
  startPolling()
}

const backToConversations = () => {
  showConversations.value = true
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

const resolveDisplayName = (person, fallback = 'Usuario') => {
  if (!person) return fallback
  return (
    person.full_name ||
    person.name ||
    person.display_name ||
    person.username ||
    person.email ||
    fallback
  )
}

const getConversationName = (conv) => {
  return (
    resolveDisplayName(conv.advisor, '') ||
    conv.advisor_name ||
    conv.other_user_name ||
    conv.participant_name ||
    'Asesor'
  )
}

const messageSenderName = (msg) => {
  if (msg.sender_id === auth.userId) return 'Tú'
  return (
    resolveDisplayName(msg.sender, '') ||
    msg.sender_name ||
    getConversationName(selectedConversation.value || {})
  )
}

onMounted(async () => {
  await propertyStore.fetchProperties()
  await fetchConversations()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <div class="chat-page">
    <ClientDashboardHeader eyebrow="Panel de Cliente" title="Mensajes" />

    <div class="chat-container">
      <aside class="conversations-list" :class="{ 'mobile-show': showConversations }">
        <h3>Conversaciones</h3>
        
        <div v-if="loading" class="loading fancy-loading">
          <div class="skeleton-row" v-for="n in 3" :key="n">
            <span class="sk-avatar"></span>
            <span class="sk-lines">
              <i></i>
              <i></i>
            </span>
          </div>
        </div>
        
        <div v-else-if="conversations.length === 0" class="empty fancy-empty">
          <div class="empty-icon-wrap"><AppIcon name="chat" :size="28" /></div>
          <h4>Aún no tienes conversaciones</h4>
          <p>Cuando contactes a un asesor desde una propiedad, tus mensajes aparecerán aquí.</p>
          <RouterLink to="/propiedades" class="empty-action">Explorar propiedades</RouterLink>
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

      <main class="chat-area" :class="{ 'mobile-hide': !showConversations && !selectedConversation }">
        <div v-if="!selectedConversation" class="no-selection">
          <div class="no-selection-icon"><AppIcon name="chat" :size="48" /></div>
          <h3>Selecciona una conversación</h3>
          <p>Elige una conversación de la lista para ver los mensajes</p>
        </div>

        <template v-else>
          <header class="chat-header">
            <div class="chat-user">
              <button class="back-btn" @click="backToConversations" title="Volver a conversaciones">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
              </button>
              <div class="user-avatar">{{ getConversationName(selectedConversation).charAt(0) }}</div>
              <span>{{ getConversationName(selectedConversation) }}</span>
            </div>
          </header>

          <div class="messages-container">
            <div v-if="messages.length === 0" class="no-messages">
              <p>No hay mensajes aún. Envía el primero!</p>
            </div>
            <div v-else v-for="msg in messages" :key="msg.id" :class="['message', { mine: msg.sender_id === auth.userId }]">
              <span class="sender-name">{{ messageSenderName(msg) }}</span>
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
.chat-container { display: grid; grid-template-columns: minmax(280px, 320px) 1fr; gap: 0; background: var(--color-card); border: 1px solid var(--color-line); border-radius: 16px; overflow: hidden; height: 600px; }

.conversations-list { border-right: 1px solid var(--color-line); padding: 20px; overflow-y: auto; }
.conversations-list h3 { font-size: 14px; color: var(--color-muted); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 16px; }
.conversation-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 12px; cursor: pointer; border: 1px solid transparent; transition: .22s ease; }
.conversation-item:hover { background: rgba(7, 24, 44, 0.05); border-color: rgba(7, 24, 44, 0.08); transform: translateY(-1px); }
.conversation-item.active { background: linear-gradient(120deg, rgba(7, 24, 44, 0.95), rgba(16, 46, 79, 0.92)); border-color: rgba(214, 168, 72, 0.35); box-shadow: 0 10px 20px rgba(7, 24, 44, 0.22); }
.conv-avatar { width: 44px; height: 44px; border-radius: 50%; background: var(--color-gold); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; flex-shrink: 0; }
.conv-info { display: flex; flex-direction: column; overflow: hidden; }
.conv-name { font-weight: 600; color: var(--color-navy); }
.conv-preview { font-size: 13px; color: var(--color-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.conversation-item.active .conv-name { color: #fff; }
.conversation-item.active .conv-preview { color: rgba(255, 255, 255, 0.78); }

.chat-area { display: flex; flex-direction: column; }
.no-selection { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--color-muted); text-align: center; padding: 40px; }
.no-selection-icon { color: var(--color-gold); margin-bottom: 16px; }

.chat-header { padding: 16px 20px; border-bottom: 1px solid var(--color-line); }
.chat-user { display: flex; align-items: center; gap: 12px; font-weight: 600; color: var(--color-navy); }
.user-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--color-gold); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; }
.back-btn { width: 32px; height: 32px; border-radius: 50%; border: none; background: rgba(7, 24, 44, 0.08); color: var(--color-navy); cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background:
    radial-gradient(circle at 15% 5%, rgba(214, 168, 72, 0.06), transparent 28%),
    radial-gradient(circle at 90% 100%, rgba(7, 24, 44, 0.06), transparent 30%),
    #f8fafc;
}
.no-messages { text-align: center; color: var(--color-muted); padding: 40px; }

.message { display: flex; flex-direction: column; max-width: 74%; animation: msgIn .2s ease both; }
.message.mine { align-self: flex-end; }
.sender-name { font-size: 11px; font-weight: 700; color: #60758f; margin: 0 4px 4px; }
.message.mine .sender-name { color: #91671f; text-align: right; }
.message-bubble { padding: 12px 16px; border-radius: 18px; font-size: 14px; line-height: 1.5; border: 1px solid transparent; box-shadow: 0 6px 14px rgba(15, 23, 42, 0.08); transition: transform .2s ease, box-shadow .2s ease; }
.message-bubble:hover { transform: translateY(-1px); box-shadow: 0 10px 18px rgba(15, 23, 42, 0.12); }
.message:not(.mine) .message-bubble { background: #ffffff; color: var(--color-navy); border-color: #e6edf6; border-bottom-left-radius: 6px; }
.message.mine .message-bubble { background: linear-gradient(120deg, #d8a54d, #c9973d); color: #fff; border-bottom-right-radius: 6px; }
.message-time { font-size: 11px; color: var(--color-muted); margin-top: 4px; }
.message.mine .message-time { text-align: right; }

.chat-input { display: flex; gap: 12px; padding: 16px 20px; border-top: 1px solid var(--color-line); }
.chat-input input { flex: 1; padding: 12px 16px; border: 1px solid var(--color-line); border-radius: 24px; font-size: 14px; outline: none; transition: .2s; background: #fff; }
.chat-input input:focus { border-color: #d8a54d; box-shadow: 0 0 0 3px rgba(216, 165, 77, 0.15); }
.chat-input button { width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(120deg, #07182c, #0f355f); color: white; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: .2s; box-shadow: 0 10px 16px rgba(7, 24, 44, 0.25); }
.chat-input button:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 14px 20px rgba(7, 24, 44, 0.32); }
.chat-input button:disabled { opacity: 0.5; cursor: not-allowed; }

.loading, .empty { padding: 20px; text-align: center; color: var(--color-muted); }
.fancy-loading { display: grid; gap: 12px; padding: 10px 4px; text-align: left; }
.skeleton-row { display: flex; align-items: center; gap: 10px; padding: 10px; border: 1px solid #e8edf4; border-radius: 12px; background: #fff; }
.sk-avatar { width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(90deg, #eef2f8, #f7f9fc, #eef2f8); background-size: 200% 100%; animation: shimmer 1.2s infinite; }
.sk-lines { flex: 1; display: grid; gap: 6px; }
.sk-lines i { height: 10px; border-radius: 999px; background: linear-gradient(90deg, #eef2f8, #f7f9fc, #eef2f8); background-size: 200% 100%; animation: shimmer 1.2s infinite; }
.sk-lines i:first-child { width: 72%; }
.sk-lines i:last-child { width: 48%; }
.fancy-empty { min-height: 210px; display: grid; place-items: center; gap: 8px; background: #f9fbff; border: 1px dashed #d8e2ef; border-radius: 14px; padding: 22px 14px; }
.empty-icon-wrap { width: 54px; height: 54px; border-radius: 14px; display: grid; place-items: center; color: #d8a54d; background: rgba(216, 165, 77, 0.12); }
.fancy-empty h4 { margin: 0; color: #102c4f; font-size: 16px; }
.fancy-empty p { margin: 0; font-size: 13px; max-width: 240px; color: #62778f; }
.empty-action { margin-top: 4px; min-height: 36px; padding: 0 14px; border-radius: 999px; background: #07182c; color: #fff; display: inline-flex; align-items: center; font-size: 12px; font-weight: 700; }

@keyframes msgIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (max-width: 900px) {
  .chat-container { height: 500px; }
}
@media (max-width: 768px) {
  .chat-container { grid-template-columns: 1fr; height: calc(100vh - 180px); min-height: 400px; }
  .conversations-list { display: none; }
  .conversations-list.mobile-show { display: block; }
  .chat-area { border-radius: 16px; }
  .back-btn { display: flex; }
  .message { max-width: 88%; }
  .message-bubble { padding: 10px 14px; font-size: 13px; }
  .chat-input { padding: 12px 16px; }
  .chat-input input { padding: 10px 14px; font-size: 13px; }
}
@media (min-width: 769px) {
  .back-btn { display: none; }
}
@media (max-width: 480px) {
  .messages-container { padding: 12px; }
  .chat-header { padding: 12px 16px; }
}
</style>

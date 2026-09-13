<script setup>
import { ref, computed } from 'vue'
import DashboardHeader from '@/components/shared/dashboard/DashboardHeader.vue'
import AppIcon from '@/components/shared/AppIcon.vue'
import ConversationItem from '@/components/shared/ConversationItem.vue'
import ChatBubble from '@/components/shared/ChatBubble.vue'
import TypingIndicator from '@/components/shared/TypingIndicator.vue'
import Breadcrumb from '@/components/shared/Breadcrumb.vue'
import { useChat } from '@/composables/useChat'
import { useAuthStore } from '@/stores/authStore'

const props = defineProps({
  role: {
    type: String,
    required: true,
    validator: (v) => ['client', 'advisor'].includes(v)
  },
  eyebrow: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: 'Mensajes'
  },
  showSearch: {
    type: Boolean,
    default: false
  },
  showFilters: {
    type: Boolean,
    default: false
  }
})

const roleName = props.role === 'advisor' ? 'advisor' : 'client'
const auth = useAuthStore()

const {
  conversations,
  messages,
  selectedConversation,
  newMessage,
  loading,
  sending,
  sendError,
  showConversations,
  messagesContainer,
  isOtherTyping,
  wsConnected,
  groupedMessages,
  filteredConversations,
  totalUnread,
  searchQuery,
  filterType,
  messageSenderName,
  getConversationName,
  fetchConversations,
  fetchMessages,
  selectConversation,
  backToConversations,
  sendMessage,
  handleTyping,
  scrollToBottom,
  playNotificationSound
} = useChat({ role: props.role, roleName, autoConnect: true })

const crumbs = computed(() => [
  { label: props.title, path: props.role === 'advisor' ? '/advisor/mensajes' : '/cliente/mensajes' }
])

const displayedConversations = computed(() => {
  return searchQuery.value || filterType.value !== 'all'
    ? filteredConversations.value
    : conversations.value
})
</script>

<template>
  <div class="chat-page">
    <DashboardHeader :eyebrow="eyebrow" :title="title" />
    <Breadcrumb :crumbs="crumbs" />

    <div class="chat-container">
      <aside class="conversations-list" :class="{ 'mobile-show': showConversations }">
        <div class="sidebar-header">
          <h2>Conversaciones</h2>
          <span v-if="totalUnread > 0" class="total-unread" aria-label="Total mensajes sin leer">{{ totalUnread }}</span>
        </div>

        <div class="search-bar" v-if="showSearch">
          <input
            v-model="searchQuery"
            placeholder="Buscar cliente..."
            aria-label="Buscar conversaciones"
          />
        </div>

        <div class="filter-tabs" v-if="showFilters">
          <button
            :class="['filter-tab', { active: filterType === 'all' }]"
            @click="filterType = 'all'"
            aria-label="Mostrar todas las conversaciones"
          >Todas</button>
          <button
            :class="['filter-tab', { active: filterType === 'unread' }]"
            @click="filterType = 'unread'"
            aria-label="Mostrar solo conversaciones sin leer"
          >Sin leer</button>
        </div>

        <div v-if="loading" class="loading fancy-loading">
          <div class="skeleton-row" v-for="n in 3" :key="n">
            <span class="sk-avatar"></span>
            <span class="sk-lines">
              <i></i>
              <i></i>
            </span>
          </div>
        </div>

        <div v-else-if="displayedConversations.length === 0" class="empty fancy-empty">
          <div class="empty-icon-wrap"><AppIcon name="chat" :size="28" /></div>
          <h4>Aún no tienes conversaciones</h4>
          <p v-if="props.role === 'advisor'">Cuando un cliente te contacte desde una propiedad, sus mensajes aparecerán aquí.</p>
          <p v-else>Cuando contactes a un asesor desde una propiedad, tus mensajes aparecerán aquí.</p>
          <RouterLink :to="props.role === 'advisor' ? '/advisor/propiedades' : '/propiedades'" class="empty-action">
            Explorar propiedades
          </RouterLink>
        </div>

        <div v-else>
          <ConversationItem
            v-for="conv in displayedConversations"
            :key="conv.id"
            :conversation="conv"
            :is-active="selectedConversation?.id === conv.id"
            @select="selectConversation"
          />
        </div>
      </aside>

      <div class="chat-area" :class="{ 'mobile-hide': !showConversations && !selectedConversation }">
        <div v-if="!selectedConversation" class="no-selection">
          <div class="no-selection-icon"><AppIcon name="chat" :size="48" /></div>
          <h2>Selecciona una conversación</h2>
          <p>Elige una conversación de la lista para ver los mensajes</p>
        </div>

        <template v-else>
          <header class="chat-header">
            <div class="chat-user">
              <button class="back-btn" @click="backToConversations" title="Volver a conversaciones" aria-label="Volver a la lista de conversaciones">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
              </button>
              <div class="user-avatar" aria-hidden="true">{{ getConversationName(selectedConversation).charAt(0) }}</div>
              <span>{{ getConversationName(selectedConversation) }}</span>
              <span v-if="wsConnected" class="online-dot" title="Conectado" aria-label="Conectado"></span>
            </div>
          </header>

          <div ref="messagesContainer" class="messages-container" role="log" aria-label="Mensajes de la conversación" aria-live="polite">
            <div v-if="messages.length === 0" class="no-messages">
              <p>No hay mensajes aún. ¡Envía el primero!</p>
            </div>

            <template v-else>
              <div v-for="group in groupedMessages" :key="group.label" class="message-group">
                <div class="date-divider"><span>{{ group.label }}</span></div>
                <ChatBubble
                  v-for="msg in group.messages"
                  :key="msg.id"
                  :message="msg"
                  :is-mine="msg.sender_id === auth.userId"
                  :sender-name="messageSenderName(msg)"
                  :show-status="true"
                />
              </div>
            </template>

            <TypingIndicator
              :user-name="getConversationName(selectedConversation)"
              :is-visible="isOtherTyping"
            />
          </div>

          <footer class="chat-input">
            <input
              v-model="newMessage"
              @keyup.enter="sendMessage"
              @input="handleTyping"
              placeholder="Escribe un mensaje..."
              :disabled="sending"
              aria-label="Escribe un mensaje"
            />
            <button @click="sendMessage" :disabled="sending || !newMessage.trim()" aria-label="Enviar mensaje">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </footer>

          <div v-if="sendError" class="send-error" role="alert">
            <span>Error al enviar. Intenta de nuevo.</span>
            <div class="send-error-actions">
              <button @click="sendMessage" aria-label="Reintentar envío">Reintentar</button>
              <button @click="sendError = false" aria-label="Cerrar error">x</button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-page { display: flex; flex-direction: column; gap: 20px; }
.chat-container { display: grid; grid-template-columns: minmax(280px, 320px) 1fr; gap: 0; background: #fff; border: 1px solid var(--color-line); border-radius: 12px; overflow: hidden; min-height: 600px; height: calc(100vh - 200px); }

.conversations-list { border-right: 1px solid var(--color-line); padding: 20px; overflow-y: auto; }
.sidebar-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.conversations-list h2 { font-size: 11px; font-weight: 800; color: var(--color-muted); text-transform: uppercase; letter-spacing: .14em; margin: 0; }
.total-unread { background: var(--color-brass); color: var(--color-petrol); font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 999px; }

/* JAKEDA: align chat atoms (contracts intact, styles only) */
.chat-page :deep(.conversation-item:hover) { background: rgba(16, 45, 45, 0.05); border-color: var(--color-line); transform: none; }
.chat-page :deep(.conversation-item.active) { background: var(--color-petrol); border-color: rgba(201, 164, 92, 0.45); box-shadow: none; }
.chat-page :deep(.conv-avatar) { background: var(--color-brass); color: var(--color-petrol); font-family: var(--serif); }
.chat-page :deep(.unread-badge) { background: var(--color-brass); color: var(--color-petrol); }
.chat-page :deep(.message-bubble) { box-shadow: none; }
.chat-page :deep(.message-bubble:hover) { transform: none; box-shadow: none; }
.chat-page :deep(.message-bubble-wrapper:not(.mine) .message-bubble) { border-color: var(--color-line); }
.chat-page :deep(.message-bubble-wrapper.mine .message-bubble) { background: var(--color-petrol); color: var(--color-ivory-2); }
.chat-page :deep(.sender-name-mine),
.chat-page :deep(.message-status) { color: var(--color-brass-ink); }

.search-bar { margin-bottom: 12px; }
.search-bar input { width: 100%; min-height: 44px; padding: 10px 12px; border: 1px solid var(--color-line); border-radius: 8px; font-size: 13px; outline: none; background: #fff; transition: border-color .2s ease; }
.search-bar input:focus { border-color: var(--color-brass); box-shadow: 0 0 0 3px rgba(201, 164, 92, 0.15); }

.filter-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.filter-tab { min-height: 44px; display: inline-flex; align-items: center; justify-content: center; padding: 6px 16px; border-radius: 999px; border: 1px solid var(--color-line); background: transparent; font-size: 12px; font-weight: 600; color: var(--color-muted); cursor: pointer; transition: border-color .2s ease, color .2s ease; }
.filter-tab.active { background: var(--color-petrol); border-color: var(--color-petrol); color: var(--color-ivory); }
.filter-tab:hover:not(.active) { border-color: var(--color-brass); color: var(--color-petrol); }

.chat-area { display: flex; flex-direction: column; min-width: 0; }
.no-selection { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--color-muted); text-align: center; padding: 40px; }
.no-selection-icon { color: var(--color-brass); margin-bottom: 16px; }

.chat-header { padding: 16px 20px; border-bottom: 1px solid var(--color-line); }
.chat-user { display: flex; align-items: center; gap: 12px; font-weight: 600; color: var(--color-petrol); }
.user-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--color-brass); color: var(--color-petrol); display: flex; align-items: center; justify-content: center; font-weight: 700; font-family: var(--serif); }
.back-btn { width: 44px; height: 44px; min-width: 44px; min-height: 44px; border-radius: 50%; border: none; background: rgba(16, 45, 45, 0.07); color: var(--color-petrol); cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.online-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-success); flex-shrink: 0; }

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  background: var(--color-ivory);
}
.no-messages { text-align: center; color: var(--color-muted); padding: 40px; }

.message-group { display: flex; flex-direction: column; }
.date-divider { display: flex; align-items: center; justify-content: center; margin: 16px 0 12px; }
.date-divider span { font-size: 11px; color: var(--color-muted); background: #fff; padding: 4px 12px; border-radius: 12px; border: 1px solid var(--color-line); text-transform: capitalize; }

.chat-input { display: flex; gap: 12px; padding: 16px 20px; border-top: 1px solid var(--color-line); background: #fff; }
.chat-input input { flex: 1; min-height: 44px; padding: 12px 16px; border: 1px solid var(--color-line); border-radius: 24px; font-size: 14px; outline: none; transition: border-color .2s ease; background: #fff; }
.chat-input input:focus { border-color: var(--color-brass); box-shadow: 0 0 0 3px rgba(201, 164, 92, 0.15); }
.chat-input button { width: 44px; height: 44px; border-radius: 50%; background: var(--color-petrol); color: var(--color-ivory-2); border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background .2s ease; box-shadow: none; }
.chat-input button:hover:not(:disabled) { background: var(--color-petrol); }
.chat-input button:disabled { opacity: 0.5; cursor: not-allowed; }

.send-error { display: flex; align-items: center; justify-content: space-between; padding: 8px 16px; background: var(--color-danger-soft); border-top: 1px solid var(--color-danger-soft); color: var(--color-danger); font-size: 12px; }
.send-error button { background: none; border: none; color: var(--color-danger); cursor: pointer; font-weight: 700; font-size: 14px; padding: 10px 12px; min-height: 44px; }
.send-error-actions { display: flex; align-items: center; gap: 12px; }

.loading, .empty { padding: 20px; text-align: center; color: var(--color-muted); }
.fancy-loading { display: grid; gap: 12px; padding: 10px 4px; text-align: left; }
.skeleton-row { display: flex; align-items: center; gap: 10px; padding: 10px; border: 1px solid var(--color-line); border-radius: 12px; background: #fff; }
.sk-avatar { width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(90deg, var(--color-ivory-2), var(--color-ivory), var(--color-ivory-2)); background-size: 200% 100%; animation: shimmer 1.2s infinite; }
.sk-lines { flex: 1; display: grid; gap: 6px; }
.sk-lines i { height: 10px; border-radius: 999px; background: linear-gradient(90deg, var(--color-ivory-2), var(--color-ivory), var(--color-ivory-2)); background-size: 200% 100%; animation: shimmer 1.2s infinite; }
.sk-lines i:first-child { width: 72%; }
.sk-lines i:last-child { width: 48%; }
.fancy-empty { min-height: 210px; display: grid; place-items: center; gap: 8px; background: var(--color-ivory-2); border: 1px dashed var(--color-line); border-radius: 12px; padding: 22px 14px; }
.empty-icon-wrap { width: 54px; height: 54px; border-radius: 12px; display: grid; place-items: center; color: var(--color-brass-ink); background: rgba(201, 164, 92, 0.16); }
.fancy-empty h4 { margin: 0; color: var(--color-petrol); font-size: 17px; font-family: var(--serif); }
.fancy-empty p { margin: 0; font-size: 13px; max-width: 240px; color: var(--color-muted); }
.empty-action { margin-top: 4px; min-height: 44px; padding: 0 16px; border-radius: 8px; background: var(--color-petrol); color: var(--color-ivory-2); display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; text-decoration: none; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (max-width: 900px) {
  .chat-container { min-height: 500px; }
}
@media (max-width: 768px) {
  .chat-container { grid-template-columns: 1fr; height: calc(100vh - 180px); min-height: 400px; }
  .conversations-list { display: none; }
  .conversations-list.mobile-show { display: block; }
  .chat-area { border-radius: 12px; }
  .back-btn { display: flex; }
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

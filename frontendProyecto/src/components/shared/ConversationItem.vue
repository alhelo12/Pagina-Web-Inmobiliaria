<script setup>
import { computed } from 'vue'
import { formatRelativeTime } from '@/utils/chatUtils'

const props = defineProps({
  conversation: { type: Object, required: true },
  isActive: { type: Boolean, default: false },
  showPropertyContext: { type: Boolean, default: false },
})

const emit = defineEmits(['select'])

const displayName = computed(() => {
  const conv = props.conversation
  return conv.user_name || conv.advisor_name || conv.other_user_name || conv.participant_name || 'Usuario'
})

const initial = computed(() => displayName.value.charAt(0).toUpperCase())

const relativeTime = computed(() => formatRelativeTime(props.conversation.last_message_at || props.conversation.created_at))

const preview = computed(() => props.conversation.last_message || 'Sin mensajes')

const propertyInfo = computed(() => {
  if (!props.showPropertyContext || !props.conversation.property) return null
  const p = props.conversation.property
  return { title: p.title, city: p.city }
})
</script>

<template>
  <div
    :class="['conversation-item', { active: isActive }]"
    @click="emit('select', conversation)"
    role="button"
    :aria-label="`Conversacion con ${displayName}${conversation.unread_count ? `, ${conversation.unread_count} mensajes sin leer` : ''}`"
    tabindex="0"
    @keydown.enter="emit('select', conversation)"
  >
    <div class="conv-avatar" :aria-hidden="true">{{ initial }}</div>
    <div class="conv-info">
      <div class="conv-top-row">
        <span class="conv-name">{{ displayName }}</span>
        <span class="conv-time">{{ relativeTime }}</span>
      </div>
      <div class="conv-bottom-row">
        <span class="conv-preview">{{ preview }}</span>
        <span v-if="conversation.unread_count > 0" class="unread-badge" aria-label="Mensajes sin leer">
          {{ conversation.unread_count > 9 ? '+9' : conversation.unread_count }}
        </span>
      </div>
      <div v-if="propertyInfo" class="conv-property">
        <span class="property-icon">🏠</span>
        <span class="property-title">{{ propertyInfo.title }}</span>
        <span v-if="propertyInfo.city" class="property-city">— {{ propertyInfo.city }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.conversation-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 12px; cursor: pointer; border: 1px solid transparent; transition: .22s ease; }
.conversation-item:hover { background: rgba(7, 24, 44, 0.05); border-color: rgba(7, 24, 44, 0.08); transform: translateY(-1px); }
.conversation-item.active { background: linear-gradient(120deg, rgba(7, 24, 44, 0.95), rgba(16, 46, 79, 0.92)); border-color: rgba(214, 168, 72, 0.35); box-shadow: 0 10px 20px rgba(7, 24, 44, 0.22); }
.conv-avatar { width: 44px; height: 44px; border-radius: 50%; background: var(--color-gold); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; flex-shrink: 0; }
.conv-info { display: flex; flex-direction: column; overflow: hidden; flex: 1; min-width: 0; }
.conv-top-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.conv-name { font-weight: 600; color: var(--color-navy); font-size: 14px; }
.conv-time { font-size: 11px; color: var(--color-muted); flex-shrink: 0; }
.conv-bottom-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 2px; }
.conv-preview { font-size: 13px; color: var(--color-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; }
.unread-badge { background: var(--color-gold); color: white; font-size: 11px; font-weight: 700; min-width: 20px; height: 20px; border-radius: 10px; display: flex; align-items: center; justify-content: center; padding: 0 6px; flex-shrink: 0; }
.conv-property { display: flex; align-items: center; gap: 4px; margin-top: 4px; font-size: 11px; color: var(--color-muted); }
.property-icon { font-size: 10px; }
.property-title { font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.property-city { white-space: nowrap; }
.conversation-item.active .conv-name { color: #fff; }
.conversation-item.active .conv-preview { color: rgba(255, 255, 255, 0.78); }
.conversation-item.active .conv-time { color: rgba(255, 255, 255, 0.6); }
.conversation-item.active .conv-property { color: rgba(255, 255, 255, 0.5); }
</style>

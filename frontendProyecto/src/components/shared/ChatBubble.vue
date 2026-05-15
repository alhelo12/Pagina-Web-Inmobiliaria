<script setup>
import { computed } from 'vue'
import { formatMessageTime } from '@/utils/chatUtils'

const props = defineProps({
  message: { type: Object, required: true },
  isMine: { type: Boolean, default: false },
  showSender: { type: Boolean, default: true },
  showStatus: { type: Boolean, default: false },
  senderName: { type: String, default: '' },
})

const time = computed(() => formatMessageTime(props.message.created_at))
</script>

<template>
  <div :class="['message-bubble-wrapper', { mine: isMine }]" role="listitem">
    <span v-if="showSender && !isMine" class="sender-name">{{ senderName }}</span>
    <span v-if="showSender && isMine" class="sender-name sender-name-mine">{{ senderName }}</span>
    <div class="message-bubble">
      <span class="message-content">{{ message.content }}</span>
    </div>
    <div :class="['message-meta', { 'meta-mine': isMine }]">
      <span class="message-time">{{ time }}</span>
      <span v-if="showStatus && isMine" class="message-status">
        {{ message.is_read ? '✓✓' : '✓' }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.message-bubble-wrapper { display: flex; flex-direction: column; max-width: 74%; animation: msgIn .2s ease both; }
.message-bubble-wrapper.mine { align-self: flex-end; }
.sender-name { font-size: 11px; font-weight: 700; color: #60758f; margin: 0 4px 4px; }
.sender-name-mine { color: #91671f; text-align: right; }
.message-bubble { padding: 12px 16px; border-radius: 18px; font-size: 14px; line-height: 1.5; border: 1px solid transparent; box-shadow: 0 6px 14px rgba(15, 23, 42, 0.08); transition: transform .2s ease, box-shadow .2s ease; }
.message-bubble:hover { transform: translateY(-1px); box-shadow: 0 10px 18px rgba(15, 23, 42, 0.12); }
.message-bubble-wrapper:not(.mine) .message-bubble { background: #ffffff; color: var(--color-navy); border-color: #e6edf6; border-bottom-left-radius: 6px; }
.message-bubble-wrapper.mine .message-bubble { background: linear-gradient(120deg, #d8a54d, #c9973d); color: #fff; border-bottom-right-radius: 6px; }
.message-meta { display: flex; align-items: center; gap: 6px; margin-top: 4px; }
.message-meta.meta-mine { justify-content: flex-end; }
.message-time { font-size: 11px; color: var(--color-muted); }
.message-status { font-size: 11px; color: #91671f; font-weight: 700; }
.message-content { word-break: break-word; white-space: pre-wrap; }

@keyframes msgIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

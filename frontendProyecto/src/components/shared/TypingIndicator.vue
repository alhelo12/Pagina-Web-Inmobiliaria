<script setup>
defineProps({
  userName: { type: String, default: '' },
  isVisible: { type: Boolean, default: false },
})
</script>

<template>
  <Transition name="typing">
    <div v-if="isVisible" class="typing-indicator" role="status" aria-live="polite">
      <span class="typing-name">{{ userName }}</span>
      <span class="typing-text">esta escribiendo</span>
      <div class="typing-dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.typing-indicator { display: flex; align-items: center; gap: 6px; padding: 8px 16px; font-size: 12px; color: var(--color-muted); }
.typing-name { font-weight: 600; color: var(--color-navy); }
.typing-dots { display: flex; gap: 3px; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: var(--color-muted); animation: typingBounce 1.4s infinite ease-in-out; }
.dot:nth-child(1) { animation-delay: 0s; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.typing-enter-active,
.typing-leave-active { transition: opacity 0.2s ease; }
.typing-enter-from,
.typing-leave-to { opacity: 0; }
</style>

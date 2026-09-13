<script setup>
import { useToast } from '@/composables/useToast'
import AppIcon from '@/components/shared/AppIcon.vue'

const { toasts, dismissToast } = useToast()
</script>

<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['toast', `toast-${toast.type}`, { visible: toast.visible }]"
          :role="toast.type === 'error' ? 'alert' : 'status'"
          @click="dismissToast(toast.id)"
        >
          <div class="toast-icon">
            <AppIcon v-if="toast.type === 'success'" name="check-circle" :size="18" />
            <AppIcon v-else-if="toast.type === 'error'" name="x-circle" :size="18" />
            <AppIcon v-else-if="toast.type === 'warning'" name="warning" :size="18" />
            <AppIcon v-else name="bell" :size="18" />
          </div>
          <div class="toast-content">
            <strong>{{ toast.title }}</strong>
            <p v-if="toast.message">{{ toast.message }}</p>
          </div>
          <button class="toast-close" aria-label="Cerrar notificación" @click.stop="dismissToast(toast.id)">
            <AppIcon name="x" :size="14" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 380px;
  pointer-events: none;
}

.toast {
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(7, 27, 28, 0.18);
  border: 1px solid var(--color-line);
  cursor: pointer;
  transition: box-shadow 0.3s ease;
}

.toast:hover {
  box-shadow: 0 16px 36px rgba(7, 27, 28, 0.24);
}

.toast-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.toast-info .toast-icon { color: var(--color-petrol); }
.toast-success .toast-icon { color: var(--color-success); }
.toast-error .toast-icon { color: var(--color-danger); }
.toast-warning .toast-icon { color: var(--color-brass-ink); }

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-content strong {
  display: block;
  color: var(--color-ink);
  font-size: 13px;
  font-weight: 700;
}

.toast-content p {
  margin: 2px 0 0;
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.4;
}

.toast-close {
  background: transparent;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 2px;
  flex-shrink: 0;
  transition: color 0.2s ease;
}

.toast-close:hover {
  color: var(--color-ink);
}

.toast-enter-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.toast-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(40px) scale(0.95);
}

@media (max-width: 480px) {
  .toast-container {
    left: 12px;
    right: 12px;
    max-width: none;
  }
}
</style>

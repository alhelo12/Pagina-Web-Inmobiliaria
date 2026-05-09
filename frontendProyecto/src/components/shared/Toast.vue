<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="visible" :class="['toast', type]">
        <span>{{ message }}</span>
        <button class="toast-close" @click="$emit('close')">&times;</button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  message: { type: String, default: '' },
  type: { type: String, default: 'success' }
})
defineEmits(['close'])
</script>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  padding: 14px 20px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 18px 45px rgba(7, 23, 45, 0.22);
  max-width: 380px;
}
.toast.success { background: #dff7e9; color: #166534; border: 1px solid #b7e4c7; }
.toast.error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
.toast.info { background: #eef4fb; color: #102e4f; border: 1px solid #d0dcec; }
.toast-close {
  background: none;
  border: none;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  opacity: .6;
  color: inherit;
  padding: 0 0 0 4px;
}
.toast-close:hover { opacity: 1; }
.toast-enter-active { transition: all .3s ease; }
.toast-leave-active { transition: all .25s ease; }
.toast-enter-from { opacity: 0; transform: translateX(40px); }
.toast-leave-to { opacity: 0; transform: translateX(40px); }
</style>

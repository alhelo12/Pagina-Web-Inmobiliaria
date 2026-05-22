import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

export function useToast() {
  const addToast = ({ title, message, type = 'info', duration = 4000 }) => {
    const id = ++nextId
    toasts.value.push({ id, title, message, type, visible: true })
    setTimeout(() => {
      const idx = toasts.value.findIndex(t => t.id === id)
      if (idx !== -1) {
        toasts.value[idx].visible = false
        setTimeout(() => {
          toasts.value = toasts.value.filter(t => t.id !== id)
        }, 300)
      }
    }, duration)
  }

  const dismissToast = (id) => {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx !== -1) {
      toasts.value[idx].visible = false
      setTimeout(() => {
        toasts.value = toasts.value.filter(t => t.id !== id)
      }, 300)
    }
  }

  return { toasts, addToast, dismissToast }
}

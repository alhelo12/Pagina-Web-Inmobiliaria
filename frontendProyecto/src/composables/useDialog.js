import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

const FOCUSABLE =
  'a[href], button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])'

export function useDialog(isOpen, onClose) {
  const dialogRef = ref(null)
  let lastFocused = null

  function onKeydown(event) {
    if (event.key === 'Escape') {
      event.stopPropagation()
      onClose?.()
      return
    }
    if (event.key !== 'Tab' || !dialogRef.value) return
    const nodes = [...dialogRef.value.querySelectorAll(FOCUSABLE)].filter(
      (el) => el.offsetParent !== null
    )
    if (!nodes.length) return
    const first = nodes[0]
    const last = nodes[nodes.length - 1]
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault()
      last.focus()
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault()
      first.focus()
    }
  }

  function activate() {
    lastFocused = document.activeElement
    document.addEventListener('keydown', onKeydown)
    nextTick(() => dialogRef.value?.querySelector(FOCUSABLE)?.focus())
  }

  function deactivate(restore = true) {
    document.removeEventListener('keydown', onKeydown)
    if (restore && lastFocused?.isConnected) lastFocused.focus()
    lastFocused = null
  }

  watch(isOpen, (open) => (open ? activate() : deactivate()), { immediate: true })
  onBeforeUnmount(() => deactivate(false))

  return { dialogRef }
}

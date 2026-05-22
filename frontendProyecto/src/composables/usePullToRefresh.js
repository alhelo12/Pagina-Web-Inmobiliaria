import { ref, onMounted, onUnmounted } from 'vue'

export function usePullToRefresh(onRefresh) {
  const pulling = ref(false)
  const pullDistance = ref(0)

  let startY = 0
  let currentY = 0
  let isPulling = false

  const MAX_PULL = 80
  const THRESHOLD = 60

  const handleTouchStart = (e) => {
    if (window.scrollY > 0) return
    startY = e.touches[0].clientY
    isPulling = true
  }

  const handleTouchMove = (e) => {
    if (!isPulling) return
    currentY = e.touches[0].clientY
    const diff = currentY - startY
    if (diff > 0) {
      pullDistance.value = Math.min(diff * 0.5, MAX_PULL)
      pulling.value = true
    }
  }

  const handleTouchEnd = async () => {
    if (!isPulling) return
    isPulling = false

    if (pullDistance.value >= THRESHOLD) {
      pullDistance.value = MAX_PULL
      await onRefresh()
    }

    pulling.value = false
    pullDistance.value = 0
  }

  onMounted(() => {
    document.addEventListener('touchstart', handleTouchStart, { passive: true })
    document.addEventListener('touchmove', handleTouchMove, { passive: true })
    document.addEventListener('touchend', handleTouchEnd)
  })

  onUnmounted(() => {
    document.removeEventListener('touchstart', handleTouchStart)
    document.removeEventListener('touchmove', handleTouchMove)
    document.removeEventListener('touchend', handleTouchEnd)
  })

  return { pulling, pullDistance }
}

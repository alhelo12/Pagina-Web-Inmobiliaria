export function formatRelativeTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now - date
  const diffMin = Math.floor(diffMs / 60000)
  const diffHr = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHr / 24)

  if (diffMin < 1) return 'Ahora'
  if (diffMin < 60) return `hace ${diffMin} min`
  if (diffHr < 24) return `hace ${diffHr}h`
  if (diffDay === 1) return 'Ayer'
  if (diffDay < 7) return `hace ${diffDay}d`
  return date.toLocaleDateString('es-MX', { day: 'numeric', month: 'short' })
}

export function formatMessageTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
}

export function formatDateGroup(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const msgDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())

  if (msgDate.getTime() === today.getTime()) return 'Hoy'
  if (msgDate.getTime() === yesterday.getTime()) return 'Ayer'
  return date.toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}

export function sanitizeMessage(content) {
  if (typeof content !== 'string') return ''
  return content
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
}

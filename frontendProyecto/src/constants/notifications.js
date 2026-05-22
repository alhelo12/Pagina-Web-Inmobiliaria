/**
 * Tipos de notificación unificados — fuente única de verdad.
 *
 * Cada entrada mapea un `type` del backend a su metadata visual.
 * Se usa desde NotificationBell, NotificationsView y AdvisorNotificationsView.
 */

export const NOTIFICATION_META = {
  advisor_assigned: {
    icon: 'user',
    color: '#d6a848',
    label: 'Asesor asignado',
    roles: ['client']
  },
  approved: {
    icon: 'check',
    color: '#22c55e',
    label: 'Aprobada',
    roles: ['client']
  },
  rejected: {
    icon: 'x-circle',
    color: '#dc2626',
    label: 'Rechazada',
    roles: ['client']
  },
  sold: {
    icon: 'home',
    color: '#7c3aed',
    label: 'Vendida / Rentada',
    roles: ['client']
  },
  property_updated: {
    icon: 'pencil',
    color: '#3b82f6',
    label: 'Actualizada',
    roles: ['client']
  },
  appointment_confirmed: {
    icon: 'calendar',
    color: '#22c55e',
    label: 'Cita confirmada',
    roles: ['client', 'advisor']
  },
  appointment_cancelled: {
    icon: 'x-circle',
    color: '#dc2626',
    label: 'Cita cancelada',
    roles: ['client', 'advisor']
  },
  appointment_reminder: {
    icon: 'calendar',
    color: '#f59e0b',
    label: 'Recordatorio',
    roles: ['client', 'advisor']
  },
  post_sale_survey: {
    icon: 'envelope',
    color: '#3b82f6',
    label: 'Encuesta',
    roles: ['client']
  },
  post_sale_checkin: {
    icon: 'envelope',
    color: '#8b5cf6',
    label: 'Seguimiento',
    roles: ['client']
  },
  message_received: {
    icon: 'chat',
    color: '#6366f1',
    label: 'Nuevo mensaje',
    roles: ['client', 'advisor']
  }
}

export const FALLBACK_META = {
  icon: 'megaphone',
  color: '#65717e',
  label: 'Notificación'
}

/**
 * @param {string} type - clave del tipo de notificación
 * @returns {{ icon: string, color: string, label: string }}
 */
export function getNotificationMeta(type) {
  return NOTIFICATION_META[type] || FALLBACK_META
}

/**
 * Filtros de tipo visibles para un rol dado.
 * @param {'client'|'advisor'} role
 * @returns {{ key: string, label: string, color: string }[]}
 */
export function getTypeFilters(role = 'client') {
  const filters = []
  for (const [key, meta] of Object.entries(NOTIFICATION_META)) {
    if (meta.roles.includes(role)) {
      filters.push({ key, label: meta.label, color: meta.color })
    }
  }
  return filters
}

/**
 * Agrupa notificaciones por período de tiempo.
 * @param {Array} notifications
 * @returns {Array<{ group: string, items: Array }>}
 */
export function groupByDate(notifications) {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today - 86400000)
  const weekAgo = new Date(today - 7 * 86400000)

  const groups = { today: [], yesterday: [], week: [], older: [] }

  for (const n of notifications) {
    const d = new Date(n.created_at)
    if (d >= today) {
      groups.today.push(n)
    } else if (d >= yesterday) {
      groups.yesterday.push(n)
    } else if (d >= weekAgo) {
      groups.week.push(n)
    } else {
      groups.older.push(n)
    }
  }

  return [
    { group: 'Hoy', items: groups.today },
    { group: 'Ayer', items: groups.yesterday },
    { group: 'Esta semana', items: groups.week },
    { group: 'Anteriores', items: groups.older }
  ].filter(g => g.items.length > 0)
}

/**
 * Formatea una fecha ISO a texto relativo.
 * @param {string} timestamp
 * @returns {string}
 */
export function formatRelativeTime(timestamp) {
  if (!timestamp) return ''
  const diff = Date.now() - new Date(timestamp).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'hace un momento'
  if (mins < 60) return `hace ${mins} min`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `hace ${hrs}h`
  const days = Math.floor(hrs / 24)
  if (days < 30) return `hace ${days}d`
  return new Date(timestamp).toLocaleDateString('es-MX', { day: '2-digit', month: 'short' })
}

/**
 * Formatea una fecha ISO a formato legible completo.
 * @param {string} timestamp
 * @returns {string}
 */
export function formatDate(timestamp) {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleDateString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
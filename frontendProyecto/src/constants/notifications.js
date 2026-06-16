/**
 * Tipos de notificación — cargados desde el backend vía GET /notifications/meta.
 * Cache de módulo para acceso síncrono desde componentes.
 */

import { notificationsApi } from '@/api/notifications'

let metaCache = {}
let metaPromise = null

export const FALLBACK_META = {
  icon: 'megaphone',
  color: '#65717e',
  label: 'Notificación'
}

export async function loadNotificationMeta() {
  if (metaPromise) return metaPromise
  metaPromise = (async () => {
    try {
      const { data } = await notificationsApi.getMeta()
      metaCache = data
    } catch { /* fallback se usa hasta que se cargue */ }
  })()
  return metaPromise
}

export function getNotificationMeta(type) {
  return metaCache[type] || FALLBACK_META
}

export function getTypeFilters(role = 'client') {
  return Object.entries(metaCache)
    .filter(([, m]) => m.roles?.includes(role))
    .map(([key, m]) => ({ key, label: m.label, color: m.color }))
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
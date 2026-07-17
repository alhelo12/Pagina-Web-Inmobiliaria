import apiClient from '@/api/axios'
import { shallowRef } from 'vue'

const DEFAULTS = {
  property_types: ['house', 'apartment', 'land', 'commercial'],
  transaction_types: ['sale', 'rent'],
  property_statuses: ['pending', 'approved', 'rejected', 'sold'],
  appointment_statuses: ['pending', 'confirmed', 'completed', 'cancelled'],
  appointment_types: ['viewing', 'inspection'],
  user_roles: ['admin', 'advisor', 'client'],
  followup_types: ['satisfaction_survey', 'check_in_call', 'referral_request', 'maintenance_reminder'],
  followup_statuses: ['pending', 'completed', 'skipped'],
}

const LABELS = {
  property_types: { house: 'Casa', apartment: 'Departamento', land: 'Terreno', commercial: 'Local comercial' },
  transaction_types: { sale: 'Venta', rent: 'Renta' },
  property_statuses: { pending: 'Pendiente', approved: 'Aprobado', rejected: 'Rechazado', sold: 'Vendido' },
  appointment_statuses: { pending: 'Pendiente', confirmed: 'Confirmada', completed: 'Completada', cancelled: 'Cancelada' },
  appointment_types: { viewing: 'Visita', inspection: 'Inspección' },
  user_roles: { admin: 'Administrador', advisor: 'Asesor', client: 'Cliente' },
  followup_types: { satisfaction_survey: 'Encuesta de satisfacción', check_in_call: 'Llamada de seguimiento', referral_request: 'Solicitar referencia', maintenance_reminder: 'Recordatorio de mantenimiento' },
  followup_statuses: { pending: 'Pendiente', completed: 'Completado', skipped: 'Saltado' },
}

const _values = shallowRef(null)

export async function loadEnums() {
  try {
    const { data } = await apiClient.get('/constants')
    _values.value = data
  } catch {
    _values.value = { ...DEFAULTS }
  }
}

function getValues(name) {
  return _values.value?.[name] ?? DEFAULTS[name] ?? []
}

export function enumValues(name) {
  return getValues(name)
}

export function enumLabel(name, value) {
  const labels = LABELS[name]
  return labels?.[value] ?? value
}

export function enumOptions(name) {
  return getValues(name).map(v => ({ value: v, label: enumLabel(name, v) }))
}

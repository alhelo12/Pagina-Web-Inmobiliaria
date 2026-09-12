/**
 * Limpia el estado en memoria de todos los stores de usuario.
 * Se invoca al cerrar sesión para no filtrar datos entre usuarios
 * en equipos compartidos.
 */
import { useAppointmentsStore } from '@/stores/appointmentsStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useMessagesStore } from '@/stores/messagesStore'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { usePropertyStore } from '@/stores/propertyStore'

export function resetUserStores() {
  useAppointmentsStore().clear()
  useFavoritesStore().clear()
  useMessagesStore().clear()
  useNotificationsStore().clear()
  usePropertyStore().clear()
}

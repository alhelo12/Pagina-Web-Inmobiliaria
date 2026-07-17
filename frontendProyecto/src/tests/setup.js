import { vi } from 'vitest'

// Mock de localStorage
const localStorageMock = {
  getItem: vi.fn((key) => {
    const store = localStorageMock.__store || {}
    return store[key] || null
  }),
  setItem: vi.fn((key, value) => {
    const store = localStorageMock.__store || {}
    store[key] = String(value)
    localStorageMock.__store = store
  }),
  removeItem: vi.fn((key) => {
    const store = localStorageMock.__store || {}
    delete store[key]
    localStorageMock.__store = store
  }),
  clear: vi.fn(() => {
    localStorageMock.__store = {}
  }),
}

Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

// Mock de window.location
Object.defineProperty(window, 'location', {
  value: { pathname: '/', href: 'http://localhost' },
  writable: true,
})

// Mock de router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
  }),
  useRoute: () => ({
    path: '/',
    params: {},
    query: {},
  }),
}))

vi.mock('@/stores/notificationsStore', () => ({
  useNotificationsStore: () => ({
    notifications: [],
    unreadCount: 0,
    fetchNotifications: vi.fn(),
    fetchUnreadCount: vi.fn(),
    markAsRead: vi.fn(),
    markAllAsRead: vi.fn(),
    deleteNotification: vi.fn(),
    addNotification: vi.fn(),
  }),
}))

vi.mock('@/stores/messagesStore', () => ({
  useMessagesStore: () => ({
    conversations: [],
    unreadCount: 0,
    fetchConversations: vi.fn(),
  }),
}))

vi.mock('@/stores/propertyStore', () => ({
  usePropertyStore: () => ({
    properties: [],
    total: 0,
    loading: false,
    error: null,
    fetch: vi.fn(),
  }),
}))

vi.mock('@/stores/favoritesStore', () => ({
  useFavoritesStore: () => ({
    favorites: [],
    fetch: vi.fn(),
    toggle: vi.fn(),
  }),
}))

vi.mock('@/stores/appointmentsStore', () => ({
  useAppointmentsStore: () => ({
    appointments: [],
    fetch: vi.fn(),
  }),
}))

console.log = vi.fn()
console.warn = vi.fn()
console.error = vi.fn()

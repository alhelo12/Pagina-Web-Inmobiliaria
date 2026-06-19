import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { registerSW } from 'virtual:pwa-register'
import { loadNotificationMeta } from '@/constants/notifications'
import { loadEnums } from '@/utils/enums'
import './style.css'

// Leaflet CSS required so map and controls render correctly
import 'leaflet/dist/leaflet.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Importar router DESPUÉS de instalar Pinia para evitar useStore() en guards antes de tiempo
import router from './router'
app.use(router)

import { useAuthStore } from '@/stores/authStore'
const auth = useAuthStore()
auth.loadSession()

// Carga metadata de tipos de notificación (cache módulo, fallback si falla)
loadNotificationMeta()
loadEnums()

app.mount('#app')

registerSW({ onRegisteredSW() { console.log('Service Worker registered') } })

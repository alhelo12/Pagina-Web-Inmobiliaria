import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/authStore'
import { registerSW } from 'virtual:pwa-register'

// CSS de Leaflet — obligatorio para que el mapa y sus controles se vean correctamente
import 'leaflet/dist/leaflet.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

const auth = useAuthStore()
auth.loadSession()

app.mount('#app')

registerSW({ onRegisteredSW() { console.log('Service Worker registered') } })

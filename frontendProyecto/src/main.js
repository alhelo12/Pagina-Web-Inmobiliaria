import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/authStore'
import { registerSW } from 'virtual:pwa-register'
import './style.css'

// Leaflet CSS required so map and controls render correctly
import 'leaflet/dist/leaflet.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

const auth = useAuthStore()
auth.loadSession()

app.mount('#app')

registerSW({ onRegisteredSW() { console.log('Service Worker registered') } })

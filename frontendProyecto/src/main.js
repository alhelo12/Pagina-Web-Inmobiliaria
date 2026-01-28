import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// ⬇️ AQUÍ se crea la app
const app = createApp(App)

// ⬇️ AQUÍ sí existe app.use()
app.use(router)

// ⬇️ Montaje final
app.mount('#app')

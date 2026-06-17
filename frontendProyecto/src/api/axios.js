import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

// â”€â”€ Request: agrega el token JWT si existe â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
apiClient.interceptors.request.use((config) => {
  try {
    const auth = useAuthStore()
    if (auth.backendToken || auth.backendToken) {
      config.headers.Authorization = `Bearer ${auth.backendToken || auth.backendToken}`
    }
  } catch (err) {
    console.error('[Axios Request Interceptor]', err)
  }
  return config
})

// â”€â”€ Response: maneja 401 SOLO fuera del login â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Si interceptamos el 401 del propio endpoint de login, la página se recarga
// antes de que el componente pueda mostrar el error al usuario.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginEndpoint = error.config?.url?.includes('/auth/login')
    const authRoutes = new Set([
      '/login',
      '/registro',
      '/verificado',
      '/recuperar-contrasena',
      '/nueva-contrasena'
    ])
    const currentPath = window.location.pathname

    if (error.response?.status === 401 && !isLoginEndpoint) {
      try {
        const auth = useAuthStore()

        // Evita bucles de recarga en pantallas públicas/auth y cuando no hay sesión activa.
        if (!auth.backendToken || authRoutes.has(currentPath)) {
          return Promise.reject(error)
        }
      } catch (err) {
        console.error('[Axios Response Interceptor]', err)
        return Promise.reject(error)
      }

      // En flujo Supabase puede haber endpoints legacy que respondan 401 con token válido.
      // No forzamos redirección global para evitar rebotes al login.
      return Promise.reject(error)
    }

    return Promise.reject(error)
  }
)

export default apiClient


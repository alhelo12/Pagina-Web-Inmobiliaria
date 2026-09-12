import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'
import router from '@/router'

const API_URL = import.meta.env.VITE_API_URL

// En producción la URL es obligatoria; el fallback solo sirve para desarrollo.
if (!API_URL && import.meta.env.PROD) {
  throw new Error('VITE_API_URL no está definida en el build de producción')
}

const apiClient = axios.create({
  baseURL: API_URL ?? 'http://localhost:8000',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

// Request: agrega el token JWT si existe
apiClient.interceptors.request.use((config) => {
  try {
    const auth = useAuthStore()
    if (auth.backendToken) {
      config.headers.Authorization = `Bearer ${auth.backendToken}`
    }
  } catch {
    // Pinia aún no lista (arranque); la petición sigue sin token
  }
  return config
})

// Response: maneja 401 invalidando la sesión y redirigiendo
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const isLoginEndpoint = error.config?.url?.includes('/auth/login')

    if (error.response?.status === 401 && !isLoginEndpoint) {
      try {
        const auth = useAuthStore()
        await auth.logout()
        if (router.currentRoute.value.path !== '/login') {
          router.push('/login')
        }
      } catch {
        // logout idempotente: ignorar fallos de Pinia/router
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient

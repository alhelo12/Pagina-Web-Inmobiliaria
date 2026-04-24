import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' }
})

// ── Request: agrega el token JWT si existe ──────────────────────────────────
apiClient.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// ── Response: maneja 401 SOLO fuera del login ────────────────────────────────
// Si interceptamos el 401 del propio endpoint de login, la página se recarga
// antes de que el componente pueda mostrar el error al usuario.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginEndpoint = error.config?.url?.includes('/auth/login')

    if (error.response?.status === 401 && !isLoginEndpoint) {
      const auth = useAuthStore()
      auth.logout()
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

export default apiClient

import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'
import router from '@/router'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
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
  } catch (err) {
    console.error('[Axios Request Interceptor]', err)
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
        if (auth.backendToken) {
          await auth.logout()
          router.push('/login')
        }
      } catch (err) {
        console.error('[Axios Response Interceptor]', err)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient


<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { authApi } from '@/api/auth'

const router = useRouter()
const auth   = useAuthStore()

const email    = ref('')
const password = ref('')
const loading  = ref(false)
const error    = ref('')

const roleRedirect = {
  admin:   '/admin/propiedades',
  advisor: '/advisor/panel',
  client:  '/'
}

const submit = async () => {
  error.value   = ''     // limpia el error anterior al intentar de nuevo
  loading.value = true
  try {
    const { data } = await authApi.login(email.value, password.value)
    auth.login(data.access_token)
    router.push(roleRedirect[auth.role] ?? '/')
  } catch (err) {
    if (err.response) {
      // El servidor respondió con un error (401, 403, etc.)
      error.value = err.response.data?.detail ?? 'Credenciales incorrectas'
    } else if (err.request) {
      // La petición salió pero no hubo respuesta — backend caído o CORS
      error.value = 'No se pudo conectar con el servidor. Verifica que el backend esté corriendo.'
    } else {
      error.value = 'Ocurrió un error inesperado. Intenta de nuevo.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h1>Iniciar sesión</h1>
      <p class="subtitle">
        Acceso para administradores, asesores y clientes registrados
      </p>

      <!-- ERROR — persiste hasta que el usuario intente de nuevo o lo cierre -->
      <div v-if="error" class="alert-error">
        <span>{{ error }}</span>
        <button class="close-error" @click="error = ''">✕</button>
      </div>

      <form @submit.prevent="submit">
        <div class="field">
          <label>Correo electrónico</label>
          <input
            v-model="email"
            type="email"
            placeholder="correo@ejemplo.com"
            autocomplete="email"
            required
          />
        </div>

        <div class="field">
          <label>Contraseña</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>

        <button class="login-btn" type="submit" :disabled="loading">
          {{ loading ? 'Ingresando...' : 'Ingresar' }}
        </button>
      </form>

      <div class="divider"></div>

      <p class="register-text">¿Quieres vender o rentar una propiedad?</p>

      <RouterLink to="/registro" class="register-btn">
        Crear cuenta y registrar propiedad
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: calc(100vh - 80px);
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f7f7f7;
  font-family: 'Poppins', sans-serif;
}

.login-card {
  background: white;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  border-radius: 12px;
  box-shadow: 0 15px 40px rgba(0,0,0,0.08);
}

.login-card h1 { font-size: 26px; font-weight: 600; margin-bottom: 6px; }
.subtitle       { font-size: 14px; color: #777; margin-bottom: 28px; }

.alert-error {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  background: #fee2e2;
  color: #991b1b;
  padding: 12px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 18px;
  line-height: 1.5;
}

.close-error {
  background: none;
  border: none;
  color: #991b1b;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  flex-shrink: 0;
  opacity: .7;
}
.close-error:hover { opacity: 1; }

.field           { margin-bottom: 18px; }
.field label     { display: block; font-size: 13px; margin-bottom: 6px; color: #444; }
.field input     { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ddd; font-size: 14px; box-sizing: border-box; }
.field input:focus { outline: none; border-color: #f5a623; }

.login-btn {
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  background: #f5a623;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  transition: background .2s;
  font-family: inherit;
}
.login-btn:hover    { background: #d9941d; }
.login-btn:disabled { opacity: .6; cursor: not-allowed; }

.divider { height: 1px; background: #eee; margin: 28px 0 18px; }

.register-text { font-size: 14px; color: #333; text-align: center; margin-bottom: 10px; }

.register-btn {
  display: block;
  width: 100%;
  padding: 11px;
  background: #2f2f2f;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  transition: background .2s;
  box-sizing: border-box;
}
.register-btn:hover { background: #000; }

@media (max-width: 480px) {
  .login-card { padding: 28px 20px; }
  .login-card h1 { font-size: 22px; }
}
</style>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import AppIcon from '@/components/shared/AppIcon.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(route.query.message ?? '')
const showPassword = ref(false)

const roleRedirect = {
  admin: '/admin/dashboard',
  advisor: '/advisor/dashboard',
  client: '/'
}

const submit = async () => {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push(roleRedirect[auth.role] ?? '/')
  } catch (err) {
    error.value = err?.message ?? 'Credenciales incorrectas o error de conexión.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-right">
      <div class="login-card">
        <div class="card-header">
          <div class="card-logo">J</div>
          <h1>Iniciar sesión</h1>
          <p class="subtitle">Acceso para administradores, asesores<br/>y clientes registrados</p>
        </div>

        <div v-if="success" class="alert-success">{{ success }}</div>

        <div v-if="error" class="alert-error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <span>{{ error }}</span>
          <button class="close-error" @click="error = ''"><AppIcon name="x" :size="16" /></button>
        </div>

        <form @submit.prevent="submit" class="login-form">
          <div class="field">
            <label>Correo electrónico</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              <input v-model="email" type="email" placeholder="correo@ejemplo.com" autocomplete="email" required />
            </div>
          </div>

          <div class="field">
            <div class="label-row">
              <label>Contraseña</label>
              <RouterLink to="/recuperar-contrasena" class="forgot-link">¿Olvidaste tu contraseña?</RouterLink>
            </div>
            <div class="input-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              <input v-model="password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••••" autocomplete="current-password" required />
              <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                <svg v-if="!showPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
          </div>

          <button class="login-btn" type="submit" :disabled="loading">
            <span v-if="!loading">Ingresar</span>
            <span v-else class="loading-text">Ingresando...</span>
          </button>
        </form>

        <div class="divider"><span>o</span></div>

        <p class="register-text">¿Quieres vender o rentar una propiedad?</p>
        <RouterLink to="/registro" class="register-btn">Crear cuenta y registrar propiedad</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
* { box-sizing: border-box; }
.login-page { min-height: 100vh; display: flex; font-family: 'Poppins', sans-serif; background: #f5f2ec; }
.login-right { width: 100%; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 40px 24px; background: linear-gradient(to bottom, rgba(5, 15, 35, 0.62) 0%, rgba(7, 23, 45, 0.55) 60%, rgba(5, 15, 35, 0.72) 100%), url('@/assets/images/fondo2.jpg') center center / cover no-repeat; }
.login-card { background: white; padding: 48px 44px; width: 100%; max-width: 440px; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); }
.card-logo { width: 48px; height: 48px; background: linear-gradient(135deg, #d4a34a, #f0c36f); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 22px; color: #091d39; margin: 0 auto 16px; }
.card-header { margin-bottom: 32px; text-align: center; }
.card-header h1 { font-size: 30px; font-weight: 500; color: #07172d; margin: 0 0 8px; }
.subtitle { font-size: 13.5px; color: #65717e; line-height: 1.6; margin: 0; }
.alert-success { background: #ecfdf3; color: #065f46; padding: 12px; border-radius: 8px; border: 1px solid #a7f3d0; margin-bottom: 18px; font-size: 13px; }
.alert-error { display: flex; align-items: flex-start; gap: 10px; background: #fef2f2; color: #b91c1c; padding: 12px 14px; border-radius: 8px; border: 1px solid #fecaca; font-size: 13px; margin-bottom: 20px; }
.close-error { background: none; border: none; color: #b91c1c; cursor: pointer; margin-left: auto; }
.login-form { display: flex; flex-direction: column; }
.field { margin-bottom: 20px; }
.field label { display: block; font-size: 13px; font-weight: 500; color: #07172d; margin-bottom: 7px; }
.label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px; }
.label-row label { margin-bottom: 0; }
.forgot-link { font-size: 12.5px; color: #d4a34a; text-decoration: none; font-weight: 600; }
.forgot-link:hover { text-decoration: underline; }
.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 13px; color: #65717e; pointer-events: none; }
.input-wrapper input { width: 100%; padding: 11px 14px 11px 40px; border: 1.5px solid #dde2ec; border-radius: 9px; font-size: 14px; color: #07172d; background: #fafaf8; outline: none; }
.input-wrapper input:focus { border-color: #07172d; background: #fff; box-shadow: 0 0 0 3px rgba(7,23,45,0.08); }
.toggle-password { position: absolute; right: 12px; background: none; border: none; cursor: pointer; color: #65717e; }
.login-btn { width: 100%; margin-top: 8px; padding: 13px; background: #d4a34a; color: #fff; border: none; border-radius: 9px; font-size: 15px; font-weight: 600; cursor: pointer; }
.login-btn:hover:not(:disabled) { background: #b8892e; }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.divider { display: flex; align-items: center; gap: 14px; margin: 28px 0 20px; color: #a0adb8; font-size: 13px; }
.divider::before, .divider::after { content: ''; flex: 1; height: 1px; background: #e5e9f0; }
.register-text { font-size: 13.5px; color: #65717e; text-align: center; margin: 0 0 12px; }
.register-btn { display: flex; align-items: center; justify-content: center; width: 100%; padding: 12px; background: #07172d; color: white; border-radius: 9px; font-size: 14px; font-weight: 500; text-decoration: none; }
.register-btn:hover { background: #051525; }
@media (max-width: 768px) { .login-card { padding: 36px 28px; } }
@media (max-width: 480px) { .login-right { padding: 24px 16px; } .login-card { padding: 28px 20px; } }
</style>


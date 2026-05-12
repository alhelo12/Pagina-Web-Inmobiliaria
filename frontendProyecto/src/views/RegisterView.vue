<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'

const router = useRouter()

const form = ref({
  first_name: '',
  last_name:  '',
  email:     '',
  phone:     '',
  password:  '',
  confirm:   ''
})

const loading      = ref(false)
const error        = ref('')
const success      = ref(false)
const showPassword = ref(false)
const showConfirm  = ref(false)

const submit = async () => {
  error.value = ''

  if (form.value.password !== form.value.confirm) {
    error.value = 'Las contraseñas no coinciden'
    return
  }

  loading.value = true
  try {
    await authApi.registerClient({
      full_name: `${form.value.first_name} ${form.value.last_name}`.trim(),
      email:     form.value.email,
      phone:     form.value.phone || undefined,
      password:  form.value.password
    })
    success.value = true
    setTimeout(() => router.push('/login'), 2500)
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al crear cuenta'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-right">
      <div class="register-card">

        <!-- Éxito -->
        <div v-if="success" class="success-state">
          <div class="card-logo">✓</div>
          <div class="card-header">
            <h1>¡Cuenta creada!</h1>
            <p class="subtitle">Tu cuenta fue creada correctamente.<br/>Redirigiendo al inicio de sesión...</p>
          </div>
        </div>

        <template v-else>
          <!-- Logo + encabezado -->
          <div class="card-header">
            <div class="card-logo">J</div>
            <h1>Crear cuenta</h1>
            <p class="subtitle">Regístrate para publicar tu propiedad<br/>y recibir asesoría personalizada</p>
          </div>

          <!-- Error -->
          <div v-if="error" class="alert-error">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            <span>{{ error }}</span>
            <button class="close-error" @click="error = ''">✕</button>
          </div>

          <form @submit.prevent="submit" class="register-form">

            <!-- Nombre + Apellido -->
            <div class="field-row">
              <div class="field">
                <label>Nombre</label>
                <div class="input-wrapper">
                  <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  <input v-model="form.first_name" type="text" placeholder="Tu nombre" autocomplete="given-name" required />
                </div>
              </div>
              <div class="field">
                <label>Apellido</label>
                <div class="input-wrapper">
                  <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  <input v-model="form.last_name" type="text" placeholder="Tu apellido" autocomplete="family-name" required />
                </div>
              </div>
            </div>

            <!-- Correo -->
            <div class="field">
              <label>Correo electrónico</label>
              <div class="input-wrapper">
                <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                <input v-model="form.email" type="email" placeholder="correo@ejemplo.com" autocomplete="email" required />
              </div>
            </div>

            <!-- Teléfono -->
            <div class="field">
              <label>Teléfono <span class="optional">(opcional)</span></label>
              <div class="input-wrapper">
                <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.5 2 2 0 0 1 3.58 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.54a16 16 0 0 0 6.29 6.29l.92-.92a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                <input v-model="form.phone" type="tel" placeholder="+52 33 1234 5678" autocomplete="tel" />
              </div>
            </div>

            <!-- Contraseña -->
            <div class="field">
              <label>Contraseña</label>
              <div class="input-wrapper">
                <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                <input v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="Mínimo 8 caracteres" autocomplete="new-password" required />
                <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                  <svg v-if="!showPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
            </div>

            <!-- Confirmar contraseña -->
            <div class="field">
              <label>Confirmar contraseña</label>
              <div class="input-wrapper">
                <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                <input v-model="form.confirm" :type="showConfirm ? 'text' : 'password'" placeholder="Repite tu contraseña" autocomplete="new-password" required />
                <button type="button" class="toggle-password" @click="showConfirm = !showConfirm">
                  <svg v-if="!showConfirm" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
            </div>

            <button class="register-btn" type="submit" :disabled="loading">
              <span v-if="!loading">Crear cuenta →</span>
              <span v-else class="loading-text">
                <svg class="spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                Creando cuenta...
              </span>
            </button>

          </form>

          <div class="divider"><span>o</span></div>

          <p class="login-text">¿Ya tienes una cuenta?</p>
          <RouterLink to="/login" class="login-link-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
            Iniciar sesión
          </RouterLink>
        </template>

      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

* { box-sizing: border-box; }

.register-page {
  min-height: 100vh;
  display: flex;
  font-family: 'Poppins', sans-serif;
  background: #f5f2ec;
}

/* ── Fondo con imagen (mismo que login) ── */
.register-right {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  background:
    linear-gradient(
      to bottom,
      rgba(5, 15, 35, 0.62) 0%,
      rgba(7, 23, 45, 0.55) 60%,
      rgba(5, 15, 35, 0.72) 100%
    ),
    url('@/assets/images/fondo1.jpg') center center / cover no-repeat;
}

/* ── Card (mismo tamaño y bordes que login) ── */
.register-card {
  background: white;
  padding: 48px 56px;
  width: 100%;
  max-width: 560px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
}

/* ── Logo ── */
.card-logo {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #d4a34a, #f0c36f);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 22px;
  color: #091d39;
  margin: 0 auto 16px;
  font-family: 'Georgia', 'Times New Roman', serif;
}

/* ── Encabezado ── */
.card-header {
  margin-bottom: 28px;
  text-align: center;
}

.card-header h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 30px;
  font-weight: 400;
  color: #07172d;
  margin: 0 0 8px;
}

.subtitle {
  font-size: 13.5px;
  color: #65717e;
  line-height: 1.6;
  margin: 0;
}

.optional {
  font-size: 12px;
  font-weight: 400;
  color: #a0adb8;
}

/* ── Error ── */
.alert-error {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #fef2f2;
  color: #b91c1c;
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid #fecaca;
  font-size: 13px;
  margin-bottom: 20px;
  line-height: 1.5;
}

.alert-error svg { flex-shrink: 0; margin-top: 1px; }

.close-error {
  background: none;
  border: none;
  color: #b91c1c;
  cursor: pointer;
  font-size: 12px;
  padding: 0;
  margin-left: auto;
  flex-shrink: 0;
  opacity: 0.6;
}
.close-error:hover { opacity: 1; }

/* ── Formulario ── */
.register-form {
  display: flex;
  flex-direction: column;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 18px;
}

.field-row .field { margin-bottom: 0; }

.field { margin-bottom: 18px; }

.field label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #07172d;
  margin-bottom: 7px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 13px;
  color: #65717e;
  pointer-events: none;
}

.input-wrapper input {
  width: 100%;
  padding: 11px 14px 11px 40px;
  border: 1.5px solid #dde2ec;
  border-radius: 9px;
  font-size: 14px;
  font-family: 'Poppins', sans-serif;
  color: #07172d;
  background: #fafaf8;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  outline: none;
}

.input-wrapper input::placeholder { color: #a0adb8; }

.input-wrapper input:focus {
  border-color: #07172d;
  background: white;
  box-shadow: 0 0 0 3px rgba(7, 23, 45, 0.08);
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  color: #65717e;
  padding: 4px;
  display: flex;
  align-items: center;
}
.toggle-password:hover { color: #07172d; }

/* ── Botón principal ── */
.register-btn {
  width: 100%;
  margin-top: 8px;
  padding: 13px;
  background: #d4a34a;
  color: white;
  border: none;
  border-radius: 9px;
  font-size: 15px;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
  letter-spacing: 0.3px;
}

.register-btn:hover:not(:disabled) {
  background: #b8892e;
  box-shadow: 0 4px 14px rgba(212, 163, 74, 0.35);
}

.register-btn:active:not(:disabled) { transform: translateY(1px); }
.register-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spin { animation: spin 0.8s linear infinite; }

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Divisor ── */
.divider {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 24px 0 18px;
  color: #a0adb8;
  font-size: 13px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e5e9f0;
}

/* ── Link login ── */
.login-text {
  font-size: 13.5px;
  color: #65717e;
  text-align: center;
  margin: 0 0 12px;
}

.login-link-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  background: #07172d;
  color: white;
  border: none;
  border-radius: 9px;
  font-size: 14px;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.2s, box-shadow 0.2s;
}

.login-link-btn:hover {
  background: #051525;
  box-shadow: 0 4px 14px rgba(7, 23, 45, 0.2);
}

/* ── Estado éxito ── */
.success-state {
  text-align: center;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .register-card { padding: 36px 28px; }
}

@media (max-width: 480px) {
  .register-right { padding: 24px 16px; }
  .register-card { padding: 28px 20px; }
  .card-header h1 { font-size: 26px; }
}
</style>
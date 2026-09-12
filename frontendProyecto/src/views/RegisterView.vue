<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'

const router = useRouter()
let redirectTimer = null
onUnmounted(() => { if (redirectTimer) clearTimeout(redirectTimer) })

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
    redirectTimer = setTimeout(() => router.push('/login'), 2500)
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al crear cuenta'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth">

    <!-- ── Panel fotográfico ── -->
    <aside class="auth-photo">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">J</span>
        <span class="brand-name">JAKEDA</span>
      </RouterLink>

      <blockquote class="quote">
        <p class="serif-display">“Publica tu propiedad con respaldo jurídico.”</p>
        <cite>Miles de personas confían en Jakeda cada día</cite>
      </blockquote>
    </aside>

    <!-- ── Panel marfil: formulario ── -->
    <div class="auth-form">
      <div class="auth-card">

        <!-- Éxito -->
        <div v-if="success" class="success-state">
          <p class="eyebrow-label">Jakeda · Registro</p>
          <h1 class="serif-display">¡Cuenta creada!</h1>
          <p class="sub">Tu cuenta fue creada correctamente.<br />Redirigiendo al inicio de sesión...</p>
        </div>

        <template v-else>
          <p class="eyebrow-label">Jakeda · Registro</p>
          <h1 class="serif-display">Crea tu cuenta</h1>
          <p class="sub">Regístrate para publicar tu propiedad<br />y recibir asesoría personalizada</p>

          <!-- Error -->
          <div v-if="error" class="alert-error">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            <span>{{ error }}</span>
            <button class="close-error" aria-label="Cerrar error" @click="error = ''">✕</button>
          </div>

          <form @submit.prevent="submit" class="form">

            <!-- Nombre + Apellido -->
            <div class="field-row">
              <div class="field-underline">
                <label class="flabel" for="reg-first">Nombre</label>
                <input id="reg-first" v-model="form.first_name" type="text" placeholder="Tu nombre" autocomplete="given-name" required />
              </div>
              <div class="field-underline">
                <label class="flabel" for="reg-last">Apellido</label>
                <input id="reg-last" v-model="form.last_name" type="text" placeholder="Tu apellido" autocomplete="family-name" required />
              </div>
            </div>

            <!-- Correo -->
            <div class="field-underline">
              <label class="flabel" for="reg-email">Correo electrónico</label>
              <input id="reg-email" v-model="form.email" type="email" placeholder="correo@ejemplo.com" autocomplete="email" required />
            </div>

            <!-- Teléfono -->
            <div class="field-underline">
              <label class="flabel" for="reg-phone">Teléfono <span class="optional">(opcional)</span></label>
              <input id="reg-phone" v-model="form.phone" type="tel" placeholder="+52 33 1234 5678" autocomplete="tel" />
            </div>

            <!-- Contraseña -->
            <div class="field-underline">
              <label class="flabel" for="reg-pass">Contraseña</label>
              <div class="uwrap">
                <input id="reg-pass" v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="Mínimo 8 caracteres" autocomplete="new-password" required />
                <button type="button" class="toggle-password" :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'" @click="showPassword = !showPassword">
                  <svg v-if="!showPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
            </div>

            <!-- Confirmar contraseña -->
            <div class="field-underline">
              <label class="flabel" for="reg-confirm">Confirmar contraseña</label>
              <div class="uwrap">
                <input id="reg-confirm" v-model="form.confirm" :type="showConfirm ? 'text' : 'password'" placeholder="Repite tu contraseña" autocomplete="new-password" required />
                <button type="button" class="toggle-password" :aria-label="showConfirm ? 'Ocultar contraseña' : 'Mostrar contraseña'" @click="showConfirm = !showConfirm">
                  <svg v-if="!showConfirm" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
            </div>

            <button class="btn-ink cta" type="submit" :disabled="loading">
              <span v-if="!loading">Crear cuenta →</span>
              <span v-else class="loading-text">
                <svg class="spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                Creando cuenta...
              </span>
            </button>

          </form>

          <div class="divider"><span>o</span></div>

          <p class="alt-text">¿Ya tienes una cuenta?</p>
          <RouterLink to="/login" class="btn-ink cta alt">Iniciar sesión</RouterLink>
        </template>

      </div>
    </div>
  </div>
</template>

<style scoped>
.auth {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  background: var(--color-ivory);
}

/* ── Panel fotográfico ── */
.auth-photo {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 24px;
  padding: 36px 44px 48px;
  background: url('@/assets/images/fondo2.jpg') center / cover no-repeat;
  color: #fff;
  overflow: hidden;
}
.auth-photo::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(7, 27, 28, 0.85) 0%, rgba(7, 27, 28, 0.35) 55%, rgba(7, 27, 28, 0.45) 100%);
}
.auth-photo > * { position: relative; z-index: 1; }

.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  align-self: flex-start;
}
.brand-mark {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  background: var(--color-brass);
  color: var(--color-ink);
  font-family: var(--serif);
  font-weight: 700;
  font-size: 20px;
}
.brand-name {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #fff;
}

.quote { margin: 0; max-width: 420px; }
.quote p {
  margin: 0 0 12px;
  font-size: clamp(28px, 3.2vw, 40px);
  color: #fff;
}
.quote cite {
  font-style: normal;
  font-size: 14px;
  letter-spacing: 0.06em;
  color: rgba(255, 255, 255, 0.75);
}

/* ── Panel marfil ── */
.auth-form {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(36px, 5vw, 64px) clamp(24px, 5vw, 72px);
  background: var(--color-ivory);
  overflow-y: auto;
}
.auth-card { width: min(440px, 100%); }

.auth-card h1 {
  margin: 10px 0 8px;
  font-size: clamp(32px, 3.4vw, 44px);
  color: var(--color-ink);
}
.sub {
  margin: 0 0 26px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--color-muted);
}
.optional {
  font-size: 11px;
  font-weight: 400;
  letter-spacing: 0.04em;
  color: #a9a294;
  text-transform: none;
}

/* Error */
.alert-error {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #fdf3f0;
  color: #b91c1c;
  padding: 12px 14px;
  border: 1px solid #f0d5cd;
  font-size: 13px;
  margin-bottom: 22px;
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

/* Formulario underline */
.form { display: flex; flex-direction: column; }
.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.field-underline { margin-bottom: 22px; }
.field-row .field-underline { margin-bottom: 22px; }
.flabel {
  display: block;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-weight: 600;
  color: var(--color-charcoal);
  margin-bottom: 2px;
}
.field-underline input::placeholder { color: #a9a294; }
.uwrap { position: relative; display: flex; align-items: center; }
.uwrap input { padding-right: 34px; }
.toggle-password {
  position: absolute;
  right: 2px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-muted);
  padding: 6px;
  display: flex;
  align-items: center;
}
.toggle-password:hover { color: var(--color-ink); }

/* CTA petrol full-width */
.cta { width: 100%; margin-top: 8px; padding: 16px 22px; }
.cta:disabled { opacity: 0.6; cursor: not-allowed; }
.cta.alt { text-decoration: none; background: transparent; color: var(--color-petrol); }
.cta.alt:hover { background: var(--color-petrol); color: #fff; }

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.spin { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Divisor */
.divider {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 26px 0 18px;
  color: #a9a294;
  font-size: 13px;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--color-line);
}
.alt-text {
  font-size: 13.5px;
  color: var(--color-muted);
  text-align: center;
  margin: 0 0 12px;
}

/* Estado éxito */
.success-state { text-align: left; }

/* ── Responsive ── */
@media (max-width: 900px) {
  .auth { grid-template-columns: 1fr; }
  .auth-photo { min-height: 280px; padding: 28px 24px 32px; }
  .quote p { font-size: clamp(24px, 6vw, 30px); }
}
@media (max-width: 640px) {
  .field-row { grid-template-columns: 1fr; gap: 0; }
}
</style>

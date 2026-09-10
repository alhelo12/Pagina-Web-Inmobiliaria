<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()
const email = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

const submit = async () => {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    await auth.forgotPassword(email.value)
    success.value = 'Te enviamos un enlace a tu correo para restablecer tu contraseña.'
  } catch (err) {
    error.value = err?.message ?? 'No se pudo enviar el enlace.'
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
        <p class="serif-display">“Recupera el acceso en un minuto.”</p>
        <cite>Te enviaremos un enlace seguro a tu correo</cite>
      </blockquote>
    </aside>

    <!-- ── Panel marfil: formulario ── -->
    <div class="auth-form">
      <div class="auth-card">
        <p class="eyebrow-label">Jakeda · Recuperar acceso</p>
        <h1 class="serif-display">Recupera tu contraseña</h1>
        <p class="sub">Ingresa tu correo y te enviaremos un enlace.</p>

        <form @submit.prevent="submit" class="form">
          <div class="field-underline">
            <label class="flabel" for="rec-email">Correo electrónico</label>
            <input id="rec-email" v-model="email" type="email" placeholder="correo@ejemplo.com" required />
          </div>
          <button class="btn-ink cta" type="submit" :disabled="loading">{{ loading ? 'Enviando...' : 'Enviar enlace →' }}</button>
        </form>

        <p v-if="success" class="ok">{{ success }}</p>
        <p v-if="error" class="err">{{ error }}</p>

        <RouterLink to="/login" class="back">← Volver al inicio de sesión</RouterLink>
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
  padding: clamp(36px, 5vw, 72px) clamp(24px, 5vw, 72px);
  background: var(--color-ivory);
}
.auth-card { width: min(420px, 100%); }

.auth-card h1 {
  margin: 10px 0 8px;
  font-size: clamp(32px, 3.4vw, 44px);
  color: var(--color-ink);
}
.sub {
  margin: 0 0 28px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--color-muted);
}

/* Formulario underline */
.form { display: flex; flex-direction: column; }
.field-underline { margin-bottom: 24px; }
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

/* CTA petrol full-width */
.cta { width: 100%; margin-top: 8px; padding: 16px 22px; }
.cta:disabled { opacity: 0.6; cursor: not-allowed; }

.ok { margin-top: 16px; color: #0c5c46; font-size: 14px; line-height: 1.6; }
.err { margin-top: 16px; color: #b91c1c; font-size: 14px; line-height: 1.6; }

.back {
  display: inline-block;
  margin-top: 24px;
  font-size: 13px;
  color: var(--color-brass-deep);
  text-decoration: underline;
  text-underline-offset: 3px;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .auth { grid-template-columns: 1fr; }
  .auth-photo { min-height: 280px; padding: 28px 24px 32px; }
  .quote p { font-size: clamp(24px, 6vw, 30px); }
}
</style>

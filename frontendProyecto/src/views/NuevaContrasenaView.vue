<template>
  <div class="auth">

    <!-- ── Panel fotográfico ── -->
    <aside class="auth-photo">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">J</span>
        <span class="brand-name">JAKEDA</span>
      </RouterLink>

      <blockquote class="quote">
        <p class="serif-display">“Un nuevo comienzo, seguro.”</p>
        <cite>Elige una contraseña fuerte para proteger tu cuenta</cite>
      </blockquote>
    </aside>

    <!-- ── Panel marfil: formulario ── -->
    <div class="auth-form">
      <div class="auth-card">
        <p class="eyebrow-label">Jakeda · Nueva contraseña</p>
        <h1 class="serif-display">Define tu nueva contraseña</h1>
        <p class="sub">Define tu nueva contraseña para continuar.</p>

        <form @submit.prevent="submit" class="form">
          <div class="field-underline">
            <label class="flabel" for="new-pass">Nueva contraseña</label>
            <input id="new-pass" v-model="password" type="password" placeholder="Nueva contraseña" required />
          </div>
          <div class="field-underline">
            <label class="flabel" for="new-confirm">Confirmar contraseña</label>
            <input id="new-confirm" v-model="confirm" type="password" placeholder="Confirmar contraseña" required />
          </div>
          <button class="btn-ink cta" type="submit" :disabled="loading">{{ loading ? 'Actualizando...' : 'Actualizar contraseña →' }}</button>
        </form>

        <p v-if="error" class="err" role="alert">{{ error }}</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const password = ref('')
const confirm = ref('')
const loading = ref(false)
const error = ref('')

const submit = async () => {
  error.value = ''
  if (password.value !== confirm.value) {
    error.value = 'Las contraseñas no coinciden.'
    return
  }

  const token = route.query.token
  if (!token) {
    error.value = 'Enlace inválido o expirado.'
    return
  }

  loading.value = true
  try {
    await auth.resetPassword(token, password.value)
    router.push({ path: '/login', query: { message: 'Contraseña actualizada correctamente.' } })
  } catch (err) {
    error.value = err?.response?.data?.detail ?? err?.message ?? 'No se pudo actualizar la contraseña.'
  } finally {
    loading.value = false
  }
}
</script>

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
.field-underline input::placeholder { color: var(--color-muted); }

/* CTA petrol full-width */
.cta { width: 100%; margin-top: 8px; padding: 16px 22px; }
.cta:disabled { opacity: 0.6; cursor: not-allowed; }

.err { margin-top: 16px; color: var(--color-danger); font-size: 14px; line-height: 1.6; }

/* ── Responsive ── */
@media (max-width: 900px) {
  .auth { grid-template-columns: 1fr; }
  .auth-photo { min-height: 280px; padding: 28px 24px 32px; }
  .quote p { font-size: clamp(24px, 6vw, 30px); }
}
</style>

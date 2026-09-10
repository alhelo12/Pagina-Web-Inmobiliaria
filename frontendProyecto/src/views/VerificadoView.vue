<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { authApi } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const message = ref('')

onMounted(async () => {
  const token = route.query.token
  if (!token) {
    message.value = 'Enlace inválido o expirado.'
    return
  }

  try {
    await authApi.verifyEmail(token)
    auth.isEmailVerified = true
    auth.persistSession()
    message.value = 'Correo verificado correctamente.'
    setTimeout(() => {
      if (auth.isLogged) {
        router.push('/cliente/dashboard')
      } else {
        router.push('/login')
      }
    }, 2000)
  } catch {
    message.value = 'El enlace ha expirado o es inválido.'
  }
})
</script>

<template>
  <section class="verify-wrap">
    <article class="verify-card">
      <p class="eyebrow-label">Jakeda · Verificación</p>
      <h1 class="serif-display">{{ message || 'Verificando...' }}</h1>
      <p v-if="auth.isLogged" class="sub">Redirigiendo a tu panel...</p>
      <RouterLink v-else to="/login" class="btn-ink cta">Ir a login</RouterLink>
    </article>
  </section>
</template>

<style scoped>
.verify-wrap {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: var(--color-ivory);
}
.verify-card {
  width: min(480px, 100%);
  background: var(--color-card);
  border: 1px solid var(--color-line);
  box-shadow: var(--shadow-soft);
  padding: 44px 40px;
  text-align: center;
}
.verify-card h1 {
  margin: 10px 0 0;
  font-size: clamp(28px, 4vw, 38px);
  color: var(--color-ink);
}
.sub {
  margin: 14px 0 0;
  color: var(--color-muted);
  font-size: 14px;
}
.cta {
  display: inline-flex;
  width: 100%;
  margin-top: 24px;
  padding: 16px 22px;
  text-decoration: none;
}
@media (max-width: 480px) {
  .verify-card { padding: 32px 24px; }
}
</style>

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
  <section class="state-wrap">
    <article class="state-card">
      <h1>Recuperar contraseña</h1>
      <p>Ingresa tu correo y te enviaremos un enlace.</p>

      <form @submit.prevent="submit" class="form">
        <input v-model="email" type="email" placeholder="correo@ejemplo.com" required />
        <button type="submit" :disabled="loading">{{ loading ? 'Enviando...' : 'Enviar enlace' }}</button>
      </form>

      <p v-if="success" class="ok">{{ success }}</p>
      <p v-if="error" class="err">{{ error }}</p>
    </article>
  </section>
</template>

<style scoped>
.state-wrap { min-height: 80vh; display: grid; place-items: center; padding: 22px; background: #f5f2ec; font-family: 'Poppins', sans-serif; }
.state-card { width: min(94vw, 760px); background: #fff; border: 1px solid #e7dfd0; border-radius: 16px; padding: 28px; }
h1 { margin: 0; color: #07182c; font-size: clamp(36px, 4vw, 50px); line-height: 1.05; }
p { margin: 12px 0 0; color: #4f6074; font-size: 18px; }
.form { margin-top: 18px; display: grid; gap: 10px; }
input { min-height: 48px; border: 1px solid #d9e0e8; border-radius: 12px; padding: 0 14px; font: inherit; font-size: 16px; color: #1f2937; }
input:focus { outline: none; border-color: #07182c; box-shadow: 0 0 0 2px rgba(7, 24, 44, 0.12); }
button { margin-top: 2px; min-height: 44px; border: none; border-radius: 10px; background: #d8a54d; color: #07182c; font-weight: 700; font-size: 20px; cursor: pointer; }
button:disabled { opacity: 0.65; cursor: not-allowed; }
.ok { margin-top: 12px; color: #065f46; font-size: 14px; }
.err { margin-top: 12px; color: #b91c1c; font-size: 14px; }
@media (max-width: 640px) { .state-card { padding: 20px; } h1 { font-size: 34px; } p { font-size: 16px; } button { font-size: 18px; } }
</style>

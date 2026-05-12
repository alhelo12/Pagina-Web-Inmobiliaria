<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const auth = useAuthStore()

onMounted(() => {
  if (auth.isLogged && auth.isSupabaseUser) {
    auth.isEmailVerified = true
    auth.persistSession()
    setTimeout(() => router.push('/cliente/dashboard'), 2000)
  }
})
</script>

<template>
  <section class="state-wrap">
    <article class="state-card">
      <h1>Tu correo ha sido verificado.</h1>
      <p v-if="auth.isLogged">Redirigiendo a tu panel...</p>
      <p v-else>Ya puedes iniciar sesión.</p>
      <RouterLink to="/login" class="state-btn">Ir a login</RouterLink>
    </article>
  </section>
</template>

<style scoped>
.state-wrap { min-height: 80vh; display: grid; place-items: center; padding: 22px; background: #f5f2ec; font-family: 'Poppins', sans-serif; }
.state-card { width: min(94vw, 760px); background: #fff; border: 1px solid #e7dfd0; border-radius: 16px; padding: 28px; text-align: center; }
.state-card h1 { margin: 0; color: #07182c; font-size: clamp(36px, 4vw, 50px); line-height: 1.05; }
.state-card p { margin: 14px 0 0; color: #4f6074; font-size: 18px; }
.state-btn { display: inline-flex; min-height: 46px; align-items: center; justify-content: center; margin-top: 20px; padding: 0 20px; background: #D8A54D; color: #07182C; border-radius: 10px; font-weight: 700; text-decoration: none; }
</style>
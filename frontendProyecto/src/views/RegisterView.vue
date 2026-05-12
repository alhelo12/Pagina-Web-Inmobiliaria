<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()

const form = ref({
  full_name: '',
  email: '',
  phone: '',
  password: '',
  confirm: ''
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

const submit = async () => {
  error.value = ''

  if (form.value.password !== form.value.confirm) {
    error.value = 'Las contraseñas no coinciden'
    return
  }

  loading.value = true
  try {
    await auth.register(form.value.email, form.value.password, form.value.full_name, form.value.phone)
    success.value = true
  } catch (err) {
    error.value = err?.message ?? 'Error al crear cuenta'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="register">
    <div class="card">
      <h2>Crear cuenta</h2>
      <p class="subtitle">Regístrate para publicar tu propiedad y recibir asesoría</p>

      <div v-if="success" class="alert-success">
        Cuenta creada. Revisa tu correo para verificar tu cuenta antes de iniciar sesión.
      </div>

      <template v-else>
        <div v-if="error" class="alert-error">{{ error }}</div>

        <form @submit.prevent="submit">
          <input v-model="form.full_name" type="text" placeholder="Nombre completo" required />
          <input v-model="form.email" type="email" placeholder="Correo electrónico" required />
          <input v-model="form.phone" type="tel" placeholder="Teléfono (opcional)" />
          <input v-model="form.password" type="password" placeholder="Contraseña (mín. 8 car.)" required />
          <input v-model="form.confirm" type="password" placeholder="Confirmar contraseña" required />
          <button type="submit" :disabled="loading">{{ loading ? 'Creando cuenta...' : 'Crear cuenta' }}</button>
        </form>

        <div class="login-link">¿Ya tienes cuenta? <RouterLink to="/login">Inicia sesión</RouterLink></div>
      </template>
    </div>
  </section>
</template>

<style scoped>
.register { min-height: 90vh; display: flex; align-items: center; justify-content: center; background: #f5f2ec; font-family: 'Poppins', sans-serif; }
.card { background: #fff; width: 100%; max-width: 420px; padding: 32px; border-radius: 12px; box-shadow: 0 15px 40px rgba(0,0,0,.1); }
.card h2 { font-size: 28px; font-weight: 600; text-align: center; color: #07182C; }
.subtitle { text-align: center; color: #666; font-size: 14px; margin: 8px 0 24px; }
.alert-success { background: #ecfdf3; color: #065f46; padding: 12px; border-radius: 8px; border: 1px solid #a7f3d0; text-align: center; margin-bottom: 18px; }
.alert-error { background: #fee2e2; color: #991b1b; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 14px; }
form { display: flex; flex-direction: column; gap: 14px; }
input { padding: 12px; border-radius: 6px; border: 1px solid #ddd; font-size: 14px; font-family: inherit; }
input:focus { outline: none; border-color: #D8A54D; }
button { margin-top: 12px; padding: 12px; background: #D8A54D; color: #fff; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; font-family: inherit; }
button:hover { background: #b8892e; }
button:disabled { opacity: .6; cursor: not-allowed; }
.login-link { margin-top: 18px; text-align: center; font-size: 14px; }
.login-link a { color: #D8A54D; font-weight: 600; }
</style>


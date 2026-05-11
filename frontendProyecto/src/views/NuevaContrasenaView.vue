<template>
  <section class="state-wrap">
    <article class="state-card">
      <h1>Nueva contraseña</h1>
      <p>Define tu nueva contraseña para continuar.</p>

      <form @submit.prevent="submit" class="form">
        <input v-model="password" type="password" placeholder="Nueva contraseña" required />
        <input v-model="confirm" type="password" placeholder="Confirmar contraseña" required />
        <button type="submit" :disabled="loading">{{ loading ? 'Actualizando...' : 'Actualizar contraseña' }}</button>
      </form>

      <p v-if="error" class="err">{{ error }}</p>
    </article>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()
const router = useRouter()

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

  loading.value = true
  try {
    await auth.updatePassword(password.value)
    router.push({ path: '/login', query: { message: 'Contraseña actualizada correctamente.' } })
  } catch (err) {
    error.value = err?.message ?? 'No se pudo actualizar la contraseña.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.state-wrap {
  min-height: 80vh;
  display: grid;
  place-items: center;
  padding: 22px;
  background: #f5f2ec;
  font-family: 'Poppins', sans-serif;
}

.state-card {
  width: min(94vw, 760px);
  background: #fff;
  border: 1px solid #e7dfd0;
  border-radius: 16px;
  padding: 28px;
}

h1 {
  margin: 0;
  color: #07182c;
  font-size: clamp(36px, 4vw, 50px);
  line-height: 1.05;
}

p {
  margin: 12px 0 0;
  color: #4f6074;
  font-size: 18px;
}

.form {
  margin-top: 18px;
  display: grid;
  gap: 10px;
}

input {
  min-height: 48px;
  border: 1px solid #d9e0e8;
  border-radius: 12px;
  padding: 0 14px;
  font: inherit;
  font-size: 16px;
  color: #1f2937;
}

input:focus {
  outline: none;
  border-color: #07182c;
  box-shadow: 0 0 0 2px rgba(7, 24, 44, 0.12);
}

button {
  margin-top: 2px;
  min-height: 44px;
  border: none;
  border-radius: 10px;
  background: #d8a54d;
  color: #07182c;
  font-weight: 700;
  font-size: 22px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.err {
  margin-top: 12px;
  color: #b91c1c;
  font-size: 14px;
}

@media (max-width: 640px) {
  .state-card {
    padding: 20px;
  }

  h1 {
    font-size: 34px;
  }

  p {
    font-size: 16px;
  }

  button {
    font-size: 18px;
  }
}
</style>

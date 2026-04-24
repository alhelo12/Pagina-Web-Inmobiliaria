<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'

const router = useRouter()

const form = ref({
  full_name: '',
  email:     '',
  phone:     '',
  password:  '',
  confirm:   ''
})

const loading = ref(false)
const error   = ref('')
const success = ref(false)

const submit = async () => {
  error.value = ''

  if (form.value.password !== form.value.confirm) {
    error.value = 'Las contraseñas no coinciden'
    return
  }

  loading.value = true
  try {
    await authApi.registerClient({
      full_name: form.value.full_name,
      email:     form.value.email,
      phone:     form.value.phone || undefined,
      password:  form.value.password
    })
    success.value = true
    setTimeout(() => router.push('/login'), 2000)
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al crear cuenta'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="register">
    <div class="card">
      <h2>Crear cuenta</h2>
      <p class="subtitle">
        Regístrate para publicar tu propiedad y recibir asesoría
      </p>

      <!-- ÉXITO -->
      <div v-if="success" class="alert-success">
        ✅ Cuenta creada correctamente. Redirigiendo al login...
      </div>

      <template v-else>
        <!-- ERROR -->
        <div v-if="error" class="alert-error">{{ error }}</div>

        <form @submit.prevent="submit">
          <input v-model="form.full_name" type="text"     placeholder="Nombre completo"       required />
          <input v-model="form.email"     type="email"    placeholder="Correo electrónico"    required />
          <input v-model="form.phone"     type="tel"      placeholder="Teléfono (opcional)"            />
          <input v-model="form.password"  type="password" placeholder="Contraseña (mín. 8 car.)" required />
          <input v-model="form.confirm"   type="password" placeholder="Confirmar contraseña"  required />

          <button type="submit" :disabled="loading">
            {{ loading ? 'Creando cuenta...' : 'Crear cuenta' }}
          </button>
        </form>

        <div class="login-link">
          ¿Ya tienes cuenta?
          <RouterLink to="/login">Inicia sesión</RouterLink>
        </div>
      </template>
    </div>
  </section>
</template>

<style scoped>
.register {
  min-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
  font-family: 'Poppins', sans-serif;
}

.card {
  background: white;
  width: 100%;
  max-width: 420px;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 15px 40px rgba(0,0,0,.1);
}

.card h2    { font-size: 28px; font-weight: 600; text-align: center; }
.subtitle   { text-align: center; color: #666; font-size: 14px; margin: 8px 0 24px; }

.alert-success {
  background: #dcfce7; color: #166534;
  padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 18px;
}
.alert-error {
  background: #fee2e2; color: #991b1b;
  padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 14px;
}

form  { display: flex; flex-direction: column; gap: 14px; }

input {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #ddd;
  font-size: 14px;
  font-family: inherit;
}
input:focus { outline: none; border-color: #f5a623; }

button {
  margin-top: 12px;
  padding: 12px;
  background: #f5a623;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background .2s;
  font-family: inherit;
}
button:hover    { background: #e6951c; }
button:disabled { opacity: .6; cursor: not-allowed; }

.login-link { margin-top: 18px; text-align: center; font-size: 14px; }
.login-link a { color: #f5a623; font-weight: 500; }

@media (max-width: 480px) { .card { padding: 24px; } }
</style>

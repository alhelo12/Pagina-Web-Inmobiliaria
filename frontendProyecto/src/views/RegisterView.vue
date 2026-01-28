<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = ref({
  nombre: '',
  email: '',
  telefono: '',
  password: '',
  confirmPassword: ''
})

const submitRegister = () => {
  // Aquí SOLO frontend
  console.log('Registro cliente:', form.value)

  // Luego el backend validará
  router.push('/login')
}
</script>

<template>
  <section class="register">
    <div class="card">
      <h2>Crear cuenta</h2>
      <p class="subtitle">
        Regístrate para publicar tu propiedad y recibir asesoría
      </p>

      <form @submit.prevent="submitRegister">
        <input v-model="form.nombre" type="text" placeholder="Nombre completo" required />
        <input v-model="form.email" type="email" placeholder="Correo electrónico" required />
        <input v-model="form.telefono" type="tel" placeholder="Teléfono" required />

        <input v-model="form.password" type="password" placeholder="Contraseña" required />
        <input v-model="form.confirmPassword" type="password" placeholder="Confirmar contraseña" required />

        <button type="submit">Crear cuenta</button>
      </form>

      <div class="login-link">
        ¿Ya tienes cuenta?
        <span @click="router.push('/login')">Inicia sesión</span>
      </div>
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

.card h2 {
  font-size: 28px;
  font-weight: 600;
  text-align: center;
}

.subtitle {
  text-align: center;
  color: #666;
  font-size: 14px;
  margin: 8px 0 24px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

input {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #ddd;
  font-size: 14px;
}

input:focus {
  outline: none;
  border-color: #f5a623;
}

button {
  margin-top: 12px;
  padding: 12px;
  background: #f5a623;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

button:hover {
  background: #e6951c;
}

.login-link {
  margin-top: 18px;
  text-align: center;
  font-size: 14px;
}

.login-link span {
  color: #f5a623;
  cursor: pointer;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 480px) {
  .card {
    padding: 24px;
  }
}
</style>

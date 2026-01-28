<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = ref({
  name: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: ''
})

const submitRegister = () => {
  // SOLO FRONTEND (simulación)
  console.log('Registro cliente:', form.value)
  router.push('/cliente/registrar-propiedad')
}
</script>

<template>
  <div class="auth-container">
    <h1>Crear cuenta de propietario</h1>
    <p class="subtitle">
      Registra tus datos para enviar tu propiedad a revisión
    </p>

    <form @submit.prevent="submitRegister">
      <input type="text" placeholder="Nombre completo" v-model="form.name" required />
      <input type="email" placeholder="Correo electrónico" v-model="form.email" required />
      <input type="tel" placeholder="Teléfono" v-model="form.phone" required />
      <input type="password" placeholder="Contraseña" v-model="form.password" required />
      <input type="password" placeholder="Confirmar contraseña" v-model="form.confirmPassword" required />

      <button type="submit">Crear cuenta</button>
    </form>

    <p class="note">
      Tu propiedad será revisada por un asesor antes de publicarse.
    </p>
  </div>
</template>

<style scoped>
.auth-container {
  max-width: 420px;
  margin: 80px auto;
  padding: 30px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0,0,0,.08);
  font-family: 'Poppins', sans-serif;
}

h1 {
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  color: #777;
  margin-bottom: 24px;
}

input {
  width: 100%;
  padding: 12px;
  margin-bottom: 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

button {
  width: 100%;
  padding: 12px;
  background: #f5a623;
  border: none;
  border-radius: 6px;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

button:hover {
  background: #e69a1f;
}

.note {
  margin-top: 16px;
  font-size: 12px;
  color: #666;
  text-align: center;
}
</style>

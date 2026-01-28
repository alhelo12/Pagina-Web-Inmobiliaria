<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goRegister = () => {
  router.push('/registro')
}

const submitLogin = () => {
  console.log('Login enviado')
  // Backend decidirá rol y redirección
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h1>Iniciar sesión</h1>
      <p class="subtitle">
        Acceso para administradores, asesores y clientes registrados
      </p>

      <form @submit.prevent="submitLogin">
        <div class="field">
          <label>Correo electrónico</label>
          <input type="email" placeholder="correo@ejemplo.com" required />
        </div>

        <div class="field">
          <label>Contraseña</label>
          <input type="password" placeholder="••••••••" required />
        </div>

        <button class="login-btn" type="submit">
          Ingresar
        </button>
      </form>

      <div class="divider"></div>

      <p class="register-text">
        ¿Quieres vender o rentar una propiedad?
      </p>

      <button class="register-btn" @click="goRegister">
        Crear cuenta y registrar propiedad
      </button>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: calc(100vh - 80px);
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f7f7f7;
  font-family: 'Poppins', sans-serif;
}

.login-card {
  background: white;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  border-radius: 12px;
  box-shadow: 0 15px 40px rgba(0,0,0,0.08);
}

.login-card h1 {
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 6px;
}

.subtitle {
  font-size: 14px;
  color: #777;
  margin-bottom: 28px;
}

.field {
  margin-bottom: 18px;
}

.field label {
  display: block;
  font-size: 13px;
  margin-bottom: 6px;
  color: #444;
}

.field input {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 14px;
}

.field input:focus {
  outline: none;
  border-color: #f5a623;
}

.login-btn {
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  background: #f5a623;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
}

.login-btn:hover {
  background: #d9941d;
}

.divider {
  height: 1px;
  background: #eee;
  margin: 28px 0 18px;
}

.register-text {
  font-size: 14px;
  color: #333;
  text-align: center;
  margin-bottom: 10px;
}

.register-btn {
  width: 100%;
  padding: 11px;
  background: #2f2f2f;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.register-btn:hover {
  background: #000;
}

@media (max-width: 480px) {
  .login-card {
    padding: 28px 20px;
  }

  .login-card h1 {
    font-size: 22px;
  }
}
</style>

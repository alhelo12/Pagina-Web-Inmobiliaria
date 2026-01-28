<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="navbar">
    <div class="logo">JAKEDA</div>

    <nav class="menu">
      <!-- SOLO estos cambian a RouterLink -->
      <RouterLink to="/">Inicio</RouterLink>
      <RouterLink to="/servicios">Servicios</RouterLink>
      <RouterLink to="/propiedades">Propiedades</RouterLink>
      <RouterLink to="/nosotros">Nosotros</RouterLink>
      <RouterLink to="/contacto">Contacto</RouterLink>

      <!-- 🚫 NO TOQUEN ESTA PARTE PORFAVOR -->
      <a href="/login" class="btn-login">Iniciar sesión</a>
    </nav>
  </header>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 40px;
  background: white;
}

.menu {
  display: flex;
  gap: 22px;
  align-items: center;
}

/* RouterLink se comporta como <a> */
.menu a {
  text-decoration: none;
  color: #222;
  font-weight: 500;
}

.menu a.router-link-active {
  color: #f5a623;
  font-weight: 600;
}

.btn-login {
  padding: 8px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
}
</style>

<template>
  <header class="navbar">
    <div class="logo">JAKEDA</div>

    <nav>
      <a href="#">Inicio</a>
      <a href="#">Servicios</a>
      <a href="#">Propiedades</a>
      <a href="#">Nosotros</a>
      <a href="#">Contacto</a>
    </nav>
  </header>
</template>

<script setup>
</script>

<style scoped>
.navbar {
  height: 70px;
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  box-shadow: 0 2px 10px rgba(0,0,0,.05);
}

.logo {
  font-weight: bold;
  font-size: 50px;
  color: #f5a623;
}

nav a {
  margin-left: 20px;
  font-size: 30px;
  text-decoration: none;
  color: #333;
  font-weight: 500;
}
</style>

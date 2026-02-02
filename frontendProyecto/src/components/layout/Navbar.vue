<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'

const open = ref(false)
const scrolled = ref(false)

const onScroll = () => {
  scrolled.value = window.scrollY > 60
}

onMounted(() => {
  window.addEventListener('scroll', onScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>


<template>
  <header :class="['navbar', { scrolled }]">
    <div class="nav-container">
      <!-- LOGO -->
      <div class="logo">JAKEDA</div>

      <!-- BOTÓN HAMBURGUESA -->
      <button class="hamburger" @click="open = !open">
        <span :class="{ active: open }"></span>
        <span :class="{ active: open }"></span>
        <span :class="{ active: open }"></span>
      </button>

      <!-- MENÚ -->
      <nav :class="['menu', { open }]">
        <RouterLink to="/" @click="open=false">Inicio</RouterLink>
        <RouterLink to="/servicios" @click="open=false">Servicios</RouterLink>
        <RouterLink to="/propiedades" @click="open=false">Propiedades</RouterLink>
        <RouterLink to="/nosotros" @click="open=false">Nosotros</RouterLink>
        <RouterLink to="/contacto" @click="open=false">Contacto</RouterLink>

        <a href="/login" class="btn-login">Iniciar sesión</a>
      </nav>
    </div>
  </header>
</template>


<style scoped>
.navbar {
  position: fixed;
  top: 0;
  width: 100%;
  background: transparent;
  transition: background 0.3s ease, box-shadow 0.3s ease;
  z-index: 1000;
}

/* CUANDO SCROLLEA */
.navbar.scrolled {
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,.08);
}

.nav-container {
  max-width: 1280px;
  margin: auto;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 22px;
  font-weight: 700;
  color: #f59e0b;
}

/* HAMBURGUESA */
.hamburger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
}

.hamburger span {
  width: 25px;
  height: 3px;
  background: #333;
  transition: 0.3s;
}

/* MENÚ DESKTOP */
.menu {
  display: flex;
  gap: 20px;
  align-items: center;
}

.menu a {
  font-weight: 500;
  color: #222;
}

.menu a.router-link-active {
  color: #f59e0b;
}

.btn-login {
  border: 1px solid #ddd;
  padding: 8px 14px;
  border-radius: 20px;
}

/* 🔥 MOBILE */
@media (max-width: 768px) {
  .hamburger {
    display: flex;
  }

  .menu {
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    background: white;
    flex-direction: column;
    gap: 16px;
    padding: 20px;
    transform: translateY(-120%);
    transition: 0.3s;
  }

  .menu.open {
    transform: translateY(0);
  }
}

</style>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()

const open = ref(false)
const scrolled = ref(false)
const dropdown = ref(false)

const onScroll = () => {
  scrolled.value = window.scrollY > 60
}

onMounted(() => window.addEventListener('scroll', onScroll))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <header :class="['navbar', { scrolled }]">
    <div class="nav-container">

      <!-- LOGO -->
      <div class="logo">JAKEDA</div>

      <!-- BOTÓN HAMBURGUESA -->
      <button class="hamburger" @click="open = !open">
        <span></span>
        <span></span>
        <span></span>
      </button>

      <!-- MENÚ -->
      <nav :class="['menu', { open }]">
        <RouterLink to="/" @click="open=false">Inicio</RouterLink>
        <RouterLink to="/servicios" @click="open=false">Servicios</RouterLink>
        <RouterLink to="/propiedades" @click="open=false">Propiedades</RouterLink>
        <RouterLink to="/nosotros" @click="open=false">Nosotros</RouterLink>
        <RouterLink to="/contacto" @click="open=false">Contacto</RouterLink>

        <!-- ===== USUARIO LOGUEADO ===== -->
        <div v-if="auth.isLogged" class="user-menu">
          <button class="btn-login" @click="dropdown = !dropdown">
            Mi cuenta ▾
          </button>

          <div v-if="dropdown" class="dropdown">

            <!-- CLIENTE -->
            <template v-if="auth.role === 'client'">
              <RouterLink to="/favoritos">Mis favoritos</RouterLink>
            </template>

            <!-- ASESOR -->
            <template v-else-if="auth.role === 'advisor'">
              <RouterLink to="/advisor/panel">Panel de asesor</RouterLink>
            </template>

            <!-- ADMIN -->
            <template v-else-if="auth.role === 'admin'">
              <RouterLink to="/admin/propiedades">Propiedades</RouterLink>
              <RouterLink to="/admin/usuarios">Usuarios</RouterLink>
            </template>

            <!-- LOGOUT -->
            <button @click="auth.logout()">Cerrar sesión</button>
          </div>
        </div>

        <!-- ===== NO LOGUEADO ===== -->
        <RouterLink v-else to="/login" class="btn-login" @click="open=false">
          Iniciar sesión
        </RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  width: 100%;
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,.08);
  z-index: 1000;
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
  text-decoration: none;
}

.menu a.router-link-active {
  color: #f59e0b;
}

.btn-login {
  border: 1px solid #ddd;
  padding: 8px 14px;
  border-radius: 20px;
  background: white;
  cursor: pointer;
}

/* ===== USER DROPDOWN ===== */
.user-menu {
  position: relative;
}

.dropdown {
  position: absolute;
  right: 0;
  top: 110%;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  min-width: 180px;
  overflow: hidden;
  z-index: 2000;
}

.dropdown a,
.dropdown button {
  padding: 12px 16px;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.dropdown a:hover,
.dropdown button:hover {
  background: #f3f4f6;
}

/* ===== MOBILE ===== */
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

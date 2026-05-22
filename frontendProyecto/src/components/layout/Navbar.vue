<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import NotificationBell from '@/components/shared/NotificationBell.vue'

const auth = useAuthStore()
const router = useRouter()

const mobileOpen = ref(false)
const scrolled = ref(false)
const dropdownOpen = ref(false)
const dropdownRef = ref(null)

const dashboardPath = computed(() => {
  if (auth.role === 'admin') return '/admin/dashboard'
  if (auth.role === 'advisor') return '/advisor/panel'
  if (auth.role === 'client') return '/cliente/dashboard'
  return '/crear-propiedad'
})

const onScroll = () => {
  scrolled.value = window.scrollY > 34
}

const onOutsideClick = (event) => {
  if (!dropdownRef.value) return
  if (!dropdownRef.value.contains(event.target)) {
    dropdownOpen.value = false
  }
}

const closeAll = () => {
  mobileOpen.value = false
  dropdownOpen.value = false
}

const goDashboard = () => {
  closeAll()
  router.push(dashboardPath.value)
}

const logout = () => {
  auth.logout()
  closeAll()
  router.push('/login')
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll)
  document.addEventListener('click', onOutsideClick)
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('click', onOutsideClick)
})
</script>

<template>
  <header :class="['navbar', { scrolled }]">
    <div class="nav-container">
      <RouterLink to="/" class="logo" @click="closeAll">
        <span class="logo-mark">J</span>
        <span class="logo-text">JAKEDA</span>
      </RouterLink>

      <button
        class="hamburger"
        type="button"
        aria-label="Abrir menu"
        @click="mobileOpen = !mobileOpen"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <nav :class="['menu', { open: mobileOpen }]">
        <RouterLink to="/" @click="closeAll">Inicio</RouterLink>
        <RouterLink to="/servicios" @click="closeAll">Servicios</RouterLink>
        <RouterLink to="/propiedades" @click="closeAll">Propiedades</RouterLink>
        <RouterLink to="/nosotros" @click="closeAll">Nosotros</RouterLink>
        <RouterLink to="/contacto" @click="closeAll">Contacto</RouterLink>

        <div v-if="auth.isLogged" class="account-wrapper">
          <NotificationBell v-if="auth.role === 'client' || auth.role === 'advisor'" />

          <div ref="dropdownRef" class="account">
            <button class="btn-account" type="button" @click="dropdownOpen = !dropdownOpen">
              Mi cuenta
              <span class="chevron" :class="{ up: dropdownOpen }">▾</span>
            </button>

            <transition name="dropdown">
              <div v-if="dropdownOpen" class="dropdown">
                <button type="button" @click="goDashboard">Dashboard</button>
                <button v-if="auth.role === 'client'" type="button" @click="() => { router.push('/favoritos'); closeAll() }">Mis favoritos</button>
                <button type="button" @click="logout">Cerrar sesión</button>
              </div>
            </transition>
          </div>
        </div>

        <RouterLink
          v-else
          to="/login"
          class="btn-login"
          @click="closeAll"
        >
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
  left: 0;
  width: 100%;
  height: 60px;
  z-index: 1000;
  background: rgba(7, 24, 44, 0.46);
  backdrop-filter: blur(8px);
  transition: background 0.3s ease, box-shadow 0.3s ease;
}

.navbar.scrolled {
  background: rgba(7, 24, 44, 0.96);
  box-shadow: 0 16px 36px rgba(4, 11, 23, 0.25);
}

.nav-container {
  max-width: 1240px;
  height: 100%;
  margin: 0 auto;
  padding: 0 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #ffffff;
  text-decoration: none;
}

.logo-mark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #d4a34a, #f0c36f);
  color: #091d39;
  font-weight: 800;
}

.logo-text {
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  letter-spacing: 0.08em;
  font-weight: 700;
}

.menu {
  display: flex;
  align-items: center;
  gap: 22px;
}

.menu a {
  position: relative;
  color: rgba(255, 255, 255, 0.92);
  text-decoration: none;
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.3s ease;
}

.menu a::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -6px;
  width: 0;
  height: 2px;
  background: #dcb066;
  transition: width 0.3s ease;
}

.menu a:hover,
.menu a.router-link-active {
  color: #f7d9a6;
}

.menu a:hover::after,
.menu a.router-link-active::after {
  width: 100%;
}

.btn-login,
.btn-account {
  border: 1px solid rgba(220, 176, 102, 0.75);
  border-radius: 999px;
  padding: 10px 16px;
  color: #fff;
  background: linear-gradient(120deg, rgba(220, 176, 102, 0.18), rgba(220, 176, 102, 0.3));
  font-family: 'Poppins', sans-serif;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.btn-login::after {
  display: none;
}

.btn-login:hover,
.btn-account:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(220, 176, 102, 0.24);
  background: linear-gradient(120deg, #dcb066, #c6953b);
  color: #0a1e3b;
}

.account {
  position: relative;
}

.account-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chevron {
  margin-left: 8px;
  display: inline-block;
  transition: transform 0.3s ease;
}

.chevron.up {
  transform: rotate(180deg);
}

.dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  min-width: 180px;
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 20px 35px rgba(15, 23, 42, 0.16);
  border: 1px solid #e7ebf3;
  padding: 8px;
  display: grid;
  gap: 6px;
}

.dropdown button {
  border: none;
  background: transparent;
  border-radius: 10px;
  padding: 10px 12px;
  text-align: left;
  color: #1e293b;
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s ease, color 0.3s ease;
}

.dropdown button:hover {
  background: #f2f6ff;
  color: #1d4ed8;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.hamburger {
  display: none;
  border: none;
  background: transparent;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
}

.hamburger span {
  width: 24px;
  height: 2px;
  background: #fff;
  border-radius: 999px;
}

@media (max-width: 900px) {
  .nav-container {
    padding: 0 16px;
  }

  .hamburger {
    display: flex;
  }

  .menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #07182c;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 16px 30px rgba(0, 0, 0, 0.22);
    padding: 14px 18px 18px;
    display: grid;
    gap: 12px;
    transform: translateY(-120%);
    opacity: 0;
    pointer-events: none;
    transition: transform 0.3s ease, opacity 0.3s ease;
  }

  .menu.open {
    transform: translateY(0);
    opacity: 1;
    pointer-events: auto;
  }

  .menu a::after {
    bottom: -3px;
  }

  .btn-login,
  .btn-account {
    justify-self: start;
  }

  .dropdown {
    position: static;
    margin-top: 8px;
  }
}
</style>

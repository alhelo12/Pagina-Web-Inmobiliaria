<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import NotificationBell from '@/components/shared/NotificationBell.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const mobileOpen = ref(false)
const scrolled = ref(false)
// Transparent white-text nav only over the home hero; solid ivory everywhere else
const solid = computed(() => scrolled.value || route.path !== '/')
watch(() => route.path, () => closeAll())
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
  window.addEventListener('scroll', onScroll, { passive: true })
  document.addEventListener('click', onOutsideClick)
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('click', onOutsideClick)
})
</script>

<template>
  <header :class="['navbar', { scrolled: solid }]">
    <div class="nav-container">
      <RouterLink to="/" class="logo" @click="closeAll">
        <span class="logo-text">JAKEDA<small>REAL ESTATE</small></span>
      </RouterLink>

      <button
        class="hamburger"
        type="button"
        :aria-expanded="mobileOpen"
        aria-controls="main-menu"
        :aria-label="mobileOpen ? 'Cerrar menú' : 'Abrir menú'"
        @click="mobileOpen = !mobileOpen"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <nav id="main-menu" :class="['menu', { open: mobileOpen }]">
        <RouterLink to="/" @click="closeAll">Inicio</RouterLink>
        <RouterLink to="/servicios" @click="closeAll">Servicios</RouterLink>
        <RouterLink to="/propiedades" @click="closeAll">Propiedades</RouterLink>
        <RouterLink to="/nosotros" @click="closeAll">Nosotros</RouterLink>
        <RouterLink to="/contacto" @click="closeAll">Contacto</RouterLink>

        <div v-if="auth.isLogged" class="account-wrapper">
          <NotificationBell v-if="auth.role === 'client' || auth.role === 'advisor'" />

          <div ref="dropdownRef" class="account">
            <button
              class="btn-account"
              type="button"
              aria-haspopup="true"
              :aria-expanded="dropdownOpen"
              @click="dropdownOpen = !dropdownOpen"
            >
              Mi cuenta
              <span class="chevron" :class="{ up: dropdownOpen }">▾</span>
            </button>

            <transition name="dropdown">
              <div v-if="dropdownOpen" class="dropdown">
                <button type="button" @click="goDashboard">Dashboard</button>
                <button v-if="auth.role === 'client'" type="button" @click="() => { router.push('/cliente/favoritos'); closeAll() }">Mis favoritos</button>
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
  height: 72px;
  z-index: var(--z-nav);
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.18);
  transition: background 0.3s ease, border-color 0.3s ease;
}

.navbar.scrolled {
  background: rgba(243, 238, 228, 0.97);
  border-bottom: 1px solid var(--color-line);
  backdrop-filter: blur(10px);
}

.nav-container {
  max-width: 1440px;
  height: 100%;
  margin: 0 auto;
  padding: 0 clamp(16px, 3vw, 40px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.logo {
  display: inline-flex;
  align-items: center;
  color: #fff;
  text-decoration: none;
  transition: color 0.3s ease;
}
.navbar.scrolled .logo { color: var(--color-ink); }

.logo-text {
  font-size: 22px;
  letter-spacing: 0.28em;
  font-weight: 600;
  line-height: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.logo-text small {
  font-size: 11px;
  letter-spacing: 0.34em;
  font-weight: 500;
  opacity: 0.8;
}

.menu {
  display: flex;
  align-items: center;
  gap: 28px;
}

.menu a {
  position: relative;
  color: rgba(255, 255, 255, 0.92);
  text-decoration: none;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-weight: 500;
  transition: color 0.3s ease;
}
.navbar.scrolled .menu a { color: var(--color-ink); }

.menu a::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -6px;
  width: 100%;
  height: 1px;
  background: var(--color-brass);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.menu a:hover,
.menu a.router-link-active {
  color: var(--color-brass);
}
.navbar.scrolled .menu a:hover,
.navbar.scrolled .menu a.router-link-active { color: var(--color-brass-deep); }

.menu a:hover::after,
.menu a.router-link-active::after {
  transform: scaleX(1);
}

.btn-login,
.btn-account {
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 0;
  padding: 11px 22px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: transparent;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.25s ease, color 0.25s ease, border-color 0.25s ease;
  text-decoration: none;
}
.navbar.scrolled .btn-login,
.navbar.scrolled .btn-account {
  border-color: var(--color-petrol);
  color: var(--color-petrol);
}
.navbar.scrolled :deep(.bell-btn) { color: var(--color-petrol); }

.btn-login::after {
  display: none;
}

.btn-login:hover,
.btn-account:hover {
  background: var(--color-brass);
  border-color: var(--color-brass);
  color: #fff;
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
  background: var(--color-card);
  border-radius: 12px;
  box-shadow: 0 20px 35px rgba(15, 23, 42, 0.16);
  border: 1px solid var(--color-line);
  padding: 8px;
  display: grid;
  gap: 6px;
}

.dropdown button {
  border: none;
  background: transparent;
  border-radius: 12px;
  padding: 10px 12px;
  min-height: 44px;
  display: flex;
  align-items: center;
  text-align: left;
  color: var(--color-ink);
  font-family: var(--sans);
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s ease, color 0.3s ease;
}

.dropdown button:hover {
  background: rgba(185,148,95,.14);
  color: var(--color-ink);
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
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  width: 44px;
  height: 44px;
  min-width: 44px;
  min-height: 44px;
  padding: 10px;
}

.hamburger span {
  width: 24px;
  height: 2px;
  background: #fff;
  border-radius: 0;
}
.navbar.scrolled .hamburger span { background: var(--color-ink); }

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
    background: var(--color-ink);
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
  .navbar.scrolled .menu.open :deep(.bell-btn) { color: rgba(255, 255, 255, 0.92); }

  .menu a {
    min-height: 44px;
    display: inline-flex;
    align-items: center;
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

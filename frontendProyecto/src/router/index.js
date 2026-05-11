import { createRouter, createWebHistory } from 'vue-router'
import HomeView           from '../views/HomeView.vue'
import RegisterView       from '../views/RegisterView.vue'
import LoginView          from '../views/LoginView.vue'
import PropertiesView     from '../views/PropertiesView.vue'
import PropertyDetailView from '../views/PropertyDetailView.vue'
import NosotrosView       from '../views/client/NosotrosView.vue'
import ContactosView      from '../views/client/ContactosView.vue'
import ServicesView       from '../views/client/ServicesView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [

    // ── RUTAS PÚBLICAS ───────────────────────────────────────────────────────
    { path: '/',            name: 'home',            component: HomeView },
    { path: '/propiedades', name: 'properties',      component: PropertiesView },
    { path: '/propiedades/:id', name: 'property-detail', component: PropertyDetailView },
    { path: '/nosotros',    name: 'nosotros',        component: NosotrosView },
    { path: '/contacto',    name: 'contacto',        component: ContactosView },
    { path: '/servicios',   name: 'servicios',       component: ServicesView },
    { path: '/login',       name: 'login',           component: LoginView },
    { path: '/registro',    name: 'register',        component: RegisterView },

    // ── RUTAS DE CLIENTE ─────────────────────────────────────────────────────
    {
      path: '/cliente',
      component: () => import('@/views/client/ClientLayout.vue'),
      meta: { requiresAuth: true, role: 'client' },
      children: [
        { path: '', redirect: '/cliente/dashboard' },
        { path: 'dashboard', component: () => import('@/views/client/ClientDashboard.vue') },
        { path: 'mis-propiedades', component: () => import('@/views/client/MyPropertiesView.vue') },
        { path: 'favoritos', component: () => import('@/views/client/FavoritesView.vue') },
        { path: 'publicar', component: () => import('@/views/client/CreatePropertyView.vue') },
        { path: 'notificaciones', component: () => import('@/views/client/NotificationsView.vue') },
        { path: 'citas', component: () => import('@/views/client/AppointmentsView.vue') },
        { path: 'mensajes', component: () => import('@/views/client/ClientChatView.vue') },
        { path: 'perfil', component: () => import('@/views/client/ProfileView.vue') }
      ]
    },
    {
      path: '/crear-propiedad',
      name: 'create-property',
      component: () => import('@/views/client/CreatePropertyView.vue'),
      meta: { requiresAuth: true, role: ['client', 'admin', 'advisor'] }
    },
    {
      path: '/favoritos',
      name: 'favoritos',
      component: () => import('@/views/client/FavoritesView.vue'),
      meta: { requiresAuth: true, role: 'client' }
    },

    // ── RUTAS DE ASESOR ──────────────────────────────────────────────────────
    {
      path: '/advisor',
      component: () => import('@/views/advisor/AdvisorLayout.vue'),
      meta: { requiresAuth: true, role: 'advisor' },
      children: [
        { path: '', redirect: '/advisor/dashboard' },
        { path: 'dashboard', component: () => import('@/views/advisor/AdvisorDashboard.vue') },
        { path: 'panel', component: () => import('@/views/advisor/AdvisorPanel.vue') },
        { path: 'clientes', component: () => import('@/views/advisor/AdvisorClientsView.vue') },
        { path: 'citas', component: () => import('@/views/advisor/AdvisorAppointmentsView.vue') },
        { path: 'mensajes', component: () => import('@/views/advisor/AdvisorChatView.vue') },
        { path: 'notificaciones', component: () => import('@/views/advisor/AdvisorNotificationsView.vue') },
        { path: 'perfil', component: () => import('@/views/advisor/AdvisorProfileView.vue') }
      ]
    },

    // ── RUTAS DE ADMIN ───────────────────────────────────────────────────────
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        { path: '',            redirect: '/admin/dashboard' },
        { path: 'dashboard',   component: () => import('@/views/admin/DashboardView.vue') },
        { path: 'propiedades', component: () => import('@/views/admin/PropertiesAdminView.vue') },
        { path: 'propiedades/:id/editar', component: () => import('@/views/client/CreatePropertyView.vue') },
        { path: 'usuarios',    component: () => import('@/views/admin/UsersView.vue') },
        { path: 'nuevapropiedad', component: () => import('@/views/client/CreatePropertyView.vue') }
      ]
    }
  ]
})

// ── GUARD DE NAVEGACIÓN ──────────────────────────────────────────────────────
import { useAuthStore } from '@/stores/authStore'

function isTokenExpired(token) {
  try {
    const base64  = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    const { exp } = JSON.parse(atob(base64))
    return exp * 1000 < Date.now()
  } catch {
    return true
  }
}

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth) {
    if (!auth.isLogged || !auth.token || isTokenExpired(auth.token)) {
      auth.logout()
      return next('/login')
    }
  }

  // Verifica que el rol coincida (acepta string o array de roles)
  if (to.meta.role) {
    const allowed = Array.isArray(to.meta.role) ? to.meta.role : [to.meta.role]
    if (!allowed.includes(auth.role)) {
      return next('/')
    }
  }

  next()
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'
import PropertiesView from '../views/PropertiesView.vue'
import PropertyDetailView from '../views/PropertyDetailView.vue'
import NosotrosView from '../views/client/NosotrosView.vue'
import ContactosView from '../views/client/ContactosView.vue'
import ServicesView from '../views/client/ServicesView.vue'



const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },

    { path: '/propiedades', name: 'properties', component: PropertiesView },

    // 🔥 DETALLE DE PROPIEDAD
    {
      path: '/propiedades/:id',
      name: 'property-detail',
      component: PropertyDetailView
    },
    {
      path: '/nosotros',
      name: 'nosotros',
      component: NosotrosView
    },
    {
      path: '/contacto',
      name: 'contacto',
      component: ContactosView
    },
        {
      path: '/servicios',
      name: 'servicios',
      component: ServicesView
    },
    {
  path: '/crear-propiedad',
  name: 'create-property',
  component: () => import('@/views/client/CreatePropertyView.vue')
},
{
  path: '/favoritos',
  name: 'favoritos',
  component: () => import('@/views/client/FavoritesView.vue'),
  meta: { requiresAuth: true, role: 'client' }
},
{
  path: '/admin',
  component: () => import('@/views/admin/AdminLayout.vue'),
  meta: { requiresAuth: true, role: 'admin' },
  children: [
    {
      path: '',
      redirect: '/admin/propiedades'
    },
    {
      path: 'propiedades',
      component: () => import('@/views/admin/PropertiesAdminView.vue')
    },
    {
      path: 'usuarios',
      component: () => import('@/views/admin/UsersView.vue')
    }
  ]
},

// DASHBOARD (tarjetas)
{
  path: '/advisor',
  component: () => import('@/views/advisor/AdvisorLayout.vue'),
  children: [
    {
      path: 'panel',
      component: () => import('@/views/advisor/AdvisorPanel.vue')
    }
  ]
}
,

    { path: '/login', name: 'login', component: LoginView },
    { path: '/registro', name: 'register', component: RegisterView }
  ]
})

import { useAuthStore } from '@/stores/authStore'

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  // requiere login
  if (to.meta.requiresAuth && !auth.isLogged) {
    return next('/login')
  }

  // requiere rol específico
  if (to.meta.role && auth.role !== to.meta.role) {
    return next('/')
  }

  next()
})


export default router

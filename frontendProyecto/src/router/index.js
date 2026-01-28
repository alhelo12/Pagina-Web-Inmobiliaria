import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'
import PropertiesView from '../views/PropertiesView.vue'
import PropertyDetailView from '../views/PropertyDetailView.vue'
import NosotrosView from '../views/client/NosotrosView.vue'

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
}
,

    { path: '/login', name: 'login', component: LoginView },
    { path: '/registro', name: 'register', component: RegisterView }
  ]
})

export default router

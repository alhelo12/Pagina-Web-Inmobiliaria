<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { usePropertyStore } from '@/stores/propertyStore'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { storeToRefs } from 'pinia'
import ClientDashboardHeader from '@/components/client/dashboard/ClientDashboardHeader.vue'
import ClientMetricCards from '@/components/client/dashboard/ClientMetricCards.vue'
import ClientRecentList from '@/components/client/dashboard/ClientRecentList.vue'
import ClientFavoritesPreview from '@/components/client/dashboard/ClientFavoritesPreview.vue'
import ClientActivityPanel from '@/components/client/dashboard/ClientActivityPanel.vue'

const auth = useAuthStore()
const router = useRouter()
const favStore = useFavoritesStore()
const propertyStore = usePropertyStore()
const notifStore = useNotificationsStore()

const { favorites } = storeToRefs(favStore)
const { properties, loading } = storeToRefs(propertyStore)
const { unreadCount } = storeToRefs(notifStore)

const loadingDashboard = ref(true)
const error = ref('')

const myProperties = computed(() => {
  return properties.value.filter(p => p.owner_id === auth.userId).slice(0, 5)
})

const pendingCount = computed(() => {
  return properties.value.filter(p => p.owner_id === auth.userId && p.status === 'pending').length
})

const metrics = computed(() => ({
  favoritesCount: favorites.value.length,
  myPropertiesCount: myProperties.value.length,
  pendingCount: pendingCount.value,
  exploredCount: 0,
  unreadNotifications: unreadCount.value
}))

onMounted(async () => {
  loadingDashboard.value = true
  error.value = ''
  try {
    await Promise.all([
      favStore.fetchFavorites(),
      propertyStore.fetchProperties(),
      notifStore.fetchUnreadCount()
    ])
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al cargar el dashboard'
  } finally {
    loadingDashboard.value = false
  }
})
</script>

<template>
  <section class="dashboard">
    <ClientDashboardHeader
      eyebrow="Dashboard"
      title="Mi Panel"
      :show-add="true"
      add-label="Nueva propiedad"
      :profile-name="auth.userEmail?.split('@')?.[0] || 'Cliente'"
      :profile-email="auth.userEmail || ''"
      @add="router.push('/cliente/publicar')"
    />

    <div v-if="loadingDashboard" class="state">Cargando resumen...</div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <template v-else>
      <ClientMetricCards :metrics="metrics" />

      <div class="overview-grid">
        <ClientActivityPanel />

        <ClientFavoritesPreview :favorites="favorites" />

        <ClientRecentList
          title="Mis Publicaciones"
          :items="myProperties"
          empty-text="No has publicado propiedades."
        />
      </div>

      <div class="actions-grid">
        <RouterLink to="/propiedades" class="action-btn">
          <span class="icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </span>
          <span>Explorar Propiedades</span>
        </RouterLink>

        <RouterLink to="/cliente/favoritos" class="action-btn">
          <span class="icon heart">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          </span>
          <span>Ver Favoritos</span>
        </RouterLink>

        <RouterLink to="/cliente/publicar" class="action-btn">
          <span class="icon add">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </span>
          <span>Publicar Propiedad</span>
        </RouterLink>

        <RouterLink to="/contacto" class="action-btn">
          <span class="icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
          </span>
          <span>Contactar</span>
        </RouterLink>
      </div>
    </template>
  </section>
</template>

<style scoped>
.dashboard { display: grid; gap: 16px; }
.overview-grid { display: grid; gap: 14px; grid-template-columns: 1fr 1fr 1fr; }
.state { padding: 18px; color: var(--color-muted); background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; }
.error-msg { color: #991b1b; }
.actions-grid { display: grid; gap: 10px; grid-template-columns: repeat(4, 1fr); margin-top: 14px; }
.action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid var(--color-line);
  background: var(--color-card);
  color: var(--color-navy);
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  transition: .2s ease;
}
.action-btn:hover { border-color: var(--color-gold); background: #fdfcf8; }
.action-btn .icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(16, 46, 79, .1);
  color: var(--color-navy-2);
  display: grid;
  place-items: center;
}
.action-btn .icon.heart { background: rgba(220, 38, 38, .1); color: #dc2626; }
.action-btn .icon.add { background: rgba(34, 197, 94, .1); color: #22c55e; }
@media (max-width: 1050px) {
  .overview-grid { grid-template-columns: 1fr 1fr; }
  .actions-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 700px) {
  .overview-grid { grid-template-columns: 1fr; }
  .actions-grid { grid-template-columns: 1fr; }
}
</style>
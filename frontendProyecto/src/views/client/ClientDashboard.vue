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
import RelationshipPanel from '@/components/client/RelationshipPanel.vue'

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
  const uid = Number(auth.userId)
  return properties.value.filter(p => p.submitted_by_user_id === uid).slice(0, 5)
})

const pendingCount = computed(() => {
  const uid = Number(auth.userId)
  return properties.value.filter(p => p.submitted_by_user_id === uid && p.status === 'pending').length
})

const metrics = computed(() => ({
  favoritesCount: favorites.value.length,
  myPropertiesCount: myProperties.value.length,
  pendingCount: pendingCount.value,
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

        <RelationshipPanel :advisor="null" :stats="{ appointments: 0, messages: 0, properties: myProperties.length }" />

        <ClientRecentList
          title="Mis Publicaciones"
          :items="myProperties"
          empty-text="No has publicado propiedades."
        />
      </div>

      <div class="actions-grid">
        <RouterLink to="/cliente/publicar" class="action-btn">
          <span class="icon add">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </span>
          <span>Nueva Propiedad</span>
        </RouterLink>

        <RouterLink to="/cliente/mis-propiedades" class="action-btn">
          <span class="icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          </span>
          <span>Mis Propiedades</span>
        </RouterLink>

        <RouterLink to="/cliente/favoritos" class="action-btn">
          <span class="icon heart">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          </span>
          <span>Favoritos</span>
        </RouterLink>

        <RouterLink to="/cliente/citas" class="action-btn">
          <span class="icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          </span>
          <span>Citas</span>
        </RouterLink>
      </div>
    </template>
  </section>
</template>

<style scoped>
.dashboard { display: grid; gap: 16px; }
.overview-grid { display: grid; gap: 14px; grid-template-columns: 1fr 1fr 1fr 1fr; }
.state { padding: 18px; color: var(--color-muted); background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; }
.error-msg { color: #991b1b; }
.actions-grid { display: grid; gap: 10px; grid-template-columns: repeat(3, 1fr); margin-top: 14px; }
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
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { usePropertyStore } from '@/stores/propertyStore'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { useAppointmentsStore } from '@/stores/appointmentsStore'
import { storeToRefs } from 'pinia'
import ClientDashboardHeader from '@/components/client/dashboard/ClientDashboardHeader.vue'
import ClientActivityPanel from '@/components/client/dashboard/ClientActivityPanel.vue'
import ClientFavoritesPreview from '@/components/client/dashboard/ClientFavoritesPreview.vue'
import RelationshipPanel from '@/components/client/RelationshipPanel.vue'
import ClientRecentList from '@/components/client/dashboard/ClientRecentList.vue'
import Breadcrumb from '@/components/shared/Breadcrumb.vue'

const auth = useAuthStore()
const router = useRouter()
const favStore = useFavoritesStore()
const propertyStore = usePropertyStore()
const notifStore = useNotificationsStore()
const apptStore = useAppointmentsStore()

const { favorites } = storeToRefs(favStore)
const { properties } = storeToRefs(propertyStore)
const { unreadCount } = storeToRefs(notifStore)
const { upcomingAppointments } = storeToRefs(apptStore)

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

onMounted(async () => {
  loadingDashboard.value = true
  error.value = ''
  try {
    await Promise.all([
      favStore.fetchFavorites(),
      propertyStore.fetchProperties(),
      notifStore.fetchUnreadCount(),
      apptStore.fetchUpcoming(7)
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
      @add="router.push('/cliente/publicar')"
    />

    <Breadcrumb :crumbs="[{ label: 'Dashboard', path: '/cliente/dashboard' }]" />

    <div v-if="loadingDashboard" class="state">Cargando resumen...</div>
    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <template v-else>
      <div class="overview-grid">
        <div class="grid-area-activity">
          <ClientActivityPanel />
        </div>

        <div class="grid-area-favorites">
          <ClientFavoritesPreview :favorites="favorites" />
        </div>

        <div class="grid-area-relationship">
          <RelationshipPanel :advisor="null" :stats="{
            appointments: upcomingAppointments,
            properties: myProperties.length,
            pending: pendingCount
          }" />
        </div>

        <div class="grid-area-publications">
          <ClientRecentList
            title="Mis Publicaciones"
            :items="myProperties"
            empty-text="No has publicado propiedades."
          />
        </div>
      </div>

      <div class="actions-grid">
        <RouterLink to="/cliente/mis-propiedades" class="action-btn">
          <span class="icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          </span>
          <span>Mis Propiedades</span>
          <span v-if="myProperties.length" class="action-count">{{ myProperties.length }}</span>
        </RouterLink>

        <RouterLink to="/cliente/favoritos" class="action-btn">
          <span class="icon heart">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          </span>
          <span>Favoritos</span>
          <span v-if="favorites.length" class="action-count">{{ favorites.length }}</span>
        </RouterLink>

        <RouterLink to="/cliente/citas" class="action-btn">
          <span class="icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          </span>
          <span>Citas</span>
          <span v-if="upcomingAppointments" class="action-count">{{ upcomingAppointments }}</span>
        </RouterLink>
      </div>
    </template>
  </section>
</template>

<style scoped>
.dashboard { display: grid; gap: 20px; }

.overview-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-areas:
    "activity favorites"
    "activity relationship"
    "publications publications";
  gap: 16px;
}

.grid-area-activity { grid-area: activity; }
.grid-area-favorites { grid-area: favorites; }
.grid-area-relationship { grid-area: relationship; }
.grid-area-publications { grid-area: publications; }

.state { padding: 18px; color: var(--color-muted); background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; }
.error-msg { color: #991b1b; }

.actions-grid { display: grid; gap: 10px; grid-template-columns: repeat(3, 1fr); }
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
.action-btn span:first-of-type { margin-right: auto; }
.action-btn:hover { border-color: var(--color-gold); background: #fdfcf8; }
.action-btn .icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(16, 46, 79, .1);
  color: var(--color-navy-2);
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.action-btn .icon.heart { background: rgba(220, 38, 38, .1); color: #dc2626; }
.action-count {
  background: var(--color-gold);
  color: var(--color-navy);
  font-size: 11px;
  font-weight: 800;
  min-width: 20px;
  height: 20px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  flex-shrink: 0;
}

@media (max-width: 1200px) {
  .overview-grid { grid-template-columns: 1fr 1fr; }
  .grid-area-activity { grid-area: auto; }
  .overview-grid { grid-template-areas: none; grid-template-columns: 1fr 1fr; }
}
@media (max-width: 900px) {
  .overview-grid { grid-template-columns: 1fr; grid-template-areas: none; }
  .actions-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .actions-grid { grid-template-columns: 1fr; }
}
</style>
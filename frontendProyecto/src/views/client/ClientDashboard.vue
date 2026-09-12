<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { usePropertyStore } from '@/stores/propertyStore'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { useAppointmentsStore } from '@/stores/appointmentsStore'
import { storeToRefs } from 'pinia'
import DashboardHeader from '@/components/shared/dashboard/DashboardHeader.vue'
import ActivityFeed from '@/components/shared/dashboard/ActivityFeed.vue'
import RecentList from '@/components/shared/dashboard/RecentList.vue'
import ClientFavoritesPreview from '@/components/client/dashboard/ClientFavoritesPreview.vue'
import RelationshipPanel from '@/components/client/RelationshipPanel.vue'
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

const activityItems = computed(() => {
  return (notifStore.notifications || []).map(n => ({
    id: n.id,
    title: n.title,
    message: n.message,
    timestamp: n.created_at,
    unread: !n.is_read,
    property_id: n.property_id,
    type: n.type
  }))
})

const typeIcons = {
  advisor_assigned: 'user', approved: 'check', rejected: 'x-circle',
  sold: 'home', property_updated: 'pencil'
}

const handleActivityClick = async (item) => {
  if (item.unread) {
    await notifStore.markAsRead(item.id)
  }
  if (item.property_id) {
    router.push(`/propiedades/${item.property_id}`)
  }
}

onMounted(async () => {
  loadingDashboard.value = true
  error.value = ''
  try {
    await Promise.all([
      favStore.fetchFavorites(),
      propertyStore.fetch(),
      notifStore.fetchUnreadCount(),
      notifStore.fetchNotifications({ limit: 10 }),
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
    <DashboardHeader
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
          <ActivityFeed
            subtitle="Notificaciones"
            title="Actividad Reciente"
            :items="activityItems"
            :loading="notifStore.loading"
            empty-text="No tienes actividad reciente"
            @item-click="handleActivityClick"
          >
            <template #badge>
              <span v-if="unreadCount > 0" class="unread-badge">{{ unreadCount }} nuevas</span>
            </template>
            <template #footer>
              <RouterLink to="/cliente/notificaciones" class="view-all">Ver todas las notificaciones</RouterLink>
            </template>
          </ActivityFeed>
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
          <RecentList
            subtitle="Publicaciones"
            title="Mis Publicaciones"
            :items="myProperties"
            :show-price="true"
            :show-status="false"
            :item-route="(item) => `/propiedades/${item.id}`"
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
.dashboard { display: grid; gap: 20px; max-width: 1400px; width: 100%; }

.overview-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-areas:
    "activity favorites"
    "activity relationship"
    "publications publications";
  gap: 16px;
}
.overview-grid > * { min-width: 0; }

.grid-area-activity { grid-area: activity; }
.grid-area-favorites { grid-area: favorites; }
.grid-area-relationship { grid-area: relationship; }
.grid-area-publications { grid-area: publications; }

/* JAKEDA: thin-rule rows inside shared cards */
.dashboard :deep(.feed-item),
.dashboard :deep(.recent-row),
.dashboard :deep(.fav-item) {
  background: transparent;
  border: none;
  border-bottom: 1px solid #ece5d3;
  border-radius: 0;
  padding: 12px 4px;
}
.dashboard :deep(.feed-item:last-child),
.dashboard :deep(.recent-row:last-child),
.dashboard :deep(.fav-item:last-child) { border-bottom: none; }
.dashboard :deep(.feed-item.unread) { background: #faf5e9; }
.dashboard :deep(.feed-head h3),
.dashboard :deep(.recent-head h3),
.dashboard :deep(.card-head h3) { font-family: var(--serif); font-weight: 700; }

/* JAKEDA: large serif numerals */
.dashboard :deep(.stat-value) { font-family: var(--serif); font-size: 28px; font-weight: 700; color: #102d2d; }

/* JAKEDA: status as text, not pills */
.dashboard :deep(.recent-badge) { background: transparent !important; padding: 0; border-radius: 0; font-size: 11px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.dashboard :deep(.recent-badge.pending) { color: #8a5c00; }
.dashboard :deep(.recent-badge.approved) { color: #166534; }
.dashboard :deep(.recent-badge.rejected) { color: #991b1b; }
.dashboard :deep(.recent-badge.sold) { color: #1a3f3f; }

.state { padding: 18px; color: var(--color-muted); background: #fff; border: 1px solid var(--color-line); border-radius: 12px; }
.error-msg { color: #991b1b; }

.actions-grid { display: grid; gap: 10px; grid-template-columns: repeat(3, 1fr); }
.action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--color-line);
  background: #fff;
  color: #102d2d;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  transition: border-color .2s ease;
}
.action-btn span:first-of-type { margin-right: auto; }
.action-btn:hover { border-color: var(--color-gold); background: #fff; }
.action-btn .icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(16, 45, 45, .07);
  color: #1a3f3f;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.action-btn .icon.heart { background: rgba(201, 164, 92, .16); color: #7a5c1e; }
.action-count {
  background: var(--color-gold);
  color: #102d2d;
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
.unread-badge {
  background: rgba(201, 164, 92, .18);
  color: #7a5c1e;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 999px;
}
.view-all { color: #102d2d; font-size: 13px; font-weight: 600; text-decoration: none; }
.view-all:hover { color: var(--color-gold); }

@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      "activity favorites"
      "activity relationship";
  }
  .grid-area-activity { grid-area: activity; }
  .grid-area-publications { grid-area: auto; }
}
@media (max-width: 900px) {
  .overview-grid { grid-template-columns: 1fr; grid-template-areas: none; }
  .overview-grid > * { grid-area: auto !important; }
  .actions-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .actions-grid { grid-template-columns: 1fr; }
}
</style>

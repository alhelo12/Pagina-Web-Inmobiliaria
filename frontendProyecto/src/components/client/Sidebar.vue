<script setup>
import { useAuthStore } from '@/stores/authStore'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { useMessagesStore } from '@/stores/messagesStore'
import { storeToRefs } from 'pinia'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const notifStore = useNotificationsStore()
const msgStore = useMessagesStore()
const { unreadCount: unreadNotifCount } = storeToRefs(notifStore)
const { unreadCount: unreadMsgCount } = storeToRefs(msgStore)
const router = useRouter()

onMounted(() => {
  notifStore.fetchUnreadCount()
  msgStore.fetchConversations()
})

const handleLogout = () => {
  localStorage.removeItem('backendToken')
  localStorage.removeItem('role')
  localStorage.removeItem('backendUserId')
  localStorage.removeItem('isEmailVerified')
  localStorage.removeItem('userEmail')
  router.push('/')
}
</script>

<template>
  <aside class="sidebar">
    <RouterLink to="/" class="brand">
      <span class="logo-dot"></span>
      <strong>JAKEDA</strong>
    </RouterLink>

    <div class="user-card">
      <div class="user-avatar">{{ auth.userEmail?.charAt(0).toUpperCase() || 'U' }}</div>
      <div class="user-info">
        <strong>{{ auth.userEmail?.split('@')[0] || 'Usuario' }}</strong>
        <small>{{ auth.userEmail || '' }}</small>
      </div>
    </div>

    <nav>
      <RouterLink to="/cliente/dashboard" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
        <span>Dashboard</span>
      </RouterLink>
      <RouterLink to="/cliente/mis-propiedades" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        <span>Mis Propiedades</span>
      </RouterLink>
      <RouterLink to="/cliente/citas" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        <span>Citas</span>
      </RouterLink>
      <RouterLink to="/cliente/mensajes" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        <span>Mensajes</span>
        <span v-if="unreadMsgCount > 0" class="nav-badge">{{ unreadMsgCount > 9 ? '9+' : unreadMsgCount }}</span>
      </RouterLink>
      <RouterLink to="/cliente/perfil" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        <span>Mi Perfil</span>
      </RouterLink>
      <RouterLink to="/cliente/notificaciones" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        <span>Notificaciones</span>
        <span v-if="unreadNotifCount > 0" class="nav-badge">{{ unreadNotifCount > 9 ? '9+' : unreadNotifCount }}</span>
      </RouterLink>
      <RouterLink to="/cliente/post-venta" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <span>Post-Venta</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <div class="sidebar-card">
        <small>Area Personal</small>
        <p>Gestiona tus propiedades publicadas y revisa su estado.</p>
      </div>
      <button class="logout-btn" @click="handleLogout">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        Cerrar sesión
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  width: 280px;
  flex: 0 0 280px;
  background: var(--color-card);
  color: var(--color-navy);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  border-right: 1px solid var(--color-line);
  overflow-y: auto;
  overflow-x: hidden;
}
.brand { display: flex; align-items: center; gap: 12px; color: var(--color-navy); text-decoration: none; }
.logo-dot { width: 12px; height: 12px; border-radius: 999px; background: var(--color-gold); box-shadow: 0 0 0 6px rgba(214, 168, 72, 0.18); }
.brand strong { letter-spacing: .12em; font-weight: 900; }

.user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--color-cream);
  border: 1px solid var(--color-line);
  border-radius: 10px;
}
.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--color-gold);
  color: var(--color-navy);
  display: grid;
  place-items: center;
  font-weight: 900;
  font-size: 15px;
  flex-shrink: 0;
}
.user-info { display: flex; flex-direction: column; min-width: 0; }
.user-info strong { font-size: 13px; color: var(--color-navy); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-info small { font-size: 11px; color: var(--color-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

nav { display: grid; gap: 6px; }
.nav-item {
  color: var(--color-muted);
  padding: 10px 14px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: .3s ease;
  position: relative;
  text-decoration: none;
}
.nav-item svg { flex-shrink: 0; }
.nav-item:hover { background: rgba(214, 168, 72, .1); color: var(--color-navy); transform: translateX(2px); }
.nav-item.router-link-active {
  background: rgba(214, 168, 72, .16);
  color: var(--color-navy);
  font-weight: 700;
  box-shadow: inset 3px 0 0 var(--color-gold);
}
.nav-item.router-link-active svg { stroke: var(--color-gold); }
.nav-badge { margin-left: auto; background: #dc2626; color: white; font-size: 10px; font-weight: 700; min-width: 18px; height: 18px; border-radius: 999px; display: flex; align-items: center; justify-content: center; padding: 0 5px; flex-shrink: 0; }

.sidebar-footer { margin-top: auto; display: flex; flex-direction: column; gap: 12px; }
.sidebar-card { padding: 16px; border-radius: 10px; background: #f7efe0; border: 1px solid rgba(214, 168, 72, .28); }
.sidebar-card small { color: var(--color-gold); font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }
.sidebar-card p { margin-top: 6px; color: var(--color-muted); line-height: 1.5; font-size: 12px; }
.logout-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  background: transparent;
  color: var(--color-muted);
  font-weight: 600;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: .3s ease;
  width: 100%;
  text-align: left;
}
.logout-btn:hover { background: rgba(153, 27, 27, .08); color: #991b1b; }

@media (max-width: 900px) {
  .sidebar { position: static; width: 100%; height: auto; flex: none; padding: 18px; }
  nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .nav-item { font-size: 13px; padding: 10px 12px; gap: 8px; }
  .nav-badge { font-size: 9px; min-width: 16px; height: 16px; }
  .sidebar-card { display: none; }
}
@media (max-width: 560px) {
  nav { grid-template-columns: 1fr; }
}
</style>



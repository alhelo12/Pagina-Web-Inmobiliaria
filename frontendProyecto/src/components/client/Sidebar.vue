<script setup>
import { useAuthStore } from '@/stores/authStore'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { storeToRefs } from 'pinia'

const auth = useAuthStore()
const notifStore = useNotificationsStore()
const { unreadCount } = storeToRefs(notifStore)
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
      <RouterLink to="/cliente/dashboard"><i></i>Dashboard</RouterLink>
      <RouterLink to="/cliente/mis-propiedades"><i></i>Mis Propiedades</RouterLink>
      <RouterLink to="/cliente/citas"><i></i>Citas</RouterLink>
      <RouterLink to="/cliente/mensajes"><i></i>Mensajes</RouterLink>
      <RouterLink to="/cliente/perfil"><i></i>Mi Perfil</RouterLink>
      <RouterLink to="/cliente/notificaciones">
        <i></i>Notificaciones
        <span v-if="unreadCount > 0" class="nav-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
      </RouterLink>
    </nav>

    <div class="sidebar-card">
      <small>Area Personal</small>
      <p>Gestiona tus propiedades publicadas y revisa su estado.</p>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: sticky;
  top: 82px;
  height: calc(100vh - 82px);
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
nav a { color: var(--color-muted); padding: 10px 14px; border-radius: 10px; font-weight: 600; font-size: 14px; display: flex; align-items: center; gap: 10px; transition: .3s ease; position: relative; text-decoration: none; }
nav a i { width: 7px; height: 7px; border-radius: 999px; background: rgba(7, 23, 45, .22); transition: .3s ease; flex-shrink: 0; }
nav a:hover, nav a.router-link-active { background: rgba(214, 168, 72, .14); color: var(--color-navy); transform: translateX(2px); }
nav a:hover i, nav a.router-link-active i { background: var(--color-gold); box-shadow: 0 0 0 5px rgba(214, 168, 72, .14); }
.nav-badge { margin-left: auto; background: #dc2626; color: white; font-size: 10px; font-weight: 700; min-width: 18px; height: 18px; border-radius: 999px; display: flex; align-items: center; justify-content: center; padding: 0 5px; flex-shrink: 0; }

.sidebar-card { margin-top: auto; padding: 16px; border-radius: 10px; background: #f7efe0; border: 1px solid rgba(214, 168, 72, .28); }
.sidebar-card small { color: var(--color-gold); font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }
.sidebar-card p { margin-top: 6px; color: var(--color-muted); line-height: 1.5; font-size: 12px; }

@media (max-width: 900px) {
  .sidebar { position: static; width: 100%; height: auto; flex: none; }
  nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .sidebar-card { display: none; }
}
</style>
<template>
  <aside class="sidebar">
    <RouterLink to="/" class="brand">
      <span class="logo-dot"></span>
      <strong>InmobiPanel</strong>
    </RouterLink>

    <nav>
      <RouterLink to="/admin/dashboard" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
        <span>Dashboard</span>
      </RouterLink>
      <RouterLink to="/admin/propiedades" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        <span>Propiedades</span>
        <span v-if="pendingCount > 0" class="badge">{{ pendingCount > 99 ? '99+' : pendingCount }}</span>
      </RouterLink>
      <RouterLink to="/admin/usuarios" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        <span>Usuarios</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <div class="sidebar-card">
        <small>Panel corporativo</small>
        <p>Gestión clara para propiedades, usuarios y seguimiento comercial.</p>
      </div>
      <button class="logout-btn" @click="handleLogout">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        Cerrar sesión
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { propertiesApi } from '@/api/properties'

const router = useRouter()
const pendingCount = ref(0)

onMounted(async () => {
  try {
    const res = await propertiesApi.getPending({ limit: 1 })
    const items = res.data.properties ?? res.data.items ?? []
    pendingCount.value = res.data.total ?? items.length ?? 0
  } catch {}
})

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/')
}
</script>

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
  gap: 28px;
  border-right: 1px solid var(--color-line);
  overflow-y: auto;
}
.brand { display: flex; align-items: center; gap: 12px; color: var(--color-navy); text-decoration: none; }
.logo-dot { width: 12px; height: 12px; border-radius: 999px; background: var(--color-gold); box-shadow: 0 0 0 6px rgba(214, 168, 72, 0.18); }
.brand strong { letter-spacing: .03em; font-weight: 800; }
nav { display: grid; gap: 6px; }
.nav-item {
  color: var(--color-muted);
  padding: 11px 14px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: .3s ease;
  text-decoration: none;
  position: relative;
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
.badge {
  margin-left: auto;
  background: #fee2e2;
  color: #991b1b;
  font-size: 11px;
  font-weight: 800;
  min-width: 20px;
  height: 20px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
}
.sidebar-footer { margin-top: auto; display: flex; flex-direction: column; gap: 12px; }
.sidebar-card { padding: 18px; border-radius: 10px; background: #f7efe0; border: 1px solid rgba(214, 168, 72, .28); }
.sidebar-card small { color: var(--color-gold); font-weight: 800; font-size: 11px; }
.sidebar-card p { margin-top: 8px; color: var(--color-muted); line-height: 1.6; font-size: 13px; }
.logout-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 14px;
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
  .sidebar { position: static; width: 100%; height: auto; flex: none; }
  nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>

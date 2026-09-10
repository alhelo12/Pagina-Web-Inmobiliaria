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
import { useAuthStore } from '@/stores/authStore'
import { propertiesApi } from '@/api/properties'

const router = useRouter()
const auth = useAuthStore()
const pendingCount = ref(0)

onMounted(async () => {
  try {
    const res = await propertiesApi.getPending({ limit: 1 })
    const items = res.data.properties ?? res.data.items ?? []
    pendingCount.value = res.data.total ?? items.length ?? 0
  } catch {}
})

const handleLogout = async () => {
  await auth.logout()
  router.push('/')
}
</script>

<style scoped>
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  width: 280px;
  flex: 0 0 280px;
  background: #102d2d;
  color: #f3ede0;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 28px;
  border-right: 1px solid #0b2222;
  overflow-y: auto;
  overflow-x: hidden;
}
.brand { display: flex; align-items: center; gap: 12px; color: #f3ede0; text-decoration: none; }
.logo-dot { width: 12px; height: 12px; border-radius: 999px; background: #c9a45c; box-shadow: 0 0 0 6px rgba(201, 164, 92, 0.18); }
.brand strong { letter-spacing: .18em; font-weight: 700; font-family: Georgia, 'Times New Roman', serif; }
nav { display: grid; gap: 6px; }
.nav-item {
  color: rgba(243, 237, 224, 0.72);
  padding: 11px 14px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: background .2s ease, color .2s ease;
  text-decoration: none;
  position: relative;
}
.nav-item svg { flex-shrink: 0; }
.nav-item:hover { background: rgba(201, 164, 92, 0.14); color: #f3ede0; }
.nav-item.router-link-active {
  background: #c9a45c;
  color: #102d2d;
  font-weight: 700;
  box-shadow: none;
}
.nav-item.router-link-active svg { stroke: currentColor; }
.badge {
  margin-left: auto;
  background: #0b2222;
  color: #f3ede0;
  border: 1px solid rgba(243, 237, 224, 0.35);
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
.sidebar-card { padding: 18px; border-radius: 10px; background: rgba(243, 237, 224, 0.05); border: 1px solid rgba(201, 164, 92, 0.3); }
.sidebar-card small { color: #c9a45c; font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: .12em; }
.sidebar-card p { margin-top: 8px; color: rgba(243, 237, 224, 0.65); line-height: 1.6; font-size: 13px; }
.logout-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 14px;
  border-radius: 8px;
  background: transparent;
  color: rgba(243, 237, 224, 0.7);
  font-weight: 600;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: background .2s ease, color .2s ease;
  width: 100%;
  text-align: left;
}
.logout-btn:hover { background: rgba(201, 164, 92, 0.12); color: #f3ede0; }
@media (max-width: 900px) {
  .sidebar { position: static; width: 100%; height: auto; flex: none; padding: 18px; }
  nav { grid-template-columns: 1fr; }
  .nav-item { font-size: 13px; padding: 10px 12px; gap: 8px; }
  .badge { font-size: 9px; min-width: 16px; height: 16px; }
  .sidebar-card { display: none; }
}
</style>



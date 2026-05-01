<template>
  <aside class="sidebar">
    <RouterLink to="/" class="brand">
      <span class="logo-dot"></span>
      <strong>InmobiPanel</strong>
    </RouterLink>

    <nav>
      <RouterLink to="/admin/propiedades"><i>◦</i>Dashboard</RouterLink>
      <RouterLink to="/admin/propiedades"><i>◦</i>Propiedades</RouterLink>
      <RouterLink to="/favoritos"><i>◦</i>Favoritos</RouterLink>
      <RouterLink to="/admin/usuarios"><i>◦</i>Usuarios</RouterLink>
      <RouterLink to="/crear-propiedad"><i>◦</i>Configuracion</RouterLink>
    </nav>

    <div class="sidebar-card">
      <small>Panel corporativo</small>
      <p>Gestion clara para propiedades, usuarios y seguimiento comercial.</p>
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
  background: #ffffff;
  color: #0f172a;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 28px;
  border-right: 1px solid #e7edf7;
}
.brand { display: flex; align-items: center; gap: 12px; color: #0f172a; }
.logo-dot { width: 12px; height: 12px; border-radius: 999px; background: #2563eb; box-shadow: 0 0 0 6px rgba(37, 99, 235, 0.15); }
.brand strong { letter-spacing: .04em; }
nav { display: grid; gap: 8px; }
nav a { color: #64748b; padding: 12px 14px; border-radius: 10px; font-weight: 700; display: flex; align-items: center; gap: 10px; transition: .3s ease; }
nav a i { color: #94a3b8; font-style: normal; }
nav a:hover, nav a.router-link-active { background: #eff6ff; color: #1d4ed8; transform: translateX(2px); }
.sidebar-card { margin-top: auto; padding: 18px; border-radius: 12px; background: #f8fbff; border: 1px solid #dbeafe; }
.sidebar-card small { color: #2563eb; font-weight: 800; }
.sidebar-card p { margin-top: 8px; color: #64748b; line-height: 1.6; font-size: 13px; }
@media (max-width: 900px) {
  .sidebar { position: static; width: 100%; height: auto; flex: none; }
  nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>

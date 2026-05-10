<template>
  <aside class="sidebar">
    <RouterLink to="/" class="brand">
      <span class="logo-dot"></span>
      <strong>InmobiPanel</strong>
    </RouterLink>

    <nav>
      <RouterLink to="/advisor/dashboard"><i></i>Dashboard</RouterLink>
      <RouterLink to="/advisor/panel"><i></i>Mis Propiedades</RouterLink>
      <RouterLink to="/advisor/clientes"><i></i>Clientes</RouterLink>
    </nav>

    <div class="sidebar-card">
      <small>Panel de Asesor</small>
      <p>Gestiona tus propiedades, revisa pendientes y cierra ventas.</p>
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
  gap: 28px;
  border-right: 1px solid var(--color-line);
}
.brand { display: flex; align-items: center; gap: 12px; color: var(--color-navy); }
.logo-dot { width: 12px; height: 12px; border-radius: 999px; background: var(--color-gold); box-shadow: 0 0 0 6px rgba(214, 168, 72, 0.18); }
.brand strong { letter-spacing: .03em; font-weight: 800; }
nav { display: grid; gap: 8px; }
nav a { color: var(--color-muted); padding: 12px 14px; border-radius: 10px; font-weight: 600; display: flex; align-items: center; gap: 10px; transition: .3s ease; }
nav a i { width: 7px; height: 7px; border-radius: 999px; background: rgba(7, 23, 45, .22); transition: .3s ease; }
nav a:hover, nav a.router-link-active { background: rgba(214, 168, 72, .14); color: var(--color-navy); transform: translateX(2px); }
nav a:hover i, nav a.router-link-active i { background: var(--color-gold); box-shadow: 0 0 0 5px rgba(214, 168, 72, .14); }
.sidebar-card { margin-top: auto; padding: 18px; border-radius: 10px; background: #f7efe0; border: 1px solid rgba(214, 168, 72, .28); }
.sidebar-card small { color: var(--color-gold); font-weight: 800; }
.sidebar-card p { margin-top: 8px; color: var(--color-muted); line-height: 1.6; font-size: 13px; }
@media (max-width: 900px) {
  .sidebar { position: static; width: 100%; height: auto; flex: none; }
  nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
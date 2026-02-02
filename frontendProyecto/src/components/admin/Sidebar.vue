<template>
  <aside class="sidebar">
    <h2>Admin</h2>

    <RouterLink to="/admin/dashboard">📊 Dashboard</RouterLink>
    <RouterLink to="/admin/propiedades">🏠 Propiedades</RouterLink>
    <RouterLink to="/admin/usuarios">👥 Usuarios</RouterLink>

    <button class="dark-btn" @click="$emit('toggleDark')">
      🌙 Modo Oscuro
    </button>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  background: #0f2a44;
  color: white;
  padding: 25px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  transition: all 0.3s ease;
}

.sidebar a {
  color: white;
  text-decoration: none;
  padding: 10px;
  border-radius: 8px;
  transition: background 0.2s;
}

.sidebar a:hover {
  background: rgba(255,255,255,0.15);
}

.sidebar a.router-link-active {
  background: #f59e0b;
  color: #0f2a44;
}

.dark-btn {
  margin-top: auto;
  background: #1e3a5f;
  border: none;
  padding: 10px;
  color: white;
  border-radius: 8px;
  cursor: pointer;
}
</style>

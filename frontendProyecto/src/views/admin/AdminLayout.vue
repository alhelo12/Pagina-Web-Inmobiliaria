<script setup>
// El AdminLayout solo envuelve el contenido.
// La navegación se gestiona desde el Navbar global.
</script>

<template>
  <div class="admin-layout">
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f4f6f9;
}
.content {
  padding: 30px;
}
</style>

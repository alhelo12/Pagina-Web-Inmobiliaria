<script setup>
import Sidebar from '@/components/admin/Sidebar.vue'
</script>

<template>
  <div class="admin-layout">
    <Sidebar />
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.admin-layout { min-height: calc(100vh - 60px); display: flex; background: #ffffff; }
.content { flex: 1; min-width: 0; padding: 28px; background: #f8fbff; }
@media (max-width: 900px) {
  .admin-layout { flex-direction: column; }
  .content { padding: 18px; }
}
</style>

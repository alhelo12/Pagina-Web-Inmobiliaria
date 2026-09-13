<script setup>
import Sidebar from '@/components/admin/Sidebar.vue'
</script>

<template>
  <div class="admin-layout">
    <Sidebar />
    <div class="content">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  min-height: calc(100vh - 60px);
  display: flex;
  background: var(--color-ivory);
  font-family: var(--sans);
  overflow-x: hidden;
}

.admin-layout :deep(button),
.admin-layout :deep(input),
.admin-layout :deep(select),
.admin-layout :deep(textarea) {
  font-family: inherit;
}

/* JAKEDA private-panel: serif greeting headings */
.admin-layout :deep(h1),
.admin-layout :deep(h2) {
  font-family: var(--serif);
  font-weight: 700;
  letter-spacing: 0;
}

/* JAKEDA private-panel: white cards, 1px line borders, no heavy shadows */
.admin-layout :deep(.dash-header),
.admin-layout :deep(.feed-card),
.admin-layout :deep(.recent-card),
.admin-layout :deep(.favorites-card),
.admin-layout :deep(.relationship-panel),
.admin-layout :deep(.panel),
.admin-layout :deep(.chart-card),
.admin-layout :deep(.metrics .card),
.admin-layout :deep(.table-card),
.admin-layout :deep(.table-container),
.admin-layout :deep(.filters-bar) {
  box-shadow: none !important;
}
.admin-layout :deep(.dash-header),
.admin-layout :deep(.feed-card),
.admin-layout :deep(.recent-card),
.admin-layout :deep(.favorites-card),
.admin-layout :deep(.relationship-panel),
.admin-layout :deep(.panel),
.admin-layout :deep(.chart-card),
.admin-layout :deep(.table-card),
.admin-layout :deep(.table-container),
.admin-layout :deep(.filters-bar) {
  border: 1px solid var(--color-line) !important;
  background: #ffffff !important;
}

.content { flex: 1; min-width: 0; padding: 32px; background: var(--color-ivory); overflow-x: hidden; }
@media (max-width: 900px) {
  .admin-layout { flex-direction: column; }
  .content { padding: 18px; }
}
</style>


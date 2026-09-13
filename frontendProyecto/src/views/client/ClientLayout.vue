<script setup>
import Sidebar from '@/components/client/Sidebar.vue'
</script>

<template>
  <div class="client-layout">
    <Sidebar />
    <div class="content">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.client-layout {
  min-height: calc(100vh - 60px);
  display: flex;
  background: var(--color-ivory);
  font-family: var(--sans);
  overflow-x: hidden;
}

.client-layout :deep(button),
.client-layout :deep(input),
.client-layout :deep(select),
.client-layout :deep(textarea) {
  font-family: inherit;
}

/* JAKEDA private-panel: serif greeting headings */
.client-layout :deep(h1),
.client-layout :deep(h2) {
  font-family: var(--serif);
  font-weight: 700;
  letter-spacing: 0;
}

/* JAKEDA private-panel: white cards, 1px line borders, no heavy shadows */
.client-layout :deep(.dash-header),
.client-layout :deep(.feed-card),
.client-layout :deep(.recent-card),
.client-layout :deep(.favorites-card),
.client-layout :deep(.relationship-panel),
.client-layout :deep(.panel),
.client-layout :deep(.chart-card),
.client-layout :deep(.metrics .card),
.client-layout :deep(.table-card),
.client-layout :deep(.table-container),
.client-layout :deep(.filters-bar) {
  box-shadow: none !important;
}
.client-layout :deep(.dash-header),
.client-layout :deep(.feed-card),
.client-layout :deep(.recent-card),
.client-layout :deep(.favorites-card),
.client-layout :deep(.relationship-panel),
.client-layout :deep(.panel),
.client-layout :deep(.chart-card),
.client-layout :deep(.table-card),
.client-layout :deep(.table-container),
.client-layout :deep(.filters-bar) {
  border: 1px solid var(--color-line) !important;
  background: #ffffff !important;
}

.content { flex: 1; min-width: 0; padding: 32px; background: var(--color-ivory); overflow-x: hidden; }
@media (max-width: 900px) {
  .client-layout { flex-direction: column; }
  .content { padding: 18px; }
}
</style>


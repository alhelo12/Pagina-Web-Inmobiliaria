<script setup>
import Sidebar from '@/components/advisor/Sidebar.vue'
</script>

<template>
  <div class="advisor-layout">
    <Sidebar />
    <div class="content">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.advisor-layout {
  min-height: calc(100vh - 60px);
  display: flex;
  background: var(--color-ivory);
  font-family: var(--sans);
  overflow-x: hidden;
}

.advisor-layout :deep(button),
.advisor-layout :deep(input),
.advisor-layout :deep(select),
.advisor-layout :deep(textarea) {
  font-family: inherit;
}

/* JAKEDA private-panel: serif greeting headings */
.advisor-layout :deep(h1),
.advisor-layout :deep(h2) {
  font-family: var(--serif);
  font-weight: 700;
  letter-spacing: 0;
}

/* JAKEDA private-panel: white cards, 1px line borders, no heavy shadows */
.advisor-layout :deep(.dash-header),
.advisor-layout :deep(.feed-card),
.advisor-layout :deep(.recent-card),
.advisor-layout :deep(.favorites-card),
.advisor-layout :deep(.relationship-panel),
.advisor-layout :deep(.panel),
.advisor-layout :deep(.chart-card),
.advisor-layout :deep(.metrics .card),
.advisor-layout :deep(.table-card),
.advisor-layout :deep(.table-container),
.advisor-layout :deep(.filters-bar) {
  box-shadow: none !important;
}
.advisor-layout :deep(.dash-header),
.advisor-layout :deep(.feed-card),
.advisor-layout :deep(.recent-card),
.advisor-layout :deep(.favorites-card),
.advisor-layout :deep(.relationship-panel),
.advisor-layout :deep(.panel),
.advisor-layout :deep(.chart-card),
.advisor-layout :deep(.table-card),
.advisor-layout :deep(.table-container),
.advisor-layout :deep(.filters-bar) {
  border: 1px solid var(--color-line) !important;
  background: #ffffff !important;
}

.content { flex: 1; min-width: 0; padding: 32px; background: var(--color-ivory); overflow-x: hidden; }
@media (max-width: 900px) {
  .advisor-layout { flex-direction: column; }
  .content { padding: 18px; }
}
</style>


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
.admin-layout {
  --color-navy: #102d2d;
  --color-navy-2: #1a3f3f;
  --color-gold: #c9a45c;
  --color-cream: #f6f1e7;
  --color-card: #ffffff;
  --color-muted: #6f7a76;
  --color-line: #e5dcc8;
  --shadow-soft: none;
  --shadow-strong: 0 20px 50px rgba(16, 45, 45, 0.18);
  min-height: calc(100vh - 60px);
  display: flex;
  background: var(--color-cream);
  font-family: 'Poppins', sans-serif;
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
  font-family: Georgia, 'Times New Roman', serif;
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
  border: 1px solid #e5dcc8 !important;
  background: #ffffff !important;
}

.content { flex: 1; min-width: 0; padding: 32px; background: var(--color-cream); overflow-x: hidden; }
@media (max-width: 900px) {
  .admin-layout { flex-direction: column; }
  .content { padding: 18px; }
}
</style>


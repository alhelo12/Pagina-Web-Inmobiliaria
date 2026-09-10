<script setup>
import Sidebar from '@/components/client/Sidebar.vue'
</script>

<template>
  <div class="client-layout">
    <Sidebar />
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.client-layout {
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

.client-layout :deep(button),
.client-layout :deep(input),
.client-layout :deep(select),
.client-layout :deep(textarea) {
  font-family: inherit;
}

/* JAKEDA private-panel: serif greeting headings */
.client-layout :deep(h1),
.client-layout :deep(h2) {
  font-family: Georgia, 'Times New Roman', serif;
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
  border: 1px solid #e5dcc8 !important;
  background: #ffffff !important;
}

.content { flex: 1; min-width: 0; padding: 32px; background: var(--color-cream); overflow-x: hidden; }
@media (max-width: 900px) {
  .client-layout { flex-direction: column; }
  .content { padding: 18px; }
}
</style>


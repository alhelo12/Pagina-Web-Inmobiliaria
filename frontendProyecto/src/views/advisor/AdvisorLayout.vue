<script setup>
import Sidebar from '@/components/advisor/Sidebar.vue'
</script>

<template>
  <div class="advisor-layout">
    <Sidebar />
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.advisor-layout {
  --color-navy: #07172d;
  --color-navy-2: #102e4f;
  --color-gold: #d6a848;
  --color-cream: #f5f2ec;
  --color-card: #fffdf8;
  --color-muted: #65717e;
  --color-line: rgba(7, 23, 45, .1);
  --shadow-soft: 0 18px 45px rgba(7, 23, 45, 0.12);
  --shadow-strong: 0 24px 70px rgba(7, 23, 45, 0.22);
  min-height: calc(100vh - 60px);
  display: flex;
  background: var(--color-cream);
  font-family: 'Poppins', sans-serif;
}

.advisor-layout :deep(button),
.advisor-layout :deep(input),
.advisor-layout :deep(select),
.advisor-layout :deep(textarea) {
  font-family: inherit;
}

.content { flex: 1; min-width: 0; padding: 28px; background: var(--color-cream); }
@media (max-width: 900px) {
  .advisor-layout { flex-direction: column; }
  .content { padding: 18px; }
}
</style>

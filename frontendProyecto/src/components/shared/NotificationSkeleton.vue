<script setup>
defineProps({
  count: { type: Number, default: 3 }
})
</script>

<template>
  <div class="skeleton-list">
    <div v-for="i in count" :key="i" class="skeleton-card">
      <div class="skeleton-icon pulse"></div>
      <div class="skeleton-body">
        <div class="skeleton-line skeleton-title pulse"></div>
        <div class="skeleton-line skeleton-text pulse"></div>
        <div class="skeleton-line skeleton-meta pulse"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 4px;
}

.skeleton-card {
  display: flex;
  gap: 16px;
  padding: 18px;
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 10px;
}

.skeleton-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #e5e7eb;
  flex-shrink: 0;
}

.skeleton-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-line {
  background: #e5e7eb;
  border-radius: 6px;
}

.skeleton-title {
  width: 65%;
  height: 16px;
}

.skeleton-text {
  width: 90%;
  height: 12px;
}

.skeleton-meta {
  width: 30%;
  height: 10px;
}

.pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}
</style>

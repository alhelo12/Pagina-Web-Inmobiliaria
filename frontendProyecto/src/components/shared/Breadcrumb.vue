<template>
  <nav class="breadcrumb" aria-label="Navegación">
    <RouterLink to="/admin/dashboard">
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      Inicio
    </RouterLink>
    <template v-for="(crumb, idx) in crumbs" :key="crumb.path">
      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sep"><polyline points="9 18 15 12 9 6"/></svg>
      <RouterLink v-if="idx < crumbs.length - 1" :to="crumb.path">{{ crumb.label }}</RouterLink>
      <span v-else class="current">{{ crumb.label }}</span>
    </template>
  </nav>
</template>

<script setup>
defineProps({
  crumbs: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  flex-wrap: wrap;
}
.breadcrumb a {
  color: var(--color-muted);
  display: flex;
  align-items: center;
  gap: 5px;
  transition: color .2s ease;
  text-decoration: none;
}
.breadcrumb a:hover { color: var(--color-navy); }
.breadcrumb .sep { flex-shrink: 0; }
.breadcrumb .current { color: var(--color-navy); font-weight: 700; }
</style>

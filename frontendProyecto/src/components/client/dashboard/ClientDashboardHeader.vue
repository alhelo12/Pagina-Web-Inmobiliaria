<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, default: '' },
  showAdd: { type: Boolean, default: false },
  addLabel: { type: String, default: 'Agregar' }
})

const emit = defineEmits(['add'])
</script>

<template>
  <header class="dashboard-header">
    <div class="header-left">
      <p class="eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
    </div>

    <div class="header-right">
      <button v-if="showAdd" class="btn-primary" @click="emit('add')">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        {{ addLabel }}
      </button>
    </div>
  </header>
</template>

<style scoped>
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 20px 24px;
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
  box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08);
}
.header-left { display: flex; flex-direction: column; gap: 4px; }
.eyebrow { margin: 0; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
h1 { margin: 0; color: var(--color-navy); font-size: 24px; font-weight: 700; }
.header-right { display: flex; align-items: center; gap: 12px; }
.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: 8px;
  background: var(--color-navy);
  color: #fff;
  font-weight: 700;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: .2s ease;
}
.btn-primary:hover { background: var(--color-navy-2); }
@media (max-width: 768px) {
  .dashboard-header { flex-direction: column; align-items: flex-start; }
  .header-right { width: 100%; }
  .btn-primary { width: 100%; justify-content: center; }
}
</style>
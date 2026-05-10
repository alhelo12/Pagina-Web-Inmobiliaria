<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, default: '' },
  showSearch: { type: Boolean, default: false },
  showExport: { type: Boolean, default: false },
  showAdd: { type: Boolean, default: false },
  addLabel: { type: String, default: 'Agregar' },
  profileName: { type: String, default: '' },
  profileEmail: { type: String, default: '' }
})

const emit = defineEmits(['search', 'export', 'add'])
</script>

<template>
  <header class="dashboard-header">
    <div class="header-left">
      <p class="eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
    </div>

    <div class="header-right">
      <div v-if="showSearch" class="search-box">
        <input type="text" placeholder="Buscar..." @input="emit('search', $event.target.value)" />
      </div>

      <button v-if="showExport" class="btn-secondary" @click="emit('export')">
        Exportar
      </button>

      <button v-if="showAdd" class="btn-primary" @click="emit('add')">
        {{ addLabel }}
      </button>

      <div v-if="profileName" class="profile-pill">
        <div class="avatar">{{ profileName.charAt(0).toUpperCase() }}</div>
        <div class="profile-info">
          <strong>{{ profileName }}</strong>
          <small>{{ profileEmail }}</small>
        </div>
      </div>
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
.search-box input {
  padding: 10px 14px;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  font-size: 14px;
  min-width: 200px;
}
.search-box input:focus { outline: none; border-color: var(--color-gold); }
.btn-secondary {
  padding: 10px 16px;
  border-radius: 8px;
  background: var(--color-cream);
  color: var(--color-navy);
  font-weight: 700;
  border: 1px solid var(--color-line);
  cursor: pointer;
  transition: .2s ease;
}
.btn-secondary:hover { background: #eae6de; }
.btn-primary {
  padding: 10px 16px;
  border-radius: 8px;
  background: var(--color-navy);
  color: #fff;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: .2s ease;
}
.btn-primary:hover { background: var(--color-navy-2); }
.profile-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px 6px 6px;
  background: var(--color-cream);
  border: 1px solid var(--color-line);
  border-radius: 999px;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-gold);
  color: var(--color-navy);
  display: grid;
  place-items: center;
  font-weight: 900;
  font-size: 14px;
}
.profile-info { display: flex; flex-direction: column; }
.profile-info strong { font-size: 13px; color: var(--color-navy); }
.profile-info small { font-size: 11px; color: var(--color-muted); }
@media (max-width: 768px) {
  .dashboard-header { flex-direction: column; align-items: flex-start; }
  .header-right { flex-wrap: wrap; width: 100%; }
  .search-box input { min-width: 100%; }
}
</style>
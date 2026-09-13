<template>
  <header class="dash-header">
    <div class="title-wrap">
      <p>{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
    </div>

    <div class="actions">
      <div v-if="showSearch" class="search-box">
        <input :value="search" @input="$emit('update:search', $event.target.value)" type="search" :placeholder="searchPlaceholder" :aria-label="searchPlaceholder" />
      </div>
      <button v-if="showExport" class="ghost" @click="$emit('export')">Exportar</button>
      <button v-if="showAdd" class="primary" @click="$emit('add')">{{ addLabel }}</button>
      <div v-if="showProfile" class="profile">
        <span class="avatar">{{ avatarInitial }}</span>
        <div>
          <strong>{{ profileName || 'Usuario' }}</strong>
          <small>{{ profileEmail || 'Cuenta activa' }}</small>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  eyebrow: { type: String, default: 'Dashboard' },
  title: { type: String, default: 'Panel' },
  search: { type: String, default: '' },
  searchPlaceholder: { type: String, default: 'Buscar propiedad...' },
  showSearch: { type: Boolean, default: false },
  showExport: { type: Boolean, default: false },
  showAdd: { type: Boolean, default: false },
  showProfile: { type: Boolean, default: false },
  addLabel: { type: String, default: 'Agregar' },
  profileName: { type: String, default: '' },
  profileEmail: { type: String, default: '' }
})
defineEmits(['update:search', 'export', 'add'])

const avatarInitial = computed(() => {
  const name = props.profileName || props.profileEmail || 'U'
  return name.trim().charAt(0).toUpperCase()
})
</script>

<style scoped>
.dash-header { display: flex; justify-content: space-between; gap: 16px; align-items: center; padding: 24px; border-radius: 12px; background: #fff; border: 1px solid var(--color-line); box-shadow: none; overflow: hidden; }
.title-wrap { min-width: 0; }
.title-wrap p { margin: 0; color: var(--color-brass-deep); font-weight: 600; letter-spacing: .22em; text-transform: uppercase; font-size: 11px; }
.title-wrap h1 { margin: 4px 0 0; color: var(--color-petrol); font-size: clamp(26px, 3vw, 36px); font-weight: 500; font-family: var(--serif); letter-spacing: -0.01em; line-height: 1.05; }
.actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; justify-content: flex-end; min-width: 0; }
.actions > * { min-width: 0; }
.search-box { flex: 1 1 240px; min-width: min(240px, 100%); }
.search-box input { width: 100%; max-width: 100%; border: 1px solid var(--color-line); border-radius: 8px; padding: 10px 12px; background: #fff; color: var(--color-petrol); }
.search-box input:focus { outline: none; border-color: var(--color-petrol); box-shadow: none; }
button { border-radius: 8px; padding: 10px 14px; font-weight: 700; border: 1px solid transparent; transition: background .2s ease; white-space: nowrap; min-height: 44px; }
.ghost { background: transparent; color: var(--color-petrol); border-color: var(--color-line); }
.primary { background: var(--color-petrol); color: #fff; }
button:hover { filter: brightness(1.05); box-shadow: none; transform: none; }
.profile { display: flex; align-items: center; gap: 8px; padding: 7px 10px; background: #fff; border: 1px solid var(--color-line); border-radius: 12px; min-width: 0; max-width: 100%; flex: 1 1 250px; }
.avatar { width: 30px; height: 30px; border-radius: 999px; display: grid; place-items: center; background: var(--color-petrol); color: var(--color-ivory); font-weight: 800; }
.profile > div { min-width: 0; }
.profile strong { display: block; color: var(--color-petrol); font-size: 12px; line-height: 1.1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.profile small { display: block; color: var(--color-muted); font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
@media (max-width: 1100px) {
  .dash-header { flex-direction: column; align-items: stretch; }
  .actions { width: 100%; justify-content: flex-start; }
  .profile { flex-basis: 100%; }
}
@media (max-width: 640px) {
  .dash-header { padding: 18px 16px; }
  .actions { display: grid; grid-template-columns: 1fr; }
  .ghost, .primary, .profile { width: 100%; }
  .search-box input { width: 100%; }
}
</style>

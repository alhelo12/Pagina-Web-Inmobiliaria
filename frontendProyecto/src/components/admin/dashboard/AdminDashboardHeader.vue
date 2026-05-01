<template>
  <header class="dash-header">
    <div class="title-wrap">
      <p>Dashboard</p>
      <h1>Panel Administrativo</h1>
    </div>

    <div class="actions">
      <div class="search-box">
        <input :value="search" @input="$emit('update:search', $event.target.value)" type="search" placeholder="Buscar propiedad..." />
      </div>
      <button class="ghost" @click="$emit('export')">Exportar</button>
      <button class="primary" @click="$emit('add')">Agregar</button>
      <div class="profile">
        <span class="avatar">A</span>
        <div>
          <strong>{{ profileName || 'Admin' }}</strong>
          <small>{{ profileEmail || 'Cuenta activa' }}</small>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  search: { type: String, default: '' },
  profileName: { type: String, default: '' },
  profileEmail: { type: String, default: '' }
})
defineEmits(['update:search', 'export', 'add'])
</script>

<style scoped>
.dash-header { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.title-wrap p { margin: 0; color: #2563eb; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: 12px; }
.title-wrap h1 { margin: 4px 0 0; color: #0f172a; font-size: clamp(24px, 3vw, 34px); }
.actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }
.search-box input { width: 260px; border: 1px solid #dbe3f0; border-radius: 10px; padding: 10px 12px; background: #fff; }
button { border-radius: 10px; padding: 10px 14px; font-weight: 700; border: 1px solid transparent; transition: .3s ease; }
.ghost { background: #eef5ff; color: #1e40af; }
.primary { background: #2563eb; color: #fff; }
button:hover { filter: brightness(1.04); box-shadow: 0 10px 18px rgba(37, 99, 235, 0.2); }
.profile { display: flex; align-items: center; gap: 8px; padding: 7px 10px; background: #fff; border: 1px solid #e4ecf8; border-radius: 10px; }
.avatar { width: 30px; height: 30px; border-radius: 999px; display: grid; place-items: center; background: #dbeafe; color: #1d4ed8; font-weight: 800; }
.profile strong { display: block; color: #0f172a; font-size: 12px; line-height: 1.1; }
.profile small { color: #64748b; font-size: 11px; }
@media (max-width: 1100px) {
  .dash-header { flex-direction: column; align-items: stretch; }
  .search-box input { width: 100%; }
}
</style>

<template>
  <header class="dash-header">
    <div class="title-wrap">
      <p>{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
    </div>

    <div class="actions">
      <button v-if="showAdd" class="primary" @click="$emit('add')">{{ addLabel }}</button>
      <div class="profile">
        <span class="avatar">{{ profileInitial }}</span>
        <div>
          <strong>{{ profileName || 'Asesor' }}</strong>
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
  title: { type: String, default: 'Panel del Asesor' },
  showAdd: { type: Boolean, default: true },
  addLabel: { type: String, default: 'Nueva propiedad' },
  profileName: { type: String, default: '' },
  profileEmail: { type: String, default: '' }
})

defineEmits(['add'])

const profileInitial = computed(() => {
  return props.profileName?.charAt(0)?.toUpperCase() || 'A'
})
</script>

<style scoped>
.dash-header { display: flex; justify-content: space-between; gap: 16px; align-items: center; padding: 24px; border-radius: 12px; background: var(--color-card); border: 1px solid var(--color-line); box-shadow: var(--shadow-soft); }
.title-wrap p { margin: 0; color: var(--color-gold); font-weight: 800; letter-spacing: .14em; text-transform: uppercase; font-size: 12px; }
.title-wrap h1 { margin: 4px 0 0; color: var(--color-navy); font-size: clamp(24px, 3vw, 34px); font-weight: 700; }
.actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }
button { border-radius: 8px; padding: 10px 14px; font-weight: 700; border: 1px solid transparent; transition: .3s ease; }
.primary { background: var(--color-gold); color: var(--color-navy); }
button:hover { filter: brightness(1.03); box-shadow: 0 10px 18px rgba(7, 23, 45, 0.12); transform: translateY(-1px); }
.profile { display: flex; align-items: center; gap: 8px; padding: 7px 10px; background: #fff; border: 1px solid var(--color-line); border-radius: 10px; }
.avatar { width: 30px; height: 30px; border-radius: 999px; display: grid; place-items: center; background: var(--color-navy); color: var(--color-gold); font-weight: 800; }
.profile strong { display: block; color: var(--color-navy); font-size: 12px; line-height: 1.1; }
.profile small { color: var(--color-muted); font-size: 11px; }
@media (max-width: 1100px) {
  .dash-header { flex-direction: column; align-items: stretch; }
}
</style>
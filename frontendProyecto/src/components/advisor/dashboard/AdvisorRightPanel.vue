<template>
  <article class="right-panel">
    <h3>Próximas acciones</h3>
    
    <div v-if="pendingProperties?.length" class="actions-list">
      <div v-for="p in pendingProperties" :key="p.id" class="action-item">
        <div class="action-info">
          <strong>{{ p.title }}</strong>
          <span>{{ p.city || 'Sin ciudad' }}</span>
          <small>${{ Number(p.price || 0).toLocaleString('es-MX') }}</small>
        </div>
      </div>
    </div>
    <p v-else class="empty">No hay acciones pendientes</p>

    <button class="review-btn" @click="$emit('go-to-properties')">
      Revisar propiedades
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
    </button>
  </article>
</template>

<script setup>
defineProps({
  pendingProperties: { type: Array, default: () => [] }
})

defineEmits(['go-to-properties'])
</script>

<style scoped>
.right-panel { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; display: flex; flex-direction: column; }
h3 { margin: 0 0 16px; color: var(--color-navy); font-weight: 700; }
.actions-list { display: flex; flex-direction: column; gap: 10px; flex: 1; }
.action-item { padding: 12px; border-radius: 8px; background: #faf9f7; border: 1px solid var(--color-line); }
.action-info { min-width: 0; }
.action-info strong { display: block; color: var(--color-navy); font-size: 14px; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.action-info span { display: block; color: var(--color-muted); font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.action-info small { display: block; color: var(--color-navy); font-weight: 700; font-size: 13px; margin-top: 4px; }
.empty { color: var(--color-muted); font-size: 14px; text-align: center; padding: 20px 0; flex: 1; }
.review-btn { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 16px; padding: 12px 16px; border-radius: 8px; background: var(--color-navy); color: #fff; font-weight: 700; font-size: 14px; border: none; cursor: pointer; transition: .2s; width: 100%; }
.review-btn:hover { filter: brightness(1.1); }
</style>

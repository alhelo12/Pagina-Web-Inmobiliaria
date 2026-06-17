<template>
  <article class="feed-card">
    <div class="feed-head">
      <div>
        <p>{{ subtitle }}</p>
        <h3>{{ title }}</h3>
      </div>
      <slot name="badge" />
    </div>

    <div v-if="loading" class="state">Cargando...</div>

    <div v-else-if="!items?.length" class="state empty">
      <slot name="empty">
        <p>{{ emptyText }}</p>
      </slot>
    </div>

    <div v-else class="feed-list">
      <div
        v-for="item in items"
        :key="item.id"
        :class="['feed-item', { unread: item.unread }]"
        @click="$emit('item-click', item)"
      >
        <div v-if="item.icon || $slots.icon" class="feed-icon">
          <slot name="icon" :item="item">
            <span v-html="item.icon"></span>
          </slot>
        </div>
        <div class="feed-body">
          <div class="feed-header">
            <strong>{{ item.title }}</strong>
            <span class="feed-time">{{ formatTime(item.timestamp || item.created_at) }}</span>
          </div>
          <p>{{ item.message }}</p>
          <span v-if="item.typeLabel" class="feed-type">{{ item.typeLabel }}</span>
        </div>
      </div>
    </div>

    <div v-if="$slots.footer" class="feed-footer">
      <slot name="footer" />
    </div>
  </article>
</template>

<script setup>
defineProps({
  title: { type: String, default: 'Actividad Reciente' },
  subtitle: { type: String, default: 'Actividad' },
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'Sin actividad reciente.' }
})
defineEmits(['item-click'])

const formatTime = (ts) => {
  if (!ts) return ''
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'ahora'
  if (mins < 60) return `hace ${mins} min`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `hace ${hrs}h`
  const days = Math.floor(hrs / 24)
  if (days < 30) return `hace ${days}d`
  return new Date(ts).toLocaleDateString('es-MX', { day: '2-digit', month: 'short' })
}
</script>

<style scoped>
.feed-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; display: flex; flex-direction: column; }
.feed-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.feed-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.feed-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; }
.state { padding: 18px; text-align: center; color: var(--color-muted); flex: 1; }
.feed-list { display: flex; flex-direction: column; gap: 10px; }
.feed-item { display: flex; gap: 12px; padding: 12px; border-radius: 10px; border: 1px solid var(--color-line); background: #fff; cursor: pointer; transition: .2s ease; }
.feed-item:hover { border-color: var(--color-gold); background: #fdfcf8; }
.feed-item.unread { background: #f0f9ff; border-color: #bfdbfe; }
.feed-icon { width: 40px; height: 40px; border-radius: 10px; display: grid; place-items: center; flex-shrink: 0; }
.feed-icon :deep(svg) { width: 18px; height: 18px; }
.feed-body { flex: 1; min-width: 0; }
.feed-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 4px; }
.feed-header strong { color: var(--color-navy); font-size: 13px; }
.feed-time { color: var(--color-muted); font-size: 11px; white-space: nowrap; }
.feed-body p { margin: 0 0 4px; color: var(--color-muted); font-size: 12px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.feed-type { font-size: 11px; font-weight: 700; }
.feed-footer { margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--color-line); text-align: center; }
</style>

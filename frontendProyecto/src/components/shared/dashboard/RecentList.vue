<template>
  <article class="recent-card">
    <div v-if="title || subtitle" class="recent-head">
      <p v-if="subtitle">{{ subtitle }}</p>
      <h3>{{ title || 'Recientes' }}</h3>
    </div>

    <div v-if="items?.length" class="recent-list">
      <component
        :is="itemRoute ? 'router-link' : 'div'"
        v-for="item in items"
        :key="item.id"
        :to="itemRoute ? itemRoute(item) : undefined"
        class="recent-row"
      >
        <div class="recent-thumb-wrap">
          <img
            :src="getImage(item)"
            :alt="item.title"
            class="recent-thumb"
            @error="(e) => { e.target.src = FALLBACK_PROPERTY_IMAGE }"
          />
        </div>
        <div class="recent-info">
          <strong>{{ item.title }}</strong>
          <span>{{ item.city || 'Sin ciudad' }}</span>
        </div>
        <span v-if="showStatus" :class="['recent-badge', item.status]">{{ statusLabel[item.status] || item.status }}</span>
        <span v-if="showPrice" class="recent-price">${{ Number(item.price || 0).toLocaleString('es-MX') }}</span>
        <slot name="actions" :item="item" />
      </component>
    </div>
    <p v-else class="empty">{{ emptyText }}</p>
  </article>
</template>

<script setup>
import { getPropertyImage, FALLBACK_PROPERTY_IMAGE } from '@/utils/propertyImages'

defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  items: { type: Array, default: () => [] },
  emptyText: { type: String, default: 'No hay elementos.' },
  showPrice: { type: Boolean, default: false },
  showStatus: { type: Boolean, default: false },
  itemRoute: { type: Function, default: null }
})

const statusLabel = { pending: 'Pendiente', approved: 'Aprobada', rejected: 'Rechazada', sold: 'Vendida' }

const getImage = (p) => {
  const img = p.images?.find(i => i.is_main) ?? p.images?.[0]
  if (img) {
    const url = img.image_url ?? img.url
    if (!url) return FALLBACK_PROPERTY_IMAGE
    if (/^(https?:|blob:|data:)/.test(url)) return url
    return `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}${url.startsWith('/') ? '' : '/'}${url}`
  }
  return getPropertyImage(p) ?? FALLBACK_PROPERTY_IMAGE
}
</script>

<style scoped>
.recent-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
.recent-head { margin-bottom: 12px; }
.recent-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.recent-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; }
.recent-list { display: grid; gap: 10px; }
.recent-row { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--color-line); background: #fff; text-decoration: none; transition: .2s ease; }
.recent-row:hover { border-color: var(--color-gold); background: #fdfcf8; }
.recent-thumb-wrap { flex-shrink: 0; width: 52px; height: 52px; border-radius: 8px; overflow: hidden; background: #f0ece4; }
.recent-thumb { width: 100%; height: 100%; object-fit: cover; }
.recent-info { flex: 1; min-width: 0; }
.recent-info strong { display: block; color: var(--color-navy); font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.recent-info span { display: block; margin-top: 4px; color: var(--color-muted); font-size: 12px; }
.recent-badge { padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; text-transform: uppercase; flex-shrink: 0; }
.recent-badge.pending { background: #fff3cd; color: #856404; }
.recent-badge.approved { background: #d4edda; color: #155724; }
.recent-badge.rejected { background: #f8d7da; color: #721c24; }
.recent-badge.sold { background: #d1ecf1; color: #0c5460; }
.recent-price { color: var(--color-navy-2); font-weight: 700; white-space: nowrap; font-size: 13px; flex-shrink: 0; }
.empty { margin: 0; color: var(--color-muted); }
@media (max-width: 560px) {
  .recent-card { padding: 14px 12px; }
  .recent-row { display: grid; grid-template-columns: auto minmax(0, 1fr); row-gap: 6px; }
  .recent-badge, .recent-price { grid-column: 1 / -1; justify-self: start; }
}
</style>

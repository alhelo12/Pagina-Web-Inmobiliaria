<script setup>
import { getPropertyImage, FALLBACK_PROPERTY_IMAGE } from '@/utils/propertyImages'

defineProps({ items: Array })

const statusLabel = {
  pending: 'Pendiente',
  approved: 'Aprobada',
  rejected: 'Rechazada',
  sold: 'Vendida'
}
</script>

<template>
  <article class="recent-card">
    <div class="recent-head">
      <p>Mis propiedades</p>
      <h3>Recientes</h3>
    </div>

    <div v-if="items?.length" class="recent-list">
      <div v-for="p in items" :key="p.id" class="recent-row">
        <div class="recent-thumb-wrap">
          <img
            :src="getPropertyImage(p) || FALLBACK_PROPERTY_IMAGE"
            :alt="p.title"
            class="recent-thumb"
            @error="(e) => { e.target.src = FALLBACK_PROPERTY_IMAGE }"
          />
        </div>
        <div class="recent-info">
          <strong>{{ p.title }}</strong>
          <span>{{ p.city || 'Sin ciudad' }}</span>
        </div>
        <span class="recent-status" :class="p.status">{{ statusLabel[p.status] || p.status }}</span>
      </div>
    </div>
    <p v-else class="empty">No tienes propiedades aún.</p>
  </article>
</template>

<style scoped>
.recent-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
.recent-head { margin-bottom: 12px; }
.recent-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.recent-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; }
.recent-list { display: grid; gap: 10px; }
.recent-row { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--color-line); background: #fff; }
.recent-thumb-wrap { flex-shrink: 0; width: 52px; height: 52px; border-radius: 8px; overflow: hidden; background: #f0ece4; }
.recent-thumb { width: 100%; height: 100%; object-fit: cover; }
.recent-info { flex: 1; min-width: 0; }
.recent-info strong { display: block; color: var(--color-navy); font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.recent-info span { display: block; margin-top: 4px; color: var(--color-muted); font-size: 12px; }
.recent-status { padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; text-transform: uppercase; flex-shrink: 0; }
.recent-status.pending { background: #fff3cd; color: #856404; }
.recent-status.approved { background: #d4edda; color: #155724; }
.recent-status.rejected { background: #f8d7da; color: #721c24; }
.recent-status.sold { background: #d1ecf1; color: #0c5460; }
.empty { margin: 0; color: var(--color-muted); }
</style>
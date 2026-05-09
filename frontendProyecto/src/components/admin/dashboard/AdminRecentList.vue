<template>
  <article class="recent">
    <h3>Propiedades recientes</h3>
    <div class="list">
      <div v-for="p in items" :key="p.id" class="row">
        <div class="thumb-wrap">
          <img
            :src="getImage(p)"
            :alt="p.title"
            class="thumb"
            @error="(e) => { e.target.src = fallback }"
          />
        </div>
        <div>
          <strong>{{ p.title }}</strong>
          <p>{{ p.city }} · {{ propertyTypeLabel(p.property_type) }}</p>
        </div>
        <div class="right">
          <span>${{ Number(p.price).toLocaleString('es-MX') }}</span>
          <small :class="p.status">{{ p.status }}</small>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
import { getPropertyImage } from '@/utils/propertyImages'

defineProps({ items: { type: Array, default: () => [] } })

const fallback = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgdmlld0JveD0iMCAwIDY0IDY0IiBzdHlsZT0iZGlzcGxheTpibG9jazsiIGNsYXNzPSJhIiBmaWxsPSIjZWRlY2VkIj48cmVjdCB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHJ4PSIxMiIgc3R5bGU9ImZpbGw6I2VkZWNlZCIgc3BhY2Y9Im5vbmUiLz48cGF0aCBkPSJNMjIgMzZoMjBjLTEuMSAwLTIgLjktMiAyIDAgMS4xLjkgMiAyIDIgMCAxLjEtLjkgMi0yIDJoLTIwYzEuMSAwIDItLjkgMi0yIDAtMS4xLS45LTItMi0yeiIgZmlsbD0iI2RkYzJkNSIvPjwvc3ZnPg=='

const getImage = (p) => {
  const img = p.images?.find(i => i.is_main) ?? p.images?.[0]
  if (img) {
    const url = img.image_url ?? img.url
    if (!url) return fallback
    if (/^(https?:|blob:|data:)/.test(url)) return url
    return `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}${url.startsWith('/') ? '' : '/'}${url}`
  }
  return getPropertyImage(p) ?? fallback
}

const propertyTypeLabel = (type) => {
  const map = { house: 'Casa', apartment: 'Departamento', '': '-' }
  return map[type] ?? type ?? '-'
}
</script>

<style scoped>
.recent { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
h3 { margin: 0 0 12px; color: var(--color-navy); font-weight: 700; }
.list { display: grid; gap: 10px; }
.row { display: flex; align-items: center; gap: 12px; border: 1px solid var(--color-line); border-radius: 10px; padding: 10px 12px; background: #fff; }
.thumb-wrap { flex-shrink: 0; width: 56px; height: 56px; border-radius: 8px; overflow: hidden; background: #f0ece4; }
.thumb { width: 100%; height: 100%; object-fit: cover; }
.row > div:nth-child(2) { flex: 1; min-width: 0; }
.row strong { display: block; color: var(--color-navy); font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.row p { margin: 4px 0 0; color: var(--color-muted); font-size: 12px; }
.right { text-align: right; flex-shrink: 0; }
.right span { display: block; font-weight: 700; color: var(--color-navy); }
.right small { text-transform: capitalize; color: var(--color-gold); font-weight: 700; }
</style>

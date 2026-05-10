<script setup>
defineProps({
  title: { type: String, default: 'Recientes' },
  items: { type: Array, default: () => [] },
  emptyText: { type: String, default: 'No hay elementos.' }
})

const getPropertyImage = (property) => {
  const img = property.images?.find(i => i.is_main) ?? property.images?.[0]
  if (img) {
    const url = img.image_url ?? img.url
    if (!url) return null
    if (/^(https?:|blob:|data:)/.test(url)) return url
    const base = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
    return `${base}${url.startsWith('/') ? '' : '/'}${url}`
  }
  return null
}

const fallback = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgdmlld0JveD0iMCAwIDY0IDY0IiBzdHlsZT0iZGlzcGxheTpibG9jazsiIGNsYXNzPSJhIiBmaWxsPSIjZWRlY2VkIj48cmVjdCB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHJ4PSIxMiIgc3R5bGU9ImZpbGw6I2VkZWNlZCIgc3BhY2Y9Im5vbmUiLz48cGF0aCBkPSJNMjIgMzZoMjBjLTEuMSAwLTIgLjktMiAyIDAgMS4xLjkgMiAyIDIgMCAxLjEtLjkgMi0yIDJoLTIwYzEuMSAwIDItLjkgMi0yIDAtMS4xLS45LTItMi0yeiIgZmlsbD0iI2RkYzJkNSIvPjwvc3ZnPg=='
</script>

<template>
  <article class="recent-list-card">
    <div class="card-head">
      <p>{{ title }}</p>
      <h3>Propiedades Recientes</h3>
    </div>

    <div v-if="items.length" class="list">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        :to="`/propiedades/${item.id}`"
        class="list-item"
      >
        <div class="thumb-wrap">
          <img
            :src="getPropertyImage(item) || fallback"
            :alt="item.title"
            @error="(e) => { e.target.src = fallback }"
          />
        </div>
        <div class="item-info">
          <strong>{{ item.title }}</strong>
          <span>{{ item.city || 'Sin ciudad' }}</span>
        </div>
        <span class="price">${{ Number(item.price || 0).toLocaleString('es-MX') }}</span>
      </RouterLink>
    </div>

    <p v-else class="empty">{{ emptyText }}</p>
  </article>
</template>

<style scoped>
.recent-list-card {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 10px;
  box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08);
  padding: 18px;
}
.card-head { margin-bottom: 12px; }
.card-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.card-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; }
.list { display: grid; gap: 10px; }
.list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid var(--color-line);
  background: #fff;
  text-decoration: none;
  transition: .2s ease;
}
.list-item:hover { border-color: var(--color-gold); background: #fdfcf8; }
.thumb-wrap {
  width: 52px;
  height: 52px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--color-cream);
}
.thumb-wrap img { width: 100%; height: 100%; object-fit: cover; }
.item-info { flex: 1; min-width: 0; }
.item-info strong {
  display: block;
  color: var(--color-navy);
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.item-info span { display: block; margin-top: 2px; color: var(--color-muted); font-size: 12px; }
.price { color: var(--color-navy-2); font-weight: 700; white-space: nowrap; font-size: 13px; }
.empty { margin: 0; color: var(--color-muted); font-size: 13px; }
</style>
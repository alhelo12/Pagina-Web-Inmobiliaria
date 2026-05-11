<script setup>
import { usePropertyStore } from '@/stores/propertyStore'
import { getPropertyImage, FALLBACK_PROPERTY_IMAGE } from '@/utils/propertyImages'
import { storeToRefs } from 'pinia'

const store = usePropertyStore()
const { availableProperties } = storeToRefs(store)

const emit = defineEmits(['take'])

const formatPrice = (price) => Number(price || 0).toLocaleString('es-MX')
</script>

<template>
  <article class="available-card">
    <div class="available-head">
      <p>Nuevas</p>
      <h3>Disponibles para tomar</h3>
    </div>

    <div v-if="availableProperties?.length" class="available-list">
      <div v-for="p in availableProperties" :key="p.id" class="available-row">
        <div class="available-thumb-wrap">
          <img
            :src="getPropertyImage(p) || FALLBACK_PROPERTY_IMAGE"
            :alt="p.title"
            class="available-thumb"
            @error="(e) => { e.target.src = FALLBACK_PROPERTY_IMAGE }"
          />
        </div>
        <div class="available-info">
          <strong>{{ p.title }}</strong>
          <span>{{ p.city || 'Sin ciudad' }}</span>
        </div>
        <small>${{ formatPrice(p.price) }}</small>
        <button class="take-btn" @click="emit('take', p)">Tomar</button>
      </div>
    </div>
    <p v-else class="empty">No hay propiedades disponibles.</p>
  </article>
</template>

<style scoped>
.available-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
.available-head { margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
.available-head p { margin: 0 0 4px; color: var(--color-gold); font-size: 12px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.available-head h3 { margin: 0; color: var(--color-navy); font-size: 18px; }
.available-list { display: grid; gap: 10px; }
.available-row { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--color-line); background: #fff; }
.available-thumb-wrap { flex-shrink: 0; width: 52px; height: 52px; border-radius: 8px; overflow: hidden; background: #f0ece4; }
.available-thumb { width: 100%; height: 100%; object-fit: cover; }
.available-info { flex: 1; min-width: 0; }
.available-info strong { display: block; color: var(--color-navy); font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.available-info span { display: block; margin-top: 4px; color: var(--color-muted); font-size: 12px; }
.available-row small { color: var(--color-navy-2); font-weight: 700; white-space: nowrap; }
.take-btn { padding: 6px 12px; border-radius: 6px; background: var(--color-gold); color: var(--color-navy); font-weight: 600; font-size: 12px; border: none; cursor: pointer; transition: .2s; }
.take-btn:hover { filter: brightness(1.05); }
.empty { margin: 0; color: var(--color-muted); }
</style>
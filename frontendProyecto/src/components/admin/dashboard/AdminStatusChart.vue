<template>
  <article class="chart-card">
    <h3>Estado de propiedades</h3>
    <div class="bars">
      <div v-for="item in points" :key="item.label" class="bar-item">
        <div class="bar-wrap">
          <div class="bar" :style="{ height: item.height + '%'}"></div>
        </div>
        <small>{{ item.label }}</small>
        <strong>{{ item.value }}</strong>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  dataset: { type: Array, default: () => [] }
})

const points = computed(() => {
  const max = Math.max(...props.dataset.map(d => d.value), 1)
  return props.dataset.map(d => ({ ...d, height: Math.max(10, Math.round((d.value / max) * 100)) }))
})
</script>

<style scoped>
.chart-card { background: #fff; border: 1px solid #e6edf8; border-radius: 14px; box-shadow: 0 10px 26px rgba(15, 23, 42, 0.07); padding: 18px; }
h3 { margin: 0 0 16px; color: #0f172a; }
.bars { height: 240px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; align-items: end; }
.bar-item { text-align: center; }
.bar-wrap { height: 180px; display: flex; align-items: flex-end; justify-content: center; }
.bar { width: 36px; border-radius: 10px 10px 6px 6px; background: linear-gradient(180deg, #60a5fa, #2563eb); transition: .2s; }
.bar:hover { filter: brightness(1.08); }
small { display: block; margin-top: 8px; color: #64748b; }
strong { color: #0f172a; font-size: 13px; }
</style>

<template>
  <article class="chart-card">
    <h3>{{ title }}</h3>
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
  title: { type: String, default: 'Estado de propiedades' },
  dataset: { type: Array, default: () => [] }
})

const points = computed(() => {
  const max = Math.max(...props.dataset.map(d => d.value), 1)
  return props.dataset.map(d => ({ ...d, height: Math.max(10, Math.round((d.value / max) * 100)) }))
})
</script>

<style scoped>
.chart-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
h3 { margin: 0 0 16px; color: var(--color-navy); font-weight: 700; }
.bars { height: 240px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; align-items: end; }
.bar-item { text-align: center; min-width: 0; }
.bar-wrap { height: 180px; display: flex; align-items: flex-end; justify-content: center; }
.bar { width: 36px; border-radius: 10px 10px 6px 6px; background: var(--color-gold); transition: .2s; }
.bar:hover { filter: brightness(1.08); }
small { display: block; margin-top: 8px; color: var(--color-muted); overflow-wrap: anywhere; }
strong { color: var(--color-navy); font-size: 13px; }
@media (max-width: 560px) {
  .chart-card { padding: 16px 12px; }
  .bars { height: 212px; gap: 8px; }
  .bar-wrap { height: 150px; }
  .bar { width: 26px; }
  small { font-size: 12px; }
}
</style>

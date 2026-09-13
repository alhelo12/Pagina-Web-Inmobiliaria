<template>
  <section class="metrics">
    <article v-for="card in cards" :key="card.key" :class="['card', { highlight: card.highlight }]">
      <div class="card-icon" :style="card.iconStyle" />
      <span>{{ card.label }}</span>
      <strong>{{ metrics[card.key] ?? 0 }}</strong>
      <small>{{ card.sublabel }}</small>
    </article>
  </section>
</template>

<script setup>
defineProps({
  cards: { type: Array, required: true },
  metrics: { type: Object, required: true }
})
</script>

<style scoped>
.metrics { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }
.card { background: #fff; border-radius: 12px; border: 1px solid var(--color-line); box-shadow: none; padding: 16px; transition: border-color .2s ease; position: relative; overflow: hidden; }
.card:hover { transform: none; box-shadow: none; border-color: var(--color-brass); }
.card-icon { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
.card-icon :deep(svg) { width: 22px; height: 22px; }
.card span { color: var(--color-muted); font-size: 11px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; }
.card strong { display: block; margin-top: 8px; color: var(--color-petrol); font-size: 34px; font-weight: 500; font-family: var(--serif); line-height: 1; }
.card small { color: var(--color-muted); font-size: 12px; }
.highlight { background: var(--color-ivory-2); }
@media (max-width: 560px) { .metrics { grid-template-columns: 1fr; } }
</style>

<template>
  <section class="metrics">
    <article v-for="card in cards" :key="card.key" :class="['card', { highlight: card.highlight }]">
      <div class="card-icon" :style="card.iconStyle">
        <span v-html="card.icon"></span>
      </div>
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
.card { background: var(--color-card); border-radius: 10px; border: 1px solid var(--color-line); box-shadow: 0 10px 24px rgba(7, 23, 45, 0.08); padding: 16px; transition: .3s ease; position: relative; overflow: hidden; }
.card:hover { transform: translateY(-3px); box-shadow: 0 16px 32px rgba(7, 23, 45, 0.12); }
.card-icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
.card-icon :deep(svg) { width: 22px; height: 22px; }
.card span { color: var(--color-muted); font-size: 13px; font-weight: 600; }
.card strong { display: block; margin-top: 8px; color: var(--color-navy); font-size: 30px; font-weight: 700; }
.card small { color: #87909b; font-size: 12px; }
.highlight { background: linear-gradient(150deg, rgba(214, 168, 72, .2) 0%, var(--color-card) 100%); }
@media (max-width: 560px) { .metrics { grid-template-columns: 1fr; } }
</style>

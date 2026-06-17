<template>
  <article class="panel">
    <h3 v-if="title">{{ title }}</h3>

    <div v-if="items?.length && !$slots.default" class="items-list">
      <div v-for="item in items" :key="item.key" class="item-row">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </div>

    <slot />
  </article>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  items: { type: Array, default: () => [] }
})
</script>

<style scoped>
.panel { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; display: flex; flex-direction: column; }
h3 { margin: 0 0 12px; color: var(--color-navy); font-weight: 700; }
.items-list { display: grid; gap: 10px; }
.item-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-radius: 10px; background: #f7efe0; }
.item-row span { color: var(--color-muted); }
.item-row strong { color: var(--color-navy); }
</style>

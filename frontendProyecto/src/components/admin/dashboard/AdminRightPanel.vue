<template>
  <article class="panel">
    <h3>Resumen rápido</h3>
    <ul>
      <li><span>Vendidas</span><strong>{{ sold }}</strong></li>
      <li><span>Rechazadas</span><strong>{{ rejected }}</strong></li>
      <li><span>Precio promedio</span><strong>${{ avgPrice }}</strong></li>
    </ul>
  </article>
</template>

<script setup>
defineProps({ sold: Number, rejected: Number, avgPrice: String })
</script>

<style scoped>
.panel { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
h3 { margin: 0 0 12px; color: var(--color-navy); font-weight: 700; }
ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
li { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-radius: 10px; background: #f7efe0; }
span { color: var(--color-muted); }
strong { color: var(--color-navy); }
</style>

<template>
  <article class="panel">
    <h3>Resumen rapido</h3>
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
.panel { background: #fff; border: 1px solid #e6edf8; border-radius: 14px; box-shadow: 0 10px 26px rgba(15, 23, 42, 0.07); padding: 18px; }
h3 { margin: 0 0 12px; }
ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
li { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-radius: 10px; background: #f8fbff; }
span { color: #475569; }
strong { color: #0f172a; }
</style>

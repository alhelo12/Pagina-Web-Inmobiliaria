<template>
  <article class="recent">
    <h3>Propiedades recientes</h3>
    <div class="list">
      <div v-for="p in items" :key="p.id" class="row">
        <div>
          <strong>{{ p.title }}</strong>
          <p>{{ p.city }} · {{ p.property_type }}</p>
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
defineProps({ items: { type: Array, default: () => [] } })
</script>

<style scoped>
.recent { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 10px; box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08); padding: 18px; }
h3 { margin: 0 0 12px; color: var(--color-navy); font-weight: 700; }
.list { display: grid; gap: 10px; }
.row { display: flex; justify-content: space-between; gap: 10px; align-items: center; border: 1px solid var(--color-line); border-radius: 10px; padding: 10px 12px; background: #fff; }
.row strong { color: var(--color-navy); }
.row p { margin: 4px 0 0; color: var(--color-muted); font-size: 12px; }
.right { text-align: right; }
.right span { display: block; font-weight: 700; color: var(--color-navy); }
.right small { text-transform: capitalize; color: var(--color-gold); font-weight: 700; }
</style>

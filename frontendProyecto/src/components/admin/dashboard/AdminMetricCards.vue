<template>
  <section class="metrics">
    <article class="card">
      <span>Total propiedades</span>
      <strong>{{ metrics.total }}</strong>
      <small>Registros cargados</small>
    </article>
    <article class="card">
      <span>Aprobadas</span>
      <strong>{{ metrics.approved }}</strong>
      <small>Disponibles al público</small>
    </article>
    <article class="card">
      <span>Pendientes</span>
      <strong>{{ metrics.pending }}</strong>
      <small>En revisión</small>
    </article>
    <article class="card highlight">
      <span>Tasa aprobación</span>
      <strong>{{ metrics.approvalRate }}%</strong>
      <small>Rendimiento general</small>
    </article>
  </section>
</template>

<script setup>
defineProps({ metrics: { type: Object, required: true } })
</script>

<style scoped>
.metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.card { background: var(--color-card); border-radius: 10px; border: 1px solid var(--color-line); box-shadow: 0 10px 24px rgba(7, 23, 45, 0.08); padding: 16px; transition: .3s ease; }
.card:hover { transform: translateY(-3px); box-shadow: 0 16px 32px rgba(7, 23, 45, 0.12); }
.card span { color: var(--color-muted); font-size: 13px; font-weight: 600; }
.card strong { display: block; margin-top: 8px; color: var(--color-navy); font-size: 30px; font-weight: 700; }
.card small { color: #87909b; font-size: 12px; }
.highlight { background: linear-gradient(150deg, rgba(214, 168, 72, .2) 0%, var(--color-card) 100%); }
@media (max-width: 980px) { .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .metrics { grid-template-columns: 1fr; } }
</style>

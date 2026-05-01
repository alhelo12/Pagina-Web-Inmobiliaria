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
      <small>Disponibles al publico</small>
    </article>
    <article class="card">
      <span>Pendientes</span>
      <strong>{{ metrics.pending }}</strong>
      <small>En revision</small>
    </article>
    <article class="card highlight">
      <span>Tasa aprobacion</span>
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
.card { background: #fff; border-radius: 14px; border: 1px solid #e6edf8; box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06); padding: 16px; transition: .3s ease; }
.card:hover { transform: translateY(-3px); box-shadow: 0 14px 24px rgba(15, 23, 42, 0.1); }
.card span { color: #64748b; font-size: 13px; font-weight: 600; }
.card strong { display: block; margin-top: 8px; color: #0f172a; font-size: 30px; }
.card small { color: #94a3b8; font-size: 12px; }
.highlight { background: linear-gradient(150deg, #eff6ff 0%, #ffffff 100%); }
@media (max-width: 980px) { .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .metrics { grid-template-columns: 1fr; } }
</style>

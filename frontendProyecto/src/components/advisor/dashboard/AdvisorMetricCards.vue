<template>
  <section class="metrics">
    <article class="card">
      <div class="card-icon total-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      </div>
      <span>Mis propiedades</span>
      <strong>{{ metrics.total }}</strong>
      <small>Total asignadas</small>
    </article>
    <article class="card">
      <div class="card-icon approved-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
      </div>
      <span>Aprobadas</span>
      <strong>{{ metrics.approved }}</strong>
      <small>Visibles al público</small>
    </article>
    <article class="card">
      <div class="card-icon pending-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      </div>
      <span>Pendientes</span>
      <strong>{{ metrics.pending }}</strong>
      <small>En revisión</small>
    </article>
    <article class="card highlight">
      <div class="card-icon sold-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      </div>
      <span>Vendidas</span>
      <strong>{{ metrics.sold }}</strong>
      <small>Cerradas</small>
    </article>
    <article class="card">
      <div class="card-icon available-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>
      </div>
      <span>Disponibles</span>
      <strong>{{ metrics.availableToTake }}</strong>
      <small>Para tomar</small>
    </article>
    <article class="card">
      <div class="card-icon clients-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      </div>
      <span>Clientes</span>
      <strong>{{ metrics.clientsCount ?? 0 }}</strong>
      <small>Propietarios únicos</small>
    </article>
  </section>
</template>

<script setup>
defineProps({ metrics: { type: Object, required: true } })
</script>

<style scoped>
.metrics { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 14px; }
.card { background: var(--color-card); border-radius: 10px; border: 1px solid var(--color-line); box-shadow: 0 10px 24px rgba(7, 23, 45, 0.08); padding: 16px; transition: .3s ease; position: relative; overflow: hidden; }
.card:hover { transform: translateY(-3px); box-shadow: 0 16px 32px rgba(7, 23, 45, 0.12); }
.card-icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
.total-icon { background: #e8edf0; color: var(--color-navy-2); }
.approved-icon { background: #dff7e9; color: #166534; }
.pending-icon { background: #fff3ce; color: #856404; }
.sold-icon { background: #d4edda; color: #155724; }
.available-icon { background: #f7efe0; color: var(--color-navy-2); }
.clients-icon { background: #f0e8fd; color: #6b21a8; }
.card span { color: var(--color-muted); font-size: 13px; font-weight: 600; }
.card strong { display: block; margin-top: 8px; color: var(--color-navy); font-size: 30px; font-weight: 700; }
.card small { color: #87909b; font-size: 12px; }
.highlight { background: linear-gradient(150deg, rgba(214, 168, 72, .2) 0%, var(--color-card) 100%); }
@media (max-width: 1400px) { .metrics { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 980px) { .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .metrics { grid-template-columns: 1fr; } }
</style>
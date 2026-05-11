<template>
  <section class="metrics">
    <article class="card">
      <div class="card-icon heart-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
      </div>
      <span>Total favoritos</span>
      <strong>{{ metrics.favoritesCount || 0 }}</strong>
      <small>Propiedades guardadas</small>
    </article>
    <article class="card">
      <div v-if="metrics.unreadNotifications > 0" class="card-badge">{{ metrics.unreadNotifications > 9 ? '9+' : metrics.unreadNotifications }}</div>
      <div class="card-icon home-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      </div>
      <span>Mis propiedades</span>
      <strong>{{ metrics.myPropertiesCount || 0 }}</strong>
      <small>Publicadas por ti</small>
    </article>
    <article class="card">
      <div class="card-icon pending-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      </div>
      <span>Pendientes</span>
      <strong>{{ metrics.pendingCount || 0 }}</strong>
      <small>En revisión</small>
    </article>
    <article class="card">
      <div class="card-icon message-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      </div>
      <span>Mensajes</span>
      <strong>0</strong>
      <small>Sin leer</small>
    </article>
  </section>
</template>

<script setup>
defineProps({
  metrics: {
    type: Object,
    default: () => ({ favoritesCount: 0, myPropertiesCount: 0, pendingCount: 0, unreadNotifications: 0 })
  }
})
</script>

<style scoped>
.metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.card { background: var(--color-card); border-radius: 10px; border: 1px solid var(--color-line); box-shadow: 0 10px 24px rgba(7, 23, 45, 0.08); padding: 16px; transition: .3s ease; position: relative; overflow: hidden; }
.card:hover { transform: translateY(-3px); box-shadow: 0 16px 32px rgba(7, 23, 45, 0.12); }
.card-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #dc2626;
  color: white;
  font-size: 10px;
  font-weight: 700;
  min-width: 20px;
  height: 20px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.4);
}
.card-icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
.heart-icon { background: #fce7e7; color: #dc2626; }
.home-icon { background: #e8edf0; color: var(--color-navy-2); }
.pending-icon { background: #fff3ce; color: #856404; }
.explore-icon { background: #d4edda; color: #155724; }
.message-icon { background: #e0e7ff; color: #4338ca; }
.card span { color: var(--color-muted); font-size: 13px; font-weight: 600; }
.card strong { display: block; margin-top: 8px; color: var(--color-navy); font-size: 30px; font-weight: 700; }
.card small { color: #87909b; font-size: 12px; }
@media (max-width: 1200px) { .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .metrics { grid-template-columns: 1fr; } }
</style>
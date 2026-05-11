<template>
  <section class="hero">
    <div class="hero-content">
      <p class="eyebrow">Bienes raices con vision corporativa</p>
      <h1>Elevando tu inversion inmobiliaria</h1>
      <p class="lead">
        Compra, venta y renta de propiedades con asesoria estrategica,
        respaldo juridico y una experiencia clara de principio a fin.
      </p>

      <div class="hero-actions">
        <RouterLink to="/propiedades" class="primary">Ver propiedades</RouterLink>
        <RouterLink to="/servicios" class="secondary">Ver servicios</RouterLink>
      </div>

      <Suspense>
        <template #default>
          <SearchBar />
        </template>

        <template #fallback>
          <div class="search-skeleton">Cargando buscador...</div>
        </template>
      </Suspense>
    </div>
  </section>
</template>

<script setup>
import { defineAsyncComponent } from 'vue'
import { RouterLink } from 'vue-router'

const SearchBar = defineAsyncComponent(() =>
  import('@/components/home/SearchBar.vue')
)
</script>

<style scoped>
.hero {
  padding-top: 80px;
  position: relative;
  min-height: 720px;
  background-image:
    linear-gradient(90deg, rgba(7, 23, 45, .94) 0%, rgba(10, 33, 57, .78) 46%, rgba(7, 23, 45, .48) 100%),
    linear-gradient(180deg, rgba(7, 23, 45, .18), rgba(7, 23, 45, .86)),
    url('@/assets/images/fondo2.jpg');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.hero::after {
  content: "";
  position: absolute;
  inset: auto 0 0;
  height: 160px;
  background: linear-gradient(180deg, transparent, #f5f2ec);
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 1180px;
  width: 100%;
  margin: 0 auto;
  padding: 90px 24px 140px;
  color: white;
}

.eyebrow {
  color: #f2c46d;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: .18em;
  text-transform: uppercase;
  margin-bottom: 18px;
}

.hero-content h1 {
  max-width: 760px;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(44px, 7vw, 82px);
  line-height: .98;
  font-weight: 800;
  margin-bottom: 22px;
}

.lead {
  font-size: 19px;
  max-width: 650px;
  color: rgba(255, 255, 255, .82);
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin: 34px 0 32px;
}

.primary,
.secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 24px;
  border-radius: 8px;
  font-weight: 900;
  transition: transform .22s ease, box-shadow .22s ease, background .22s ease;
}

.primary {
  background: #2a8cff;
  box-shadow: 0 14px 30px rgba(42, 140, 255, .28);
}

.secondary {
  border: 1px solid rgba(242, 196, 109, .72);
  color: #f2c46d;
}

.primary:hover,
.secondary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-strong);
}

.search-skeleton {
  background: rgba(255,255,255,.2);
  padding: 24px;
  border-radius: 10px;
  color: white;
}

@media (max-width: 900px) {
  .hero { min-height: 680px; }
}

@media (max-width: 480px) {
  .hero { min-height: 720px; }
  .hero-actions { align-items: stretch; flex-direction: column; }
}
</style>

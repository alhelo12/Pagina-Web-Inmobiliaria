<script setup>
const services = [
  {
    title: 'Compra de inmuebles',
    description: 'Acompanamiento de punta a punta para adquirir propiedad con analisis de zona, precio y validacion documental.',
    tag: 'Asesoria integral'
  },
  {
    title: 'Venta de propiedades',
    description: 'Estrategia comercial, fotografia profesional y negociacion para cerrar en mejores tiempos y condiciones.',
    tag: 'Comercializacion'
  },
  {
    title: 'Renta y administracion',
    description: 'Perfilamiento de inquilinos, contratos claros y seguimiento operativo para proteger tu inversion.',
    tag: 'Gestion activa'
  },
  {
    title: 'Asesoria juridica',
    description: 'Soporte legal en contratos, escrituracion y cumplimiento normativo durante toda la operacion.',
    tag: 'Respaldo legal'
  },
  {
    title: 'Valuacion inmobiliaria',
    description: 'Estimacion tecnica con criterios de mercado para definir precios competitivos y sostenibles.',
    tag: 'Analisis de mercado'
  },
  {
    title: 'Inversion y portafolio',
    description: 'Planeacion de compras por objetivos, flujo esperado y perfil de riesgo para crecimiento patrimonial.',
    tag: 'Planeacion financiera'
  }
]
</script>

<template>
  <section class="services-page">
    <header class="hero">
      <div class="overlay"></div>
      <div class="hero-content">
        <p class="eyebrow-label hero-eyebrow">Servicios inmobiliarios</p>
        <h1 class="serif-display">Soluciones premium para compra, venta y renta</h1>
        <hr class="rule rule-light" />
        <p class="hero-sub">
          Operamos con procesos claros, acompanamiento cercano y enfoque en resultados.
          Tu patrimonio se gestiona con precision y transparencia.
        </p>
      </div>
    </header>

    <div class="services-wrap">
      <article v-for="service in services" :key="service.title" class="service-card">
        <span class="tag">{{ service.tag }}</span>
        <h3 class="serif-display">{{ service.title }}</h3>
        <hr class="rule" />
        <p>{{ service.description }}</p>
        <button type="button" class="read-more">
          <span class="dot">→</span>
          Conocer mas
        </button>
      </article>
    </div>

    <section class="subscribe">
      <div class="subscribe-left">
        <p class="eyebrow-label eyebrow-on-dark">Boletín</p>
        <h2 class="serif-display">Recibe novedades del mercado inmobiliario</h2>
        <p>Alertas de oportunidades, tendencias y propiedades destacadas.</p>
      </div>
      <form class="subscribe-form" @submit.prevent>
        <input type="email" placeholder="Correo electronico" aria-label="Correo electronico" />
        <button type="submit">Suscribirme</button>
      </form>
    </section>
  </section>
</template>

<style scoped>
.services-page {
  font-family: var(--sans);
  background: var(--color-ivory);
  color: var(--color-ink);
}

.hero {
  position: relative;
  min-height: 52vh;
  display: flex;
  align-items: flex-end;
  padding: 120px 22px 56px;
  background:
    linear-gradient(180deg, rgba(7, 27, 28, 0.72), rgba(7, 27, 28, 0.88)),
    url('https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1800&q=80') center/cover;
}

.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(7, 27, 28, 0.6), transparent 60%);
}

.hero-content {
  position: relative;
  max-width: var(--container-max);
  margin: 0 auto;
  width: 100%;
  color: var(--color-ivory);
  text-align: left;
}

.hero-eyebrow {
  color: var(--color-brass);
  margin: 0 0 12px;
}

.hero h1 {
  margin: 0;
  color: #fff;
  font-size: clamp(40px, 5.5vw, 72px);
  max-width: 16ch;
}

.rule {
  border: none;
  border-top: 1px solid var(--color-line);
  margin: 18px 0;
}

.rule-light {
  border-top-color: rgba(243, 238, 228, 0.3);
  max-width: 320px;
  margin-left: 0;
}

.hero-sub {
  margin: 0;
  max-width: 62ch;
  color: rgba(243, 238, 228, 0.85);
  line-height: 1.65;
}

/* Ritmo editorial: columnas variadas, sin 3 tarjetas iguales */
.services-wrap {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 56px 22px;
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 22px;
}

.service-card {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-top: 2px solid var(--color-brass);
  padding: 28px 26px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  grid-column: span 5;
}

.service-card:nth-child(2n) {
  grid-column: span 7;
}

.service-card:nth-child(3n) {
  grid-column: 2 / span 6;
}

.service-card:nth-child(4n) {
  grid-column: span 4;
  margin-top: 32px;
}

.service-card:nth-child(5n) {
  grid-column: span 8;
}

.service-card:nth-child(6n) {
  grid-column: 4 / span 6;
}

.tag {
  width: fit-content;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-brass-deep);
}

.service-card h3 {
  margin: 10px 0 0;
  font-size: clamp(28px, 3vw, 38px);
  color: var(--color-petrol);
  line-height: 1.05;
}

.service-card .rule {
  margin: 14px 0;
}

.service-card p {
  margin: 0;
  color: #43524f;
  line-height: 1.7;
  flex: 1;
}

.read-more {
  border: none;
  width: fit-content;
  margin-top: 16px;
  padding: 5px 0;
  min-height: 44px;
  background: transparent;
  color: var(--color-petrol);
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.dot {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  border: 1px solid var(--color-brass);
  color: var(--color-brass-deep);
}

.read-more:hover .dot {
  background: var(--color-brass);
  color: #fff;
}

.subscribe {
  max-width: var(--container-max);
  margin: 0 auto 64px;
  background: var(--color-petrol);
  color: var(--color-ivory);
  padding: clamp(28px, 4vw, 48px);
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 28px;
  align-items: center;
}

.eyebrow-on-dark {
  color: var(--color-brass);
}

.subscribe-left h2 {
  margin: 8px 0 10px;
  color: #fff;
  font-size: clamp(30px, 3.5vw, 46px);
}

.subscribe-left p {
  margin: 0;
  color: rgba(243, 238, 228, 0.78);
}

.subscribe-form {
  display: grid;
  gap: 12px;
}

.subscribe-form input {
  border: none;
  border-bottom: 1px solid rgba(243, 238, 228, 0.4);
  border-radius: 0;
  background: transparent;
  color: var(--color-ivory);
  padding: 12px 2px;
  outline: none;
}

.subscribe-form input::placeholder {
  color: rgba(243, 238, 228, 0.55);
}

.subscribe-form input:focus {
  border-bottom-color: var(--color-brass);
}

.subscribe-form button {
  justify-self: start;
  border: 1px solid var(--color-brass);
  padding: 14px 26px;
  min-height: 44px;
  background: var(--color-brass);
  color: #fff;
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  font-weight: 600;
  cursor: pointer;
}

.subscribe-form button:hover {
  background: var(--color-brass-deep);
}

@media (max-width: 900px) {
  .service-card,
  .service-card:nth-child(2n),
  .service-card:nth-child(3n),
  .service-card:nth-child(4n),
  .service-card:nth-child(5n),
  .service-card:nth-child(6n) {
    grid-column: 1 / -1;
    margin-top: 0;
  }

  .subscribe {
    grid-template-columns: 1fr;
    margin-inline: 22px;
  }
}

@media (max-width: 768px) {
  .hero {
    min-height: auto;
    padding-top: 100px;
  }

  .services-wrap {
    grid-template-columns: 1fr;
    padding: 36px 16px;
  }

  .service-card,
  .service-card:nth-child(2n),
  .service-card:nth-child(3n),
  .service-card:nth-child(4n),
  .service-card:nth-child(5n),
  .service-card:nth-child(6n) {
    grid-column: 1 / -1;
  }

  .subscribe {
    margin: 0 16px 40px;
  }
}
</style>

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
        <p class="eyebrow">Servicios inmobiliarios</p>
        <h1>Soluciones premium para compra, venta y renta</h1>
        <p>
          Operamos con procesos claros, acompanamiento cercano y enfoque en resultados.
          Tu patrimonio se gestiona con precision y transparencia.
        </p>
      </div>
    </header>

    <div class="services-wrap">
      <article v-for="service in services" :key="service.title" class="service-card">
        <span class="tag">{{ service.tag }}</span>
        <h3>{{ service.title }}</h3>
        <p>{{ service.description }}</p>
        <button type="button" class="read-more">
          <span class="dot">→</span>
          Conocer mas
        </button>
      </article>
    </div>

    <section class="subscribe">
      <div class="subscribe-left">
        <h2>Recibe novedades del mercado inmobiliario</h2>
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
  font-family: 'Poppins', sans-serif;
  background: #f7f9fd;
  color: #0f172a;
}

.hero {
  position: relative;
  min-height: 360px;
  display: flex;
  align-items: center;
  padding: 120px 22px 78px;
  background:
    linear-gradient(110deg, rgba(7, 24, 44, 0.94), rgba(11, 35, 68, 0.78)),
    url('https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1800&q=80') center/cover;
}

.overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 75% 30%, rgba(220, 176, 102, 0.18), transparent 34%);
}

.hero-content {
  position: relative;
  max-width: 820px;
  margin: 0 auto;
  width: 100%;
  color: #ffffff;
}

.eyebrow {
  margin: 0 0 10px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 700;
  color: #f1cb8f;
}

.hero h1 {
  margin: 0;
  font-size: clamp(30px, 4vw, 46px);
  line-height: 1.08;
}

.hero p {
  margin: 14px 0 0;
  max-width: 700px;
  color: rgba(255, 255, 255, 0.85);
}

.services-wrap {
  max-width: 1240px;
  margin: -46px auto 0;
  padding: 0 22px 56px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.service-card {
  background: #ffffff;
  border: 1px solid #e8edf5;
  border-radius: 18px;
  padding: 24px;
  min-height: 220px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.service-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 34px rgba(15, 23, 42, 0.12);
}

.tag {
  width: fit-content;
  border-radius: 999px;
  padding: 6px 10px;
  background: #edf4ff;
  color: #1e40af;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.service-card h3 {
  margin: 4px 0 0;
  font-size: 24px;
}

.service-card p {
  margin: 0;
  color: #5f6c80;
  line-height: 1.65;
  flex: 1;
}

.read-more {
  border: none;
  width: fit-content;
  background: transparent;
  color: #0f172a;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.dot {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: #f2f5fb;
  transition: all 0.3s ease;
}

.read-more:hover {
  color: #1d4ed8;
}

.read-more:hover .dot {
  background: #2563eb;
  color: #fff;
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.24);
}

.subscribe {
  max-width: 1240px;
  margin: 0 auto 56px;
  border-radius: 16px;
  background: #07182c;
  color: #ffffff;
  padding: 28px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 22px;
}

.subscribe-left h2 {
  margin: 0;
  font-size: clamp(20px, 2.7vw, 30px);
}

.subscribe-left p {
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.75);
}

.subscribe-form {
  display: flex;
  gap: 10px;
  width: min(520px, 100%);
}

.subscribe-form input {
  flex: 1;
  border: 1px solid rgba(255, 255, 255, 0.24);
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border-radius: 999px;
  padding: 12px 16px;
  outline: none;
}

.subscribe-form input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.subscribe-form button {
  border: none;
  border-radius: 999px;
  padding: 12px 18px;
  background: linear-gradient(120deg, #dcb066, #be8d3e);
  color: #0a1e3b;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.subscribe-form button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(220, 176, 102, 0.3);
}

@media (max-width: 1050px) {
  .services-wrap {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .subscribe {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (max-width: 720px) {
  .hero {
    min-height: 320px;
    padding-top: 100px;
  }

  .services-wrap {
    grid-template-columns: 1fr;
    margin-top: -28px;
  }

  .subscribe {
    margin-bottom: 34px;
  }

  .subscribe-form {
    flex-direction: column;
  }
}
</style>

<script setup>
import { ref, onMounted } from 'vue'

const seguridad = ref(0)
const clientes = ref(0)
const transparencia = ref(0)
const animado = ref(false)

const testimonials = [
  { name: 'Mariana P.', role: 'Inversionista', text: 'El proceso fue transparente y bien asesorado. Cerramos en menos tiempo de lo esperado.' },
  { name: 'Carlos R.', role: 'Propietario', text: 'La estrategia comercial y el respaldo juridico marcaron la diferencia en la venta.' }
]

const team = [
  { name: 'Valeria Soto', role: 'Asesora senior' },
  { name: 'Diego Lara', role: 'Legal inmobiliario' },
  { name: 'Andrea Ruiz', role: 'Consultora patrimonial' }
]

onMounted(() => {
  const elements = document.querySelectorAll('.reveal')
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
        if (!animado.value) {
          animateCounters()
          animado.value = true
        }
      }
    })
  }, { threshold: 0.2 })

  elements.forEach((el) => observer.observe(el))
})

const animateCounters = () => {
  const timer = setInterval(() => {
    if (seguridad.value < 100) seguridad.value += 1
    if (clientes.value < 50) clientes.value += 1
    if (transparencia.value < 100) transparencia.value += 1

    if (seguridad.value === 100 && clientes.value === 50 && transparencia.value === 100) {
      clearInterval(timer)
    }
  }, 20)
}
</script>

<template>
  <section class="about-page">
    <header class="hero reveal">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <p class="eyebrow">About us</p>
        <h1>Construimos operaciones seguras y rentables</h1>
        <p class="lead">
          En JAKEDA combinamos estrategia comercial, analisis de mercado y respaldo juridico
          para proteger tu patrimonio en cada decision inmobiliaria.
        </p>
        <button class="cta">Solicitar asesoria premium</button>
      </div>
    </header>

    <section class="split reveal">
      <div class="media-card">
        <img src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1200&q=80" alt="Equipo inmobiliario" />
        <div class="floating-badge">
          <strong>25+</strong>
          <span>Anos de experiencia combinada</span>
        </div>
      </div>

      <div class="copy-card">
        <h2>Nuestra mision</h2>
        <p>
          Ofrecer soluciones inmobiliarias confiables, transparentes y seguras, con acompanamiento
          legal especializado para decisiones con certeza.
        </p>
        <h2>Nuestra vision</h2>
        <p>
          Ser la firma de referencia para quienes buscan vender, rentar o invertir con metodologia,
          etica y alto estandar profesional.
        </p>
      </div>
    </section>

    <section class="stats reveal">
      <article class="stat-card">
        <strong>{{ seguridad }}%</strong>
        <span>Seguridad juridica</span>
      </article>
      <article class="stat-card">
        <strong>+{{ clientes }}</strong>
        <span>Clientes satisfechos</span>
      </article>
      <article class="stat-card">
        <strong>{{ transparencia }}%</strong>
        <span>Transparencia operativa</span>
      </article>
    </section>

    <section class="testimonials reveal">
      <h3>Lo que dicen nuestros clientes</h3>
      <div class="testimonial-grid">
        <article v-for="item in testimonials" :key="item.name" class="testimonial">
          <p>{{ item.text }}</p>
          <strong>{{ item.name }}</strong>
          <span>{{ item.role }}</span>
        </article>
      </div>
    </section>

    <section class="team reveal">
      <h3>Equipo experto</h3>
      <div class="team-grid">
        <article v-for="member in team" :key="member.name" class="member">
          <div class="avatar"></div>
          <strong>{{ member.name }}</strong>
          <span>{{ member.role }}</span>
        </article>
      </div>
    </section>
  </section>
</template>

<style scoped>
.about-page {
  font-family: 'Poppins', sans-serif;
  background: #f8fbff;
  color: #0f172a;
  padding-bottom: 64px;
}

.hero {
  position: relative;
  min-height: 420px;
  padding: 110px 22px 80px;
  background:
    linear-gradient(110deg, rgba(7, 24, 44, 0.94), rgba(12, 39, 72, 0.78)),
    url('https://images.unsplash.com/photo-1556155092-490a1ba16284?auto=format&fit=crop&w=1800&q=80') center/cover;
  overflow: hidden;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 75% 18%, rgba(220, 176, 102, 0.2), transparent 32%);
  animation: pulseGlow 7s ease-in-out infinite;
}

.hero-content {
  position: relative;
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
  color: #fff;
}

.eyebrow {
  margin: 0;
  color: #f0c36f;
  text-transform: uppercase;
  letter-spacing: .12em;
  font-size: 12px;
  font-weight: 700;
}

h1 {
  margin: 10px 0 12px;
  font-size: clamp(34px, 5vw, 58px);
  line-height: 1.05;
}

.lead {
  margin: 0 auto;
  max-width: 760px;
  color: rgba(255, 255, 255, 0.84);
}

.cta {
  margin-top: 24px;
  border: none;
  border-radius: 999px;
  padding: 13px 22px;
  font-weight: 700;
  color: #0b203f;
  background: linear-gradient(120deg, #f1c878, #d8a54d);
  cursor: pointer;
  transition: all .3s ease;
}

.cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 24px rgba(220, 176, 102, 0.36);
}

.split {
  max-width: 1180px;
  margin: -56px auto 0;
  padding: 0 22px;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 16px;
}

.media-card,
.copy-card {
  background: #fff;
  border-radius: 18px;
  border: 1px solid #e7edf6;
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.09);
}

.media-card {
  position: relative;
  overflow: hidden;
}

.media-card img {
  width: 100%;
  height: 100%;
  min-height: 340px;
  object-fit: cover;
}

.floating-badge {
  position: absolute;
  left: 18px;
  bottom: 18px;
  background: rgba(7, 24, 44, 0.92);
  color: #fff;
  border-radius: 14px;
  padding: 12px 14px;
  max-width: 220px;
}

.floating-badge strong {
  display: block;
  color: #f0c36f;
  font-size: 30px;
}

.copy-card {
  padding: 26px;
}

.copy-card h2 {
  margin: 0 0 8px;
  color: #0e2b57;
}

.copy-card p {
  margin: 0 0 18px;
  color: #607087;
  line-height: 1.75;
}

.stats {
  max-width: 1180px;
  margin: 16px auto 0;
  padding: 0 22px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.stat-card {
  border-radius: 14px;
  background: linear-gradient(120deg, #0b3e57, #115e7d);
  color: #fff;
  text-align: center;
  padding: 20px;
  box-shadow: 0 14px 28px rgba(11, 62, 87, 0.2);
}

.stat-card strong { display: block; font-size: 42px; color: #cff2ff; }
.stat-card span { color: rgba(255,255,255,.82); }

.testimonials,
.team {
  max-width: 1180px;
  margin: 16px auto 0;
  padding: 0 22px;
}

.testimonials h3,
.team h3 {
  margin: 0 0 12px;
  color: #0e2b57;
  font-size: 28px;
}

.testimonial-grid,
.team-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.testimonial,
.member {
  background: #fff;
  border: 1px solid #e7edf6;
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.07);
}

.testimonial p { color: #607087; line-height: 1.7; }
.testimonial strong,
.member strong { display: block; margin-top: 8px; color: #0f172a; }
.testimonial span,
.member span { color: #6f7d92; font-size: 13px; }

.member {
  text-align: center;
}

.avatar {
  width: 66px;
  height: 66px;
  margin: 0 auto 10px;
  border-radius: 999px;
  background: linear-gradient(120deg, #d8e8f8, #f0f6ff);
}

.reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity .85s ease, transform .85s ease;
}

.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

@keyframes pulseGlow {
  0%, 100% { opacity: .7; }
  50% { opacity: 1; }
}

@media (max-width: 980px) {
  .split,
  .stats,
  .testimonial-grid,
  .team-grid { grid-template-columns: 1fr; }
}
</style>

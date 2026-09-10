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
        <p class="eyebrow-label hero-eyebrow">Nosotros</p>
        <h1 class="serif-display">Operaciones seguras y rentables, con criterio editorial</h1>
        <hr class="rule rule-light" />
        <p class="lead">
          En JAKEDA combinamos estrategia comercial, analisis de mercado y respaldo juridico
          para proteger tu patrimonio en cada decision inmobiliaria.
        </p>
        <button class="btn-brass">Solicitar asesoria premium</button>
      </div>
    </header>

    <section class="split reveal">
      <div class="media-card">
        <img src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1200&q=80" alt="Equipo inmobiliario" />
        <div class="floating-badge">
          <strong class="serif-display">25+</strong>
          <span>Años de experiencia combinada</span>
        </div>
      </div>

      <div class="copy-card">
        <p class="eyebrow-label">Manifiesto</p>
        <h2 class="serif-display">Nuestra misión</h2>
        <p>
          Ofrecer soluciones inmobiliarias confiables, transparentes y seguras, con acompanamiento
          legal especializado para decisiones con certeza.
        </p>
        <hr class="rule" />
        <h2 class="serif-display">Nuestra visión</h2>
        <p>
          Ser la firma de referencia para quienes buscan vender, rentar o invertir con metodologia,
          etica y alto estandar profesional.
        </p>
      </div>
    </section>

    <section class="stats reveal">
      <article class="stat-card">
        <strong class="serif-display">{{ seguridad }}%</strong>
        <span>Seguridad juridica</span>
      </article>
      <article class="stat-card">
        <strong class="serif-display">+{{ clientes }}</strong>
        <span>Clientes satisfechos</span>
      </article>
      <article class="stat-card">
        <strong class="serif-display">{{ transparencia }}%</strong>
        <span>Transparencia operativa</span>
      </article>
    </section>

    <section class="testimonials reveal">
      <p class="eyebrow-label">Testimonios</p>
      <h3 class="serif-display">Lo que dicen nuestros clientes</h3>
      <hr class="rule" />
      <div class="testimonial-grid">
        <article v-for="item in testimonials" :key="item.name" class="testimonial">
          <p class="quote serif-display">“{{ item.text }}”</p>
          <strong>{{ item.name }}</strong>
          <span>{{ item.role }}</span>
        </article>
      </div>
    </section>

    <section class="team reveal">
      <p class="eyebrow-label">Firma</p>
      <h3 class="serif-display">Equipo experto</h3>
      <hr class="rule" />
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
  font-family: var(--sans);
  background: var(--color-ivory);
  color: var(--color-ink);
  padding-bottom: 72px;
}

.hero {
  position: relative;
  min-height: 62vh;
  padding: 120px 22px 64px;
  display: flex;
  align-items: flex-end;
  background:
    linear-gradient(180deg, rgba(7, 27, 28, 0.7), rgba(7, 27, 28, 0.9)),
    url('https://images.unsplash.com/photo-1556155092-490a1ba16284?auto=format&fit=crop&w=1800&q=80') center/cover;
  overflow: hidden;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(7, 27, 28, 0.55), transparent 60%);
}

.hero-content {
  position: relative;
  max-width: var(--container-max);
  margin: 0 auto;
  width: 100%;
  text-align: left;
  color: var(--color-ivory);
}

.hero-eyebrow {
  color: var(--color-brass);
  margin: 0 0 12px;
}

.hero-content h1 {
  margin: 0;
  color: #fff;
  font-size: clamp(40px, 5.5vw, 72px);
  max-width: 16ch;
}

.rule {
  border: none;
  border-top: 1px solid var(--color-line);
  margin: 20px 0;
}

.rule-light {
  border-top-color: rgba(243, 238, 228, 0.3);
  max-width: 320px;
  margin-left: 0;
}

.lead {
  margin: 0 0 26px;
  max-width: 62ch;
  color: rgba(243, 238, 228, 0.85);
  line-height: 1.65;
}

.btn-brass {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--color-brass);
  color: #fff;
  border: 1px solid var(--color-brass);
  padding: 14px 26px;
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  font-weight: 600;
  cursor: pointer;
}

.btn-brass:hover {
  background: var(--color-brass-deep);
}

/* Misión / visión asimétrico */
.split {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 56px 22px 0;
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: clamp(24px, 4vw, 56px);
  align-items: start;
}

.media-card {
  position: relative;
  overflow: hidden;
  background: var(--color-petrol);
}

.media-card img {
  width: 100%;
  height: 100%;
  min-height: 420px;
  object-fit: cover;
  display: block;
}

.floating-badge {
  position: absolute;
  left: 20px;
  bottom: 20px;
  background: var(--color-ink);
  color: var(--color-ivory);
  border-left: 2px solid var(--color-brass);
  padding: 14px 18px;
  max-width: 240px;
}

.floating-badge strong {
  display: block;
  color: #fff;
  font-size: clamp(38px, 4vw, 52px);
  line-height: 1;
}

.floating-badge span {
  font-size: 13px;
  color: rgba(243, 238, 228, 0.75);
}

.copy-card {
  background: transparent;
  padding: 8px 0 0;
}

.copy-card h2 {
  margin: 8px 0 10px;
  color: var(--color-petrol);
  font-size: clamp(30px, 3.5vw, 44px);
}

.copy-card p {
  margin: 0 0 18px;
  color: #43524f;
  line-height: 1.75;
}

/* Stats como fila editorial con separadores */
.stats {
  max-width: var(--container-max);
  margin: 48px auto 0;
  padding: 8px 22px 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-top: 1px solid var(--color-line);
  border-bottom: 1px solid var(--color-line);
}

.stat-card {
  padding: 28px 24px;
  border-left: 1px solid var(--color-line);
}

.stat-card:first-child {
  border-left: none;
  padding-left: 0;
}

.stat-card strong {
  display: block;
  font-size: clamp(44px, 5vw, 64px);
  color: var(--color-petrol);
  line-height: 1;
}

.stat-card span {
  display: block;
  margin-top: 10px;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-brass-deep);
  font-weight: 600;
}

/* Testimonios: cita grande + cita desplazada */
.testimonials,
.team {
  max-width: var(--container-max);
  margin: 56px auto 0;
  padding: 0 22px;
}

.testimonials h3,
.team h3 {
  margin: 8px 0 0;
  color: var(--color-petrol);
  font-size: clamp(30px, 3.5vw, 46px);
}

.testimonial-grid {
  display: grid;
  grid-template-columns: 7fr 5fr;
  gap: 22px;
  margin-top: 24px;
  align-items: start;
}

.testimonial {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-top: 2px solid var(--color-brass);
  padding: 30px 28px;
}

.testimonial:nth-child(2) {
  margin-top: 40px;
  font-size: 15px;
}

.quote {
  margin: 0;
  color: var(--color-petrol);
  font-size: clamp(24px, 2.6vw, 32px);
  line-height: 1.25;
}

.testimonial:nth-child(2) .quote {
  font-size: clamp(19px, 2vw, 23px);
}

.testimonial strong {
  display: block;
  margin-top: 16px;
  color: var(--color-ink);
}

.testimonial span {
  color: var(--color-muted);
  font-size: 13px;
}

/* Equipo: ritmo desfasado */
.team-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
  margin-top: 24px;
  align-items: start;
}

.member {
  background: transparent;
  border-top: 1px solid var(--color-line);
  padding: 22px 0 0;
}

.member:nth-child(2) {
  margin-top: 36px;
}

.member:nth-child(3) {
  margin-top: 72px;
}

.member strong {
  display: block;
  margin-top: 14px;
  color: var(--color-petrol);
  font-size: 17px;
}

.member span {
  color: var(--color-muted);
  font-size: 13px;
}

.avatar {
  width: 100%;
  aspect-ratio: 4 / 3;
  background: var(--color-ivory-2);
  border: 1px solid var(--color-line);
}

.reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.85s ease, transform 0.85s ease;
}

.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 980px) {
  .split {
    grid-template-columns: 1fr;
  }

  .testimonial-grid {
    grid-template-columns: 1fr;
  }

  .testimonial:nth-child(2) {
    margin-top: 0;
  }

  .stats {
    grid-template-columns: 1fr;
  }

  .stat-card {
    border-left: none;
    border-top: 1px solid var(--color-line);
    padding-left: 0;
  }

  .stat-card:first-child {
    border-top: none;
  }

  .team-grid {
    grid-template-columns: 1fr;
  }

  .member:nth-child(2),
  .member:nth-child(3) {
    margin-top: 0;
  }

  .hero {
    padding: 100px 18px 48px;
    min-height: auto;
  }
}

@media (max-width: 768px) {
  .testimonials,
  .team,
  .split,
  .stats {
    padding-inline: 16px;
  }

  .media-card img {
    min-height: 280px;
  }
}
</style>

<script setup>
import { reactive } from 'vue'

const form = reactive({
  name: '',
  email: '',
  phone: '',
  service: '',
  message: ''
})

const newsletter = reactive({ email: '' })

const submitForm = () => {
  alert('Solicitud enviada correctamente')
}

const submitNewsletter = () => {
  alert('Suscripcion realizada')
}
</script>

<template>
  <div class="contact-page">

    <!-- HERO -->
    <header class="hero">
      <div class="hero-inner">
        <span class="kicker">// CONTACTO</span>
        <h1>Hablemos de tu<br/>proximo hogar</h1>
        <p>Estamos listos para ayudarte con asesoria inmobiliaria y respaldo juridico.</p>
      </div>
    </header>

    <!-- MAIN: info izq + form der -->
    <section class="main-section">
      <div class="container">

        <!-- IZQUIERDA -->
        <div class="info-col">
          <h2>Contacta a nuestros<br/>expertos asesores</h2>
          <p class="desc">Nuestro equipo esta listo para orientarte en la compra, venta o renta de propiedades con respaldo juridico y atencion personalizada.</p>

          <div class="contact-items">
            <div class="contact-item">
              <div class="item-icon">📞</div>
              <div class="item-body">
                <span>Tienes alguna pregunta?</span>
                <strong>(+52) 33 1234 5678</strong>
              </div>
            </div>
            <div class="contact-item">
              <div class="item-icon">✉️</div>
              <div class="item-body">
                <span>Escribenos al correo</span>
                <strong>info@jakedainmobiliaria.com</strong>
              </div>
            </div>
            <div class="contact-item">
              <div class="item-icon">📍</div>
              <div class="item-body">
                <span>Visitanos en nuestra oficina</span>
                <strong>Guadalajara, Jalisco, Mexico</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- DERECHA: formulario -->
        <div class="form-col">
          <div class="form-card">
            <div class="form-header">
              <h3>Enviar solicitud</h3>
              <p>Completa el formulario y un asesor se pondra en contacto contigo.</p>
            </div>
            <form @submit.prevent="submitForm">
              <div class="field">
                <label>Nombre completo</label>
                <input v-model="form.name" type="text" placeholder="Tu nombre" required />
              </div>
              <div class="row-two">
                <div class="field">
                  <label>Correo electronico</label>
                  <input v-model="form.email" type="email" placeholder="correo@ejemplo.com" required />
                </div>
                <div class="field">
                  <label>Telefono</label>
                  <input v-model="form.phone" type="tel" placeholder="+52 33 1234 5678" required />
                </div>
              </div>
              <div class="field">
                <label>Servicio de interes</label>
                <select v-model="form.service" required>
                  <option disabled value="">Selecciona un servicio</option>
                  <option>Compra de propiedad</option>
                  <option>Venta de propiedad</option>
                  <option>Renta de propiedad</option>
                  <option>Asesoria juridica</option>
                </select>
              </div>
              <div class="field">
                <label>Mensaje</label>
                <textarea v-model="form.message" rows="4" placeholder="Cuentanos sobre lo que buscas..." required></textarea>
              </div>
              <button type="submit" class="btn-submit">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                Enviar solicitud
              </button>
            </form>
          </div>
        </div>

      </div>
    </section>

    <!-- BOTTOM: mapa + newsletter -->
    <section class="bottom-section">
      <div class="bottom-container">

        <div class="map-wrap">
          <div class="map-header">
            <h4>Nuestra ubicacion</h4>
            <span>Guadalajara, Jalisco, Mexico</span>
          </div>
          <iframe
            title="Mapa"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
            src="https://maps.google.com/maps?q=Guadalajara%20Jalisco&t=&z=11&ie=UTF8&iwloc=&output=embed"
          ></iframe>
        </div>

        <div class="newsletter">
          <div class="newsletter-inner">
            <span class="nl-kicker">// BOLETÍN INFORMATIVO</span>
            <h3>Recibe las mejores<br/>oportunidades</h3>
            <p>Novedades del mercado inmobiliario directamente en tu correo cada semana.</p>
            <form @submit.prevent="submitNewsletter" class="nl-form">
              <input v-model="newsletter.email" type="email" placeholder="tu@correo.com" required />
              <button type="submit">Suscribirme</button>
            </form>
            <ul class="benefits">
              <li>✓ Nuevas propiedades cada semana</li>
              <li>✓ Tendencias del mercado</li>
              <li>✓ Consejos de inversion</li>
            </ul>
          </div>
        </div>

      </div>
    </section>

  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

* { box-sizing: border-box; }

.contact-page {
  font-family: 'Poppins', sans-serif;
  background: #f5f2ec;
  color: #0f2a44;
}

/* ── HERO ── */
.hero {
  background: #0f2a44;
  padding: 80px 24px 80px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 70% 50%, rgba(242, 201, 76, 0.07) 0%, transparent 60%);
  pointer-events: none;
}

.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 680px;
  margin: 0 auto;
}

.kicker {
  display: inline-block;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: #f2c94c;
  margin-bottom: 20px;
}

.hero-inner h1 {
  font-size: clamp(40px, 6vw, 68px);
  font-weight: 800;
  color: #ffffff;
  line-height: 1.1;
  margin: 0 0 20px;
}

.hero-inner p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.7;
  margin: 0;
}

/* ── MAIN SECTION ── */
.main-section {
  background: #ffffff;
  padding: 72px 0;
}

.container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 48px;
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 72px;
  align-items: start;
}

/* INFO IZQUIERDA */
.info-col {
  display: flex;
  flex-direction: column;
  padding-top: 8px;
}

.info-col h2 {
  font-size: clamp(26px, 3vw, 36px);
  font-weight: 800;
  color: #0f2a44;
  line-height: 1.2;
  margin: 0 0 18px;
}

.desc {
  font-size: 14px;
  color: #65717e;
  line-height: 1.8;
  margin: 0 0 40px;
}

.contact-items {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.item-icon {
  width: 48px;
  height: 48px;
  background: #fdf8ee;
  border: 1.5px solid rgba(242, 201, 76, 0.45);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.item-body span {
  display: block;
  font-size: 12px;
  color: #8a9bac;
  margin-bottom: 3px;
}

.item-body strong {
  font-size: 14px;
  font-weight: 700;
  color: #0f2a44;
}

/* FORM DERECHA */
.form-card {
  background: #f8f6f1;
  border: 1px solid #e5e0d6;
  border-radius: 20px;
  padding: 36px;
  box-shadow: 0 4px 24px rgba(15, 42, 68, 0.07);
}

.form-header {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ece8df;
}

.form-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #0f2a44;
  margin: 0 0 6px;
}

.form-header p {
  font-size: 13px;
  color: #8a9bac;
  margin: 0;
}

form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.row-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field label {
  font-size: 12px;
  font-weight: 600;
  color: #3d5166;
  letter-spacing: 0.02em;
}

input, select, textarea {
  width: 100%;
  border: 1.5px solid #e0d9cc;
  background: #ffffff;
  border-radius: 10px;
  padding: 11px 14px;
  font-size: 14px;
  font-family: 'Poppins', sans-serif;
  color: #0f2a44;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input::placeholder, textarea::placeholder {
  color: #b5ae9f;
}

input:focus, select:focus, textarea:focus {
  border-color: #f2c94c;
  box-shadow: 0 0 0 3px rgba(242, 201, 76, 0.18);
}

textarea {
  resize: vertical;
  border-radius: 10px;
}

.btn-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 13px;
  background: #0f2a44;
  color: #f2c94c;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  margin-top: 4px;
  letter-spacing: 0.03em;
  transition: background 0.2s, box-shadow 0.2s, transform 0.18s;
  box-shadow: 0 4px 16px rgba(15, 42, 68, 0.22);
}

.btn-submit svg {
  stroke: #f2c94c;
}

.btn-submit:hover {
  background: #1a3d5c;
  box-shadow: 0 8px 24px rgba(15, 42, 68, 0.3);
  transform: translateY(-1px);
}

.btn-submit:active {
  transform: translateY(0);
}

/* ── BOTTOM SECTION ── */
.bottom-section {
  padding: 56px 0 64px;
  background: #f5f2ec;
}

.bottom-container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 48px;
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 24px;
  align-items: stretch;
}

/* MAPA */
.map-wrap {
  background: #ffffff;
  border: 1px solid #e5e0d6;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 2px 16px rgba(15, 42, 68, 0.06);
}

.map-header {
  padding: 18px 24px;
  border-bottom: 1px solid #ece8df;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.map-header h4 {
  font-size: 15px;
  font-weight: 700;
  color: #0f2a44;
  margin: 0;
}

.map-header span {
  font-size: 13px;
  color: #8a9bac;
}

.map-wrap iframe {
  width: 100%;
  min-height: 320px;
  border: 0;
  display: block;
}

/* NEWSLETTER */
.newsletter {
  background: #0f2a44;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(15, 42, 68, 0.2);
}

.newsletter-inner {
  padding: 36px 28px;
  color: white;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.nl-kicker {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: #f2c94c;
  margin-bottom: 14px;
  display: block;
}

.newsletter-inner h3 {
  font-size: 26px;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.2;
  margin: 0 0 12px;
}

.newsletter-inner > p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.7;
  margin: 0 0 24px;
  flex: 1;
}

.nl-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.nl-form input {
  background: rgba(255, 255, 255, 0.08);
  border: 1.5px solid rgba(255, 255, 255, 0.14);
  color: white;
  border-radius: 10px;
}

.nl-form input::placeholder {
  color: rgba(255, 255, 255, 0.38);
}

.nl-form input:focus {
  background: rgba(255, 255, 255, 0.13);
  border-color: #f2c94c;
  box-shadow: 0 0 0 3px rgba(242, 201, 76, 0.2);
}

.nl-form button {
  padding: 12px;
  background: #f2c94c;
  color: #0f2a44;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  transition: background 0.2s, transform 0.18s;
  letter-spacing: 0.02em;
}

.nl-form button:hover {
  background: #f5d76e;
  transform: translateY(-1px);
}

.benefits {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.benefits li {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* ── RESPONSIVE ── */
@media (max-width: 980px) {
  .container {
    grid-template-columns: 1fr;
    gap: 40px;
    padding: 0 24px;
  }

  .bottom-container {
    grid-template-columns: 1fr;
    padding: 0 24px;
  }

  .main-section { padding: 52px 0; }
  .bottom-section { padding: 40px 0 52px; }
}

@media (max-width: 640px) {
  .hero { padding: 64px 20px; }
  .form-card { padding: 24px 20px; }
  .row-two { grid-template-columns: 1fr; }
  .newsletter-inner { padding: 28px 20px; }
}
</style>
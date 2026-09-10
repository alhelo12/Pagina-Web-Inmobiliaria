<script setup>
import { reactive, ref } from 'vue'
import AppIcon from '@/components/shared/AppIcon.vue'
import apiClient from '@/api/axios'

const form = reactive({
  name: '',
  email: '',
  phone: '',
  service: '',
  message: ''
})

const newsletter = reactive({ email: '' })

const submitting = ref(false)
const submitStatus = ref('idle') // idle | success | error
const submitMessage = ref('')
const newsletterStatus = ref('idle')
const newsletterMessage = ref('')

const resetForm = () => {
  form.name = ''
  form.email = ''
  form.phone = ''
  form.service = ''
  form.message = ''
}

const submitForm = async () => {
  submitting.value = true
  submitStatus.value = 'idle'
  submitMessage.value = ''

  try {
    const { data } = await apiClient.post('/contact', {
      name: form.name,
      email: form.email,
      phone: form.phone || null,
      service: form.service,
      message: form.message
    })

    submitStatus.value = 'success'
    submitMessage.value = data.message || 'Tu consulta fue recibida. Un asesor te contactara pronto.'
    resetForm()
  } catch (err) {
    submitStatus.value = 'error'
    if (err.response?.data?.detail) {
      const detail = err.response.data.detail
      submitMessage.value = Array.isArray(detail)
        ? detail.map(d => d.msg).join(', ')
        : detail
    } else {
      submitMessage.value = 'No se pudo enviar la consulta. Por favor intenta de nuevo.'
    }
  } finally {
    submitting.value = false
  }
}

const submitNewsletter = () => {
  newsletterStatus.value = 'success'
  newsletterMessage.value = 'Suscripcion realizada. Recibiras nuestras novedades.'
  newsletter.email = ''
}
</script>

<template>
  <div class="contact-page">

    <!-- HERO -->
    <header class="hero">
      <div class="hero-inner">
        <p class="eyebrow-label hero-eyebrow">Contacto</p>
        <h1 class="serif-display">Hablemos de tu<br />próximo hogar</h1>
        <hr class="rule rule-light" />
        <p>Estamos listos para ayudarte con asesoria inmobiliaria y respaldo juridico.</p>
      </div>
    </header>

    <!-- MAIN: info izq + form der -->
    <section class="main-section">
      <div class="container">

        <!-- IZQUIERDA -->
        <div class="info-col">
          <p class="eyebrow-label">Asesoría directa</p>
          <h2 class="serif-display">Contacta a nuestros<br />expertos asesores</h2>
          <hr class="rule" />
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
              <div class="item-icon"><AppIcon name="envelope" :size="20" /></div>
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
              <p class="eyebrow-label">Solicitud</p>
              <h3 class="serif-display">Enviar solicitud</h3>
              <p>Completa el formulario y un asesor se pondra en contacto contigo.</p>
            </div>
            <form @submit.prevent="submitForm">
              <div class="field field-underline">
                <label>Nombre completo</label>
                <input v-model="form.name" type="text" placeholder="Tu nombre" required />
              </div>
              <div class="row-two">
                <div class="field field-underline">
                  <label>Correo electronico</label>
                  <input v-model="form.email" type="email" placeholder="correo@ejemplo.com" required />
                </div>
                <div class="field field-underline">
                  <label>Telefono</label>
                  <input v-model="form.phone" type="tel" placeholder="+52 33 1234 5678" required />
                </div>
              </div>
              <div class="field field-underline">
                <label>Servicio de interes</label>
                <select v-model="form.service" required>
                  <option disabled value="">Selecciona un servicio</option>
                  <option>Compra de propiedad</option>
                  <option>Venta de propiedad</option>
                  <option>Renta de propiedad</option>
                  <option>Asesoria juridica</option>
                </select>
              </div>
              <div class="field field-underline">
                <label>Mensaje</label>
                <textarea v-model="form.message" rows="4" placeholder="Cuentanos sobre lo que buscas..." required></textarea>
              </div>
              <p v-if="submitStatus !== 'idle'" class="form-status" :class="submitStatus">{{ submitMessage }}</p>
              <button type="submit" class="btn-submit" :disabled="submitting">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                {{ submitting ? 'Enviando...' : 'Enviar solicitud' }}
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
            <div>
              <p class="eyebrow-label">Visítanos</p>
              <h4 class="serif-display">Nuestra ubicación</h4>
            </div>
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
            <p class="eyebrow-label eyebrow-on-dark">Boletín informativo</p>
            <h3 class="serif-display">Recibe las mejores<br />oportunidades</h3>
            <hr class="rule rule-light" />
            <p>Novedades del mercado inmobiliario directamente en tu correo cada semana.</p>
            <form @submit.prevent="submitNewsletter" class="nl-form field-underline">
              <input v-model="newsletter.email" type="email" placeholder="tu@correo.com" required />
              <button type="submit">Suscribirme</button>
            </form>
            <p v-if="newsletterStatus !== 'idle'" class="form-status success">{{ newsletterMessage }}</p>
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
* { box-sizing: border-box; }

.contact-page {
  font-family: var(--sans);
  background: var(--color-ivory);
  color: var(--color-ink);
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

.hero-inner .rule-light {
  margin-inline: auto;
}

/* ── HERO petrol editorial ── */
.hero {
  background:
    linear-gradient(180deg, rgba(7, 27, 28, 0.78), rgba(7, 27, 28, 0.94)),
    url('https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1800&q=80') center/cover;
  padding: 120px 24px 72px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 760px;
  margin: 0 auto;
}

.hero-eyebrow {
  color: var(--color-brass);
  margin: 0 0 12px;
}

.hero-inner h1 {
  font-size: clamp(44px, 6vw, 76px);
  font-weight: 500;
  color: #fff;
  line-height: 1.02;
  margin: 0;
}

.hero-inner > p:last-child {
  font-size: 16px;
  color: rgba(243, 238, 228, 0.78);
  line-height: 1.7;
  margin: 0;
}

/* ── MAIN SECTION marfil ── */
.main-section {
  background: var(--color-ivory);
  padding: 64px 0 72px;
}

.container {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 0 32px;
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  gap: clamp(32px, 5vw, 72px);
  align-items: start;
}

.info-col {
  display: flex;
  flex-direction: column;
  padding-top: 8px;
}

.info-col h2 {
  font-size: clamp(34px, 3.5vw, 50px);
  font-weight: 500;
  color: var(--color-petrol);
  line-height: 1.05;
  margin: 8px 0 0;
}

.desc {
  font-size: 15px;
  color: #43524f;
  line-height: 1.75;
  margin: 0 0 36px;
}

.contact-items {
  display: flex;
  flex-direction: column;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 0;
  border-top: 1px solid var(--color-line);
}

.contact-item:last-child {
  border-bottom: 1px solid var(--color-line);
}

.item-icon {
  width: 48px;
  height: 48px;
  background: transparent;
  border: 1px solid var(--color-brass);
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  color: var(--color-brass-deep);
}

.item-body span {
  display: block;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-muted);
  margin-bottom: 4px;
}

.item-body strong {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-petrol);
}

/* FORM editorial: tarjeta marfil, campos subrayados */
.form-card {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-top: 2px solid var(--color-brass);
  padding: 36px 32px;
}

.form-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-line);
}

.form-header h3 {
  font-size: clamp(28px, 3vw, 36px);
  font-weight: 500;
  color: var(--color-petrol);
  margin: 8px 0 6px;
}

.form-header p {
  font-size: 14px;
  color: var(--color-muted);
  margin: 0;
}

form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.row-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-brass-deep);
}

.field-underline input,
.field-underline select,
.field-underline textarea {
  border-radius: 0;
}

.form-status {
  margin: 0;
  padding: 12px 14px;
  font-size: 14px;
  border-left: 2px solid var(--color-brass);
  background: var(--color-ivory);
}

.form-status.success {
  border-left-color: #2e7d4f;
}

.form-status.error {
  border-left-color: #a33b3b;
}

.btn-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 15px;
  background: var(--color-petrol);
  color: #fff;
  border: 1px solid var(--color-petrol);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  cursor: pointer;
  margin-top: 4px;
  transition: background 0.2s;
}

.btn-submit:hover:not(:disabled) {
  background: var(--color-ink);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: wait;
}

.btn-submit svg {
  stroke: var(--color-brass);
}

/* ── BOTTOM asimétrico ── */
.bottom-section {
  padding: 0 0 72px;
  background: var(--color-ivory);
}

.bottom-container {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 0 32px;
  display: grid;
  grid-template-columns: 7fr 5fr;
  gap: 24px;
  align-items: stretch;
}

.map-wrap {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  overflow: hidden;
}

.map-header {
  padding: 24px 24px 18px;
  border-bottom: 1px solid var(--color-line);
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
}

.map-header h4 {
  font-size: clamp(26px, 2.6vw, 34px);
  font-weight: 500;
  color: var(--color-petrol);
  margin: 8px 0 0;
}

.map-header span {
  font-size: 13px;
  color: var(--color-muted);
}

.map-wrap iframe {
  width: 100%;
  min-height: 340px;
  border: 0;
  display: block;
  filter: sepia(0.2) saturate(0.85);
}

.newsletter {
  background: var(--color-petrol);
}

.newsletter-inner {
  padding: 36px 30px;
  color: var(--color-ivory);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.eyebrow-on-dark {
  color: var(--color-brass);
}

.newsletter-inner h3 {
  font-size: clamp(30px, 3vw, 40px);
  font-weight: 500;
  color: #fff;
  line-height: 1.05;
  margin: 8px 0 0;
}

.newsletter-inner > p {
  font-size: 14px;
  color: rgba(243, 238, 228, 0.75);
  line-height: 1.7;
  margin: 0 0 22px;
}

.nl-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 18px;
}

.nl-form input {
  background: transparent;
  color: var(--color-ivory);
}

.nl-form input::placeholder {
  color: rgba(243, 238, 228, 0.45);
}

.nl-form button {
  padding: 14px;
  background: var(--color-brass);
  color: #fff;
  border: 1px solid var(--color-brass);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  cursor: pointer;
}

.nl-form button:hover {
  background: var(--color-brass-deep);
}

.nl-form + .form-status {
  background: rgba(255, 255, 255, 0.08);
  color: var(--color-ivory);
  margin-bottom: 16px;
}

.benefits {
  list-style: none;
  padding: 18px 0 0;
  margin: auto 0 0;
  border-top: 1px solid rgba(243, 238, 228, 0.25);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.benefits li {
  font-size: 13px;
  color: rgba(243, 238, 228, 0.7);
}

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

  .main-section { padding: 48px 0; }
  .bottom-section { padding-bottom: 52px; }
}

@media (max-width: 768px) {
  .hero { padding: 100px 20px 56px; }
  .form-card { padding: 28px 20px; }
  .row-two { grid-template-columns: 1fr; }
  .newsletter-inner { padding: 28px 20px; }
  .container,
  .bottom-container { padding: 0 16px; }
  .map-header { flex-direction: column; align-items: flex-start; }
}
</style>

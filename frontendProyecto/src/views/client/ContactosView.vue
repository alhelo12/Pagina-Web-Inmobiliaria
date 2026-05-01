<script setup>
import { reactive } from 'vue'

const form = reactive({
  email: '',
  phone: '',
  name: '',
  service: '',
  message: ''
})

const newsletter = reactive({ email: '' })

const contactCards = [
  { title: 'Telefono', value: '(+52) 33 1234 5678', note: 'Atencion de lunes a sabado' },
  { title: 'Correo', value: 'info@jakedainmobiliaria.com', note: 'Respuesta en horario laboral' },
  { title: 'Oficina', value: 'Guadalajara, Jalisco', note: 'Agenda previa para visitas' }
]

const submitForm = () => {
  alert('Solicitud enviada correctamente')
}

const submitNewsletter = () => {
  alert('Suscripcion realizada')
}
</script>

<template>
  <section class="contact-page">
    <header class="hero">
      <div class="hero-inner">
        <p>Contacto</p>
        <h1>Contact Us</h1>
        <span>Estamos listos para ayudarte con asesoria inmobiliaria y respaldo juridico.</span>
      </div>
    </header>

    <section class="content-wrap">
      <div class="form-area">
        <form class="main-form" @submit.prevent="submitForm">
          <div class="row two">
            <input v-model="form.email" type="email" placeholder="Email" required />
            <input v-model="form.phone" type="tel" placeholder="Phone" required />
          </div>

          <div class="row">
            <input v-model="form.name" type="text" placeholder="Name" required />
          </div>

          <div class="row">
            <select v-model="form.service" required>
              <option disabled value="">Servicio de interes</option>
              <option>Compra de propiedad</option>
              <option>Venta de propiedad</option>
              <option>Renta de propiedad</option>
              <option>Asesoria juridica</option>
            </select>
          </div>

          <div class="row">
            <textarea v-model="form.message" rows="5" placeholder="Message" required></textarea>
          </div>

          <button type="submit">Enviar solicitud</button>
        </form>

        <aside class="newsletter">
          <h3>Our Newsletters</h3>
          <p>Recibe oportunidades y novedades del mercado inmobiliario.</p>
          <form @submit.prevent="submitNewsletter">
            <input v-model="newsletter.email" type="email" placeholder="Email" required />
            <button type="submit">Suscribirme</button>
          </form>
        </aside>
      </div>

      <div class="cards">
        <article v-for="card in contactCards" :key="card.title" class="card">
          <h4>{{ card.title }}</h4>
          <strong>{{ card.value }}</strong>
          <p>{{ card.note }}</p>
        </article>
      </div>

      <div class="map-wrap">
        <iframe
          title="Mapa"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
          src="https://maps.google.com/maps?q=Guadalajara%20Jalisco&t=&z=11&ie=UTF8&iwloc=&output=embed"
        ></iframe>
      </div>
    </section>
  </section>
</template>

<style scoped>
.contact-page {
  font-family: 'Poppins', sans-serif;
  background: #ffffff;
  color: #0f172a;
}

.hero {
  background: #d9e9f1;
  padding: 110px 22px 94px;
  text-align: center;
}

.hero-inner p {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #2f6f86;
  font-size: 12px;
  font-weight: 700;
}

.hero-inner h1 {
  margin: 8px 0 10px;
  font-size: clamp(38px, 5vw, 72px);
  color: #0e2238;
}

.hero-inner span {
  color: #4d6177;
}

.content-wrap {
  max-width: 1180px;
  margin: -52px auto 56px;
  padding: 0 22px;
  display: grid;
  gap: 24px;
}

.form-area {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

.main-form {
  background: #f7fcff;
  border: 1px solid #dcebf1;
  border-radius: 18px;
  padding: 20px;
}

.row { margin-bottom: 12px; }
.row.two { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }

input,
select,
textarea {
  width: 100%;
  border: 1px solid #cce0ea;
  background: #e8f4fa;
  border-radius: 999px;
  padding: 12px 14px;
  outline: none;
  transition: border-color .3s ease, box-shadow .3s ease;
}

textarea {
  border-radius: 16px;
  resize: vertical;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #6ca4bb;
  box-shadow: 0 0 0 3px rgba(108, 164, 187, 0.18);
}

.main-form button,
.newsletter button {
  border: none;
  border-radius: 999px;
  padding: 12px 18px;
  background: linear-gradient(120deg, #1b4b5e, #2f7186);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  transition: all .3s ease;
}

.main-form button:hover,
.newsletter button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(47, 113, 134, 0.28);
}

.newsletter {
  background:
    linear-gradient(140deg, rgba(33, 91, 109, .94), rgba(30, 77, 94, .92)),
    url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=900&q=70') center/cover;
  border-radius: 18px;
  color: #fff;
  padding: 20px;
}

.newsletter h3 {
  margin: 0;
  font-size: 26px;
}

.newsletter p {
  color: rgba(255, 255, 255, 0.82);
}

.newsletter input {
  background: rgba(255, 255, 255, 0.9);
  border-color: transparent;
  margin-bottom: 10px;
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.card {
  border: 1px solid #e4edf2;
  border-radius: 14px;
  padding: 16px;
  background: #fff;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.06);
}

.card h4 {
  margin: 0;
  color: #2f7186;
}

.card strong {
  display: block;
  margin-top: 10px;
  color: #0f172a;
}

.card p {
  margin: 8px 0 0;
  color: #607387;
  font-size: 13px;
}

.map-wrap {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #dce7ee;
}

.map-wrap iframe {
  width: 100%;
  min-height: 300px;
  border: 0;
}

@media (max-width: 980px) {
  .form-area {
    grid-template-columns: 1fr;
  }

  .cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .row.two {
    grid-template-columns: 1fr;
  }

  .hero {
    padding-top: 98px;
  }
}
</style>

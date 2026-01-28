<template>
  <section class="contact-section">
    <!-- Encabezado -->
    <div class="header fade-down">
      <h1>Contáctanos</h1>
      <p>Estamos aquí para brindarte asesoría integral con respaldo jurídico</p>
    </div>

    <div class="contact-container">
      <!-- Información -->
      <div class="contact-info fade-left">
        <div class="info-item" v-for="item in info" :key="item.title">
          <div class="icon">{{ item.icon }}</div>
          <div>
            <h4>{{ item.title }}</h4>
            <p v-for="line in item.lines" :key="line">{{ line }}</p>
          </div>
        </div>
      </div>

      <!-- Formulario -->
      <div class="contact-form fade-right">
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label>Nombre Completo</label>
            <input v-model="form.nombre" type="text" />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" />
          </div>

          <div class="form-group">
            <label>Teléfono</label>
            <input v-model="form.telefono" type="tel" />
          </div>

          <div class="form-group">
            <label>Servicio de Interés</label>
            <select v-model="form.servicio">
              <option value="">Selecciona un servicio</option>
              <option>Compra de propiedad</option>
              <option>Venta de propiedad</option>
              <option>Renta de propiedad</option>
              <option>Trámites notariales</option>
              <option>Asesoría Jurídica</option>
              <option>Regularización</option>
              <option>Otros</option>


            </select>
          </div>

          <div class="form-group">
            <label>Mensaje</label>
            <textarea id="message" class="form-control" required placeholder="Describe tu consulta o necesidad..."></textarea>
          </div>

          <button class="btn-submit">Solicitar Asesoría</button>
        </form>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: "ContactosView",
  data() {
    return {
      form: {
        nombre: "",
        email: "",
        telefono: "",
        servicio: "",
        mensaje: "",
      },
      info: [
        {
          icon: "📍",
          title: "Oficina Principal",
          lines: ["Próximamente en ubicación céntrica"],
        },
        {
          icon: "📞",
          title: "Teléfono",
          lines: ["+52 1 33 1234 5678"],
        },
        {
          icon: "✉️",
          title: "Email",
          lines: ["info@jakedainmobiliaria.com"],
        },
        {
          icon: "⏰",
          title: "Horario de Atención",
          lines: [
            "Lunes - Viernes: 9:00 AM - 6:00 PM",
            "Sábados: 10:00 AM - 2:00 PM",
          ],
        },
      ],
    };
  },
  methods: {
    submitForm() {
      alert("Formulario enviado correctamente");
    },
  },
};
</script>

<style scoped>
/* ---------- BASE ---------- */
.contact-section {
  padding: 60px 8%;
  font-family: "Segoe UI", sans-serif;
  background: #fff;
}

.header {
  text-align: center;
  margin-bottom: 50px;
}

.header h1 {
  font-size: 42px;
  color: #0b2c5d;
}

.header p {
  font-size: 15px;
  color: #6b7280;
}

/* ---------- LAYOUT ---------- */
.contact-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;
}

/* ---------- INFO ---------- */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.info-item {
  display: flex;
  gap: 15px;
}

.icon {
  width: 50px;
  height: 50px;
  background: #0b2c5d;
  border-radius: 50%;
  color: #fff;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.info-item h4 {
  margin: 0;
  color: #0b2c5d;
}

.info-item p {
  margin: 4px 0;
  font-size: 14px;
  color: #374151;
}

/* ---------- FORM ---------- */
.contact-form {
  background: #f9fafb;
  padding: 35px;
  border-radius: 12px;
}

.form-group {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
}

label {
  font-size: 14px;
  margin-bottom: 6px;
}

input,
select,
textarea {
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: #0b2c5d;
}

.btn-submit {
  width: 100%;
  background: #d4a72c;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

/* ---------- ANIMACIONES ---------- */
.fade-down {
  animation: fadeDown 0.8s ease forwards;
}

.fade-left {
  animation: fadeLeft 1s ease forwards;
}

.fade-right {
  animation: fadeRight 1s ease forwards;
}

@keyframes fadeDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeLeft {
  from {
    opacity: 0;
    transform: translateX(-40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeRight {
  from {
    opacity: 0;
    transform: translateX(40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* ---------- RESPONSIVE ---------- */
@media (max-width: 900px) {
  .contact-container {
    grid-template-columns: 1fr;
  }
}
</style>

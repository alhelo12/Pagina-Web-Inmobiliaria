<template>
  <section class="services">
    <h2>Nuestros Servicios</h2>

    <div class="grid">
      <div class="card">
        <h3>Asesoramiento Integral</h3>
        <p>Te guiamos en compra, venta y renta con respaldo profesional.</p>
      </div>

      <div class="card">
        <h3>Respaldo Jurídico</h3>
        <p>Acompañamiento legal en todos los procesos.</p>
      </div>

      <div class="card">
        <h3>Regularización Documental</h3>
        <p>Gestión de escrituras y contratos.</p>
      </div>

      <div class="card">
        <h3>Asesoría Fiscal</h3>
        <p>Orientación SAT y trámites fiscales.</p>
      </div>
    </div>
  </section>
</template>

<script setup>
</script>

<style scoped>
.services {
  padding: 60px 40px;
  text-align: center;
}

.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-top: 30px;
}

.card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0,0,0,.1);
}
</style>

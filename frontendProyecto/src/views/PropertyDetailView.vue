<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const propertyId = route.params.id
</script>

<template>
  <section class="detail">
    <div class="container">
      <h1>Detalle de Propiedad</h1>

      <p class="id">
        Propiedad #{{ propertyId }}
      </p>

      <div class="placeholder">
        Aquí se mostrarán:
        <ul>
          <li>Galería de imágenes</li>
          <li>Precio</li>
          <li>Descripción</li>
          <li>Ubicación</li>
          <li>Contacto / WhatsApp</li>
        </ul>
      </div>
    </div>
  </section>
</template>

<style scoped>
.detail {
  padding: 60px 20px;
  font-family: 'Poppins', sans-serif;
}

.container {
  max-width: 1000px;
  margin: auto;
}

h1 {
  font-size: 32px;
  margin-bottom: 10px;
}

.id {
  color: #777;
  margin-bottom: 30px;
}

.placeholder {
  background: #f7f7f7;
  padding: 30px;
  border-radius: 12px;
  color: #444;
}

.placeholder ul {
  margin-top: 10px;
  padding-left: 20px;
}
</style>

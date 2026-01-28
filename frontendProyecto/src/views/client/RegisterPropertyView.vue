<script setup>
import { ref } from 'vue'

const property = ref({
  title: '',
  type: '',
  operation: '',
  price: '',
  address: '',
  description: ''
})

const submitProperty = () => {
  console.log('Propiedad enviada:', property.value)
  alert('Propiedad enviada a revisión')
}
</script>

<template>
  <div class="property-container">
    <h1>Registrar propiedad</h1>
    <p class="subtitle">
      Completa la información para que un asesor revise tu propiedad
    </p>

    <form @submit.prevent="submitProperty">
      <input type="text" placeholder="Título de la propiedad" v-model="property.title" required />

      <select v-model="property.type" required>
        <option value="">Tipo de propiedad</option>
        <option>Casa</option>
        <option>Departamento</option>
        <option>Terreno</option>
      </select>

      <select v-model="property.operation" required>
        <option value="">Operación</option>
        <option>Venta</option>
        <option>Renta</option>
      </select>

      <input type="number" placeholder="Precio" v-model="property.price" required />
      <input type="text" placeholder="Dirección" v-model="property.address" required />

      <textarea placeholder="Descripción" v-model="property.description"></textarea>

      <button type="submit">Enviar a revisión</button>
    </form>
  </div>
</template>

<style scoped>
.property-container {
  max-width: 600px;
  margin: 60px auto;
  padding: 30px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0,0,0,.08);
  font-family: 'Poppins', sans-serif;
}

h1 {
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  color: #777;
  margin-bottom: 24px;
}

input, select, textarea {
  width: 100%;
  padding: 12px;
  margin-bottom: 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

textarea {
  min-height: 100px;
  resize: vertical;
}

button {
  width: 100%;
  padding: 12px;
  background: #333;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

button:hover {
  background: #111;
}
</style>

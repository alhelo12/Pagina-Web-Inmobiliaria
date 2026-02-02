<template>
  <section class="services">
    <h1>Nuestros Servicios</h1>
    <p class="subtitle">
      Soluciones inmobiliarias con respaldo jurídico y profesional
    </p>

    <div class="services-grid">
      <div class="service-card" v-for="service in services" :key="service.title">
        <div class="icon">{{ service.icon }}</div>
        <h3>{{ service.title }}</h3>
        <p>{{ service.description }}</p>
      </div>
    </div>
  </section>
</template>

<script setup>
const services = [
  {
    icon: '🏠',
    title: 'Compra de Inmuebles',
    description: 'Te acompañamos en todo el proceso de compra con asesoría legal.'
  },
  {
    icon: '📄',
    title: 'Venta de Propiedades',
    description: 'Promoción profesional y cierre seguro de operaciones.'
  },
  {
    icon: '🔑',
    title: 'Renta de Inmuebles',
    description: 'Contratos claros y selección confiable de inquilinos.'
  },
  {
    icon: '⚖️',
    title: 'Asesoría Jurídica',
    description: 'Respaldo legal en cada operación inmobiliaria.'
  }
]
</script>


<style scoped>
.services {
  padding: 120px 20px;
  max-width: 1200px;
  margin: auto;
  text-align: center;
}

.subtitle {
  max-width: 600px;
  margin: 10px auto 50px;
  color: #666;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.service-card {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,.08);
  transition: transform .3s;
}

.service-card:hover {
  transform: translateY(-8px);
}

.icon {
  font-size: 40px;
  margin-bottom: 15px;
}
</style>

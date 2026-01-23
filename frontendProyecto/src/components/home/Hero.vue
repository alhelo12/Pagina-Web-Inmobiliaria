<script setup>
import SearchBar from './SearchBar.vue';
</script>

<template>
  <section class="hero">
    <div class="overlay">
      <h1>JAKEDA INMOBILIARIA</h1>
      <p>Asesoría integral con respaldo jurídico para compra, venta y renta</p>

      <!-- BUSCADOR ENCIMADO -->
      <SearchBar />
    </div>
  </section>
</template>

<style scoped>
.hero {
  background-image: url('src/assets/images/fondo.png');
  background-size: cover;
  background-position: center;
  height: 35vh;
  position: relative;
}

.overlay {
  background: rgba(0,0,0,.45);
  height: 100%;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 4rem;
}
</style>

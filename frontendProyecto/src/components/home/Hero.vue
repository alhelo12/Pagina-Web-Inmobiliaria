<template>
  <section class="hero">
    <div class="overlay"></div>

    <div class="hero-content">
      <h1>JAKEDA INMOBILIARIA</h1>
      <p>
        Asesoría integral con respaldo jurídico para compra,
        venta y renta de inmuebles
      </p>

      <div class="search-box">
        <input type="text" placeholder="Ubicación" />
        <select>
          <option>Tipo de propiedad</option>
          <option>Casa</option>
          <option>Departamento</option>
          <option>Terreno</option>
        </select>
        <select>
          <option>Operación</option>
          <option>Venta</option>
          <option>Renta</option>
        </select>
        <button>Buscar propiedades</button>
      </div>
    </div>
  </section>
</template>

<script setup>
</script>

<style scoped>
.hero {
  position: relative;
  min-height: 80vh;
  background-image: url('@/assets/images/hero.jpg');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Poppins', sans-serif;
}

.overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
}

.hero-content {
  position: relative;
  max-width: 1000px;
  width: 100%;
  padding: 0 24px;
  color: white;
  text-align: center;
}

.hero-content h1 {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
}

.hero-content p {
  font-size: 18px;
  max-width: 700px;
  margin: 0 auto 40px;
  line-height: 1.6;
}

/* Search box */
.search-box {
  background: white;
  padding: 20px;
  border-radius: 10px;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  gap: 12px;
}

.search-box input,
.search-box select {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.search-box button {
  padding: 12px 24px;
  background: #f5a623;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.search-box button:hover {
  background: #e6951c;
}

/* RESPONSIVE */
@media (max-width: 900px) {
  .hero-content h1 {
    font-size: 36px;
  }

  .search-box {
    grid-template-columns: 1fr;
  }

  .search-box button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .hero {
    min-height: 70vh;
  }

  .hero-content h1 {
    font-size: 28px;
  }

  .hero-content p {
    font-size: 16px;
  }
}
</style>

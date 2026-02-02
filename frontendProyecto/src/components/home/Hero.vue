<template>
  <section class="hero">
    <div class="overlay"></div>

    <div class="hero-content">
      <h1>JAKEDA INMOBILIARIA</h1>
      <p>
        Asesoría integral con respaldo jurídico para compra,
        venta y renta de inmuebles
      </p>

      <!-- Lazy SearchBar -->
      <Suspense>
        <template #default>
          <SearchBar />
        </template>

        <template #fallback>
          <div class="search-skeleton">
            Cargando buscador...
          </div>
        </template>
      </Suspense>
    </div>
  </section>
</template>

<script setup>
import { defineAsyncComponent } from 'vue'

const SearchBar = defineAsyncComponent(() =>
  import('@/components/home/SearchBar.vue')
)
</script>

<style scoped>
.hero {
  padding-top: 80px;
  position: relative;
  min-height: 80vh;
  background-image: url('@/assets/images/fondo.webp'); /* 👉 usa webp */
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

/* Skeleton */
.search-skeleton {
  background: rgba(255,255,255,.2);
  padding: 24px;
  border-radius: 10px;
  color: white;
}

/* Responsive */
@media (max-width: 900px) {
  .hero-content h1 {
    font-size: 36px;
  }
}

@media (max-width: 480px) {
  .hero {
    min-height: 70vh;
  }

  .hero-content h1 {
    font-size: 28px;
  }
}
</style>

<script setup>
import Navbar from './components/layout/Navbar.vue'
import Footer from './components/layout/Footer.vue'
</script>

<template>
  <div class="layout">
    <Navbar />

    <main class="content">
      <RouterView />
    </main>

    <Footer />
  </div>
</template>

<style>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.content {
  flex: 1;
  padding-top: 60px; /* altura real del navbar */
}
</style>


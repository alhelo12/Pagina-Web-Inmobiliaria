<script setup>
import Navbar from './components/layout/Navbar.vue'
import Footer from './components/layout/Footer.vue'
import ToastContainer from '@/components/shared/ToastContainer.vue'
</script>

<template>
  <div class="layout">
    <a class="skip-link" href="#main">Saltar al contenido</a>
    <Navbar />
    <ToastContainer />

    <main id="main" class="content">
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
  padding-top: 0;
  background: var(--color-ivory);
  min-height: 100dvh;
}
.content:has(.workspace-shell),
.content:has(.auth-split),
.content:has(.account-state-page) {
  background: var(--color-ivory);
}
</style>


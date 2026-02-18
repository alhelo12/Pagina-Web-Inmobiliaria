<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  // luego conectaremos con auth real
  router.push('/login')
}
</script>

<template>
  <div class="advisor-container">
    <router-view />
  </div>
</template>

<style scoped>
.advisor-container {
  padding: 100px 20px 40px; /* espacio para el navbar */
  max-width: 1200px;
  margin: auto;
}
</style>

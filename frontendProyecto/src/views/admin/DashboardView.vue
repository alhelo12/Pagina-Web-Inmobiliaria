<template>
  <div>
    <h1>Dashboard</h1>

    <div class="stats">
      <div class="card">🏠 {{ properties }} Propiedades</div>
      <div class="card">👥 {{ users }} Usuarios</div>
      <div class="card">💼 {{ advisors }} Asesores</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const properties = ref(18)
const users = ref(42)
const advisors = ref(5)
</script>

<style scoped>
.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 30px;
}

.card {
  background: white;
  padding: 25px;
  border-radius: 14px;
  font-size: 18px;
  box-shadow: 0 10px 25px rgba(0,0,0,.1);
}
</style>

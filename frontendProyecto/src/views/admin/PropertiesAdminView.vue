<template>
  <div>
    <h1>Propiedades</h1>

    <table>
      <tr>
        <th>Título</th>
        <th>Precio</th>
        <th>Acciones</th>
      </tr>

      <tr v-for="p in properties" :key="p.id">
        <td>{{ p.title }}</td>
        <td>${{ p.price.toLocaleString() }}</td>
        <td>
          <button>✏️</button>
          <button>🗑️</button>
        </td>
      </tr>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const properties = ref([
  { id: 1, title: 'Casa Moderna', price: 2500000 },
  { id: 2, title: 'Departamento Centro', price: 1800000 }
])
</script>

<style scoped>
table {
  width: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

th, td {
  padding: 14px;
  border-bottom: 1px solid #eee;
}
</style>

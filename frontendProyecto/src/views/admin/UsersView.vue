<template>
  <div>
    <h1>Usuarios</h1>

    <table>
      <tr>
        <th>Nombre</th>
        <th>Rol</th>
        <th>Estado</th>
      </tr>

      <tr v-for="u in users" :key="u.id">
        <td>{{ u.name }}</td>
        <td>{{ u.role }}</td>
        <td>{{ u.active ? 'Activo' : 'Inactivo' }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const users = ref([
  { id: 1, name: 'Juan Pérez', role: 'Admin', active: true },
  { id: 2, name: 'Ana López', role: 'Asesor', active: true },
  { id: 3, name: 'Carlos Ruiz', role: 'Cliente', active: false }
])
</script>

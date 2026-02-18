<template>
  <div :class="['admin-layout', { dark: darkMode }]">
    <!-- CONTENIDO -->
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const darkMode = ref(false)

onMounted(() => {
  darkMode.value = localStorage.getItem('dark') === 'true'
})

const toggleDark = () => {
  darkMode.value = !darkMode.value
  localStorage.setItem('dark', darkMode.value)
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f4f6f9;
}

.admin-layout.dark {
  background: #0f172a;
  color: #e5e7eb;
}

.content {
  padding: 30px;
}
</style>

<template>
  <div :class="['admin-layout', { dark: darkMode }]">
    <Sidebar @toggleDark="toggleDark" />

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '@/components/admin/Sidebar.vue'

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
  display: flex;
  min-height: 100vh;
  background: #f4f6f9;
}

.admin-layout.dark {
  background: #0f172a;
  color: #e5e7eb;
}

.content {
  flex: 1;
  padding: 30px;
}
</style>

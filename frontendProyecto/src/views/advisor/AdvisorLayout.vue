<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const auth   = useAuthStore()

const logout = () => {
  auth.logout()
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
  padding: 100px 20px 40px;
  max-width: 1200px;
  margin: auto;
}
</style>

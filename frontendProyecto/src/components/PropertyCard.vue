<script setup>
import { useAuthStore } from '@/stores/authStore'
import { useFavoritesStore } from '@/stores/favoritesStore'

const props = defineProps({
  id:    Number,
  title: String,
  price: Number,
  city:  String,
  type:  String,
  image: String
})

const auth     = useAuthStore()
const favStore = useFavoritesStore()

const typeLabel = {
  house: 'Casa', apartment: 'Departamento',
  land: 'Terreno', commercial: 'Local'
}

const toggle = async (e) => {
  e.preventDefault()
  e.stopPropagation()
  if (!auth.isLogged || auth.role !== 'client') return
  await favStore.toggleFavorite(props.id)
}
</script>

<template>
  <div class="card">
    <button
      v-if="auth.isLogged && auth.role === 'client'"
      class="fav-btn"
      :class="{ active: favStore.isFavorite(id) }"
      @click="toggle"
    >♥</button>

    <img :src="image" :alt="title" loading="lazy" />

    <div class="body">
      <h3>{{ title }}</h3>
      <p>{{ city }} · {{ typeLabel[type] ?? type }}</p>
      <strong>${{ Number(price).toLocaleString('es-MX') }} MXN</strong>
    </div>
  </div>
</template>

<style scoped>
.card {
  position: relative; background: white; border-radius: 14px;
  overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,.08);
  transition: all .25s ease; cursor: pointer;
}
.card:hover { transform: translateY(-6px); box-shadow: 0 18px 40px rgba(0,0,0,.12); }
.card img   { width: 100%; height: 220px; object-fit: cover; display: block; }
.body         { padding: 16px; }
.body h3      { font-size: 16px; margin-bottom: 6px; font-weight: 600; }
.body p       { font-size: 13px; color: #777; margin-bottom: 8px; }
.body strong  { font-size: 16px; color: #111; }
.fav-btn {
  position: absolute; top: 10px; right: 10px;
  background: white; border: none; width: 36px; height: 36px;
  border-radius: 50%; font-size: 18px; cursor: pointer;
  transition: .2s; box-shadow: 0 4px 10px rgba(0,0,0,.15);
  display: flex; align-items: center; justify-content: center; color: #ccc;
}
.fav-btn.active { color: #ef4444; transform: scale(1.15); }
</style>

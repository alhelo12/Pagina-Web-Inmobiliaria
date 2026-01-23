<template>
  <div class="card">
    <img :src="property.image" />
    <div class="info">
      <h3>{{ property.title }}</h3>
      <p class="price">{{ property.price }}</p>
      <p>{{ property.location }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  property: Object
})
</script>

<style scoped>
.card {
  border: 1px solid #eee;
  border-radius: 10px;
  overflow: hidden;
}

img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.price {
  color: #c9a23f;
  font-weight: bold;
}
</style>

<script setup>
defineProps({
  id: Number,
  title: String,
  city: String,
  type: String,
  price: Number,
  image: String
})
</script>

<template>
  <div class="card">
    <img :src="image" alt="Propiedad" />

    <div class="card-body">
      <h3>{{ title }}</h3>
      <p>{{ city }} · {{ type }}</p>
      <strong>
        ${{ price.toLocaleString() }} MXN
      </strong>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: white;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(0,0,0,0.08);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-6px);
  box-shadow: 0 18px 40px rgba(0,0,0,0.12);
}

.card img {
  width: 100%;
  height: 220px;
  object-fit: cover;
}

.card-body {
  padding: 18px;
}

.card-body h3 {
  font-size: 17px;
  margin-bottom: 6px;
}

.card-body p {
  font-size: 14px;
  color: #777;
  margin-bottom: 8px;
}

.card-body strong {
  font-size: 16px;
  color: #0d2c54;
}
</style>

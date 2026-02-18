<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

/* =========================
   FORM STATE
========================= */
const form = ref({
  title: '',
  description: '',
  price: '',
  property_type: '',
  transaction_type: 'sale',
  address: '',
  city: '',
  bedrooms: 0,
  bathrooms: 0,
  square_meters: 0,
  image: ''
})

const loading = ref(false)
const success = ref(false)

/* =========================
   SUBMIT (MOCK)
========================= */
const submitProperty = async () => {
  loading.value = true

  // 🔥 simulación llamada API
  await new Promise(r => setTimeout(r, 1200))

  console.log('Propiedad enviada:', {
    ...form.value,
    status: 'pending'
  })

  loading.value = false
  success.value = true

  // redirigir después de 2s
  setTimeout(() => {
    router.push('/propiedades')
  }, 2000)
}
</script>

<template>
  <section class="create">
    <div class="container">

      <h1>Publicar Propiedad</h1>
      <p class="subtitle">
        Tu propiedad será revisada por un asesor antes de publicarse.
      </p>

      <!-- MENSAJE ÉXITO -->
      <div v-if="success" class="success">
        ✅ Propiedad enviada correctamente.  
        Redirigiendo a propiedades...
      </div>

      <!-- FORM -->
      <form v-else @submit.prevent="submitProperty" class="form">

        <div class="grid">

          <input v-model="form.title" placeholder="Título" required />

          <input
            v-model="form.price"
            type="number"
            placeholder="Precio (MXN)"
            required
          />

          <select v-model="form.property_type" required>
            <option value="">Tipo de propiedad</option>
            <option>Casa</option>
            <option>Departamento</option>
            <option>Terreno</option>
            <option>Local</option>
          </select>

          <select v-model="form.transaction_type">
            <option value="sale">Venta</option>
            <option value="rent">Renta</option>
          </select>

          <input v-model="form.city" placeholder="Ciudad" required />
          <input v-model="form.address" placeholder="Dirección" required />

          <input v-model.number="form.bedrooms" type="number" placeholder="Recámaras" />
          <input v-model.number="form.bathrooms" type="number" placeholder="Baños" />
          <input v-model.number="form.square_meters" type="number" placeholder="m²" />

          <input v-model="form.image" placeholder="URL imagen principal" />
        </div>

        <textarea
          v-model="form.description"
          placeholder="Descripción de la propiedad"
          rows="4"
        />

        <button :disabled="loading">
          {{ loading ? 'Enviando...' : 'Publicar propiedad' }}
        </button>

      </form>
    </div>
  </section>
</template>

<style scoped>
.create {
  padding: 60px 20px;
  background: #f7f9fc;
  min-height: 80vh;
  font-family: 'Poppins', sans-serif;
}

.container {
  max-width: 900px;
  margin: auto;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 15px 40px rgba(0,0,0,0.08);
}

h1 {
  text-align: center;
  font-size: 32px;
  margin-bottom: 10px;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.success {
  background: #e8f7ee;
  color: #1e7e34;
  padding: 16px;
  border-radius: 10px;
  text-align: center;
  font-weight: 500;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

input,
select,
textarea {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 14px;
}

textarea {
  resize: none;
}

button {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 14px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

button:hover {
  background: #e69008;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 📱 responsive */
@media (max-width: 768px) {
  .container {
    padding: 25px;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

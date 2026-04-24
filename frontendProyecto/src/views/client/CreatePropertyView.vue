<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { propertiesApi } from '@/api/properties'

const router = useRouter()

const form = ref({
  title:            '',
  description:      '',
  price:            '',
  property_type:    '',
  transaction_type: 'sale',
  address:          '',
  city:             '',
  bedrooms:         0,
  bathrooms:        0,
  square_meters:    0,
  latitude:         0,
  longitude:        0
})

const loading = ref(false)
const success = ref(false)
const error   = ref('')

const submit = async () => {
  error.value   = ''
  loading.value = true
  try {
    await propertiesApi.create({
      ...form.value,
      price:         Number(form.value.price),
      bedrooms:      Number(form.value.bedrooms),
      bathrooms:     Number(form.value.bathrooms),
      square_meters: Number(form.value.square_meters)
    })
    success.value = true
    setTimeout(() => router.push('/propiedades'), 2500)
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al publicar la propiedad'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="create">
    <div class="container">
      <h1>Publicar Propiedad</h1>
      <p class="subtitle">
        Tu propiedad será revisada por un asesor antes de publicarse.
      </p>

      <!-- ÉXITO -->
      <div v-if="success" class="alert-success">
        ✅ Propiedad enviada correctamente. Redirigiendo...
      </div>

      <template v-else>
        <!-- ERROR -->
        <div v-if="error" class="alert-error">{{ error }}</div>

        <form @submit.prevent="submit" class="form">
          <div class="grid">
            <input v-model="form.title"       placeholder="Título de la propiedad" required />
            <input v-model="form.price" type="number" placeholder="Precio (MXN)" required />

            <select v-model="form.property_type" required>
              <option value="">Tipo de propiedad</option>
              <option value="house">Casa</option>
              <option value="apartment">Departamento</option>
              <option value="land">Terreno</option>
              <option value="commercial">Local comercial</option>
            </select>

            <select v-model="form.transaction_type">
              <option value="sale">Venta</option>
              <option value="rent">Renta</option>
            </select>

            <input v-model="form.city"    placeholder="Ciudad"    required />
            <input v-model="form.address" placeholder="Dirección" required />

            <input v-model.number="form.bedrooms"      type="number" min="0" placeholder="Recámaras" />
            <input v-model.number="form.bathrooms"     type="number" min="0" placeholder="Baños" />
            <input v-model.number="form.square_meters" type="number" min="0" placeholder="m²" />

            <input v-model.number="form.latitude"  type="number" step="any" placeholder="Latitud (ej. 19.432)" />
            <input v-model.number="form.longitude" type="number" step="any" placeholder="Longitud (ej. -99.133)" />
          </div>

          <textarea
            v-model="form.description"
            placeholder="Descripción de la propiedad"
            rows="4"
          />

          <button type="submit" :disabled="loading">
            {{ loading ? 'Enviando...' : 'Publicar propiedad' }}
          </button>
        </form>
      </template>
    </div>
  </section>
</template>

<style scoped>
.create { padding: 60px 20px; background: #f7f9fc; min-height: 80vh; font-family: 'Poppins', sans-serif; }

.container {
  max-width: 900px; margin: auto; background: white;
  padding: 40px; border-radius: 16px; box-shadow: 0 15px 40px rgba(0,0,0,0.08);
}

h1       { text-align: center; font-size: 32px; margin-bottom: 10px; }
.subtitle { text-align: center; color: #666; margin-bottom: 30px; }

.alert-success { background: #dcfce7; color: #166534; padding: 16px; border-radius: 10px; text-align: center; font-weight: 500; }
.alert-error   { background: #fee2e2; color: #991b1b; padding: 12px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 18px; }

.form { display: flex; flex-direction: column; gap: 18px; }
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }

input, select, textarea {
  padding: 12px; border-radius: 8px; border: 1px solid #ddd;
  font-size: 14px; font-family: inherit; width: 100%;
}
input:focus, select:focus, textarea:focus { outline: none; border-color: #f59e0b; }
textarea { resize: vertical; }

button {
  background: #f59e0b; color: white; border: none;
  padding: 14px; border-radius: 10px; font-weight: 600;
  cursor: pointer; transition: background .2s; font-family: inherit; font-size: 15px;
}
button:hover    { background: #e69008; }
button:disabled { opacity: .6; cursor: not-allowed; }

@media (max-width: 768px) {
  .container { padding: 25px; }
  .grid { grid-template-columns: 1fr; }
}
</style>

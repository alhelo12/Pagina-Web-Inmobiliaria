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
  bedrooms:         '',
  bathrooms:        '',
  square_meters:    '',
  latitude:         '',
  longitude:        ''
})

const loading = ref(false)
const success = ref(false)
const error   = ref('')

const submit = async () => {
  error.value   = ''
  loading.value = true
  try {
    await propertiesApi.create({
      title:            form.value.title,
      description:      form.value.description,
      price:            Number(form.value.price),
      property_type:    form.value.property_type,
      transaction_type: form.value.transaction_type,
      address:          form.value.address,
      city:             form.value.city,
      bedrooms:         form.value.bedrooms     !== '' ? Number(form.value.bedrooms)     : 0,
      bathrooms:        form.value.bathrooms    !== '' ? Number(form.value.bathrooms)    : 0,
      square_meters:    form.value.square_meters !== '' ? Number(form.value.square_meters) : 0,
      latitude:         form.value.latitude     !== '' ? Number(form.value.latitude)     : 0,
      longitude:        form.value.longitude    !== '' ? Number(form.value.longitude)    : 0
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
      <p class="subtitle">Tu propiedad será revisada por un asesor antes de publicarse.</p>

      <!-- ÉXITO -->
      <div v-if="success" class="alert-success">
        ✅ Propiedad enviada correctamente. Redirigiendo...
      </div>

      <template v-else>
        <!-- ERROR -->
        <div v-if="error" class="alert-error">{{ error }}</div>

        <form @submit.prevent="submit">

          <!-- SECCIÓN: Información general -->
          <fieldset>
            <legend>Información general</legend>
            <div class="grid-2">
              <div class="field">
                <label>Título <span class="req">*</span></label>
                <input v-model="form.title" type="text" placeholder="Ej. Casa en fraccionamiento Las Palmas" required />
              </div>
              <div class="field">
                <label>Precio (MXN) <span class="req">*</span></label>
                <input v-model="form.price" type="number" min="0" placeholder="Ej. 1500000" required />
              </div>
              <div class="field">
                <label>Tipo de propiedad <span class="req">*</span></label>
                <select v-model="form.property_type" required>
                  <option value="" disabled>Selecciona un tipo</option>
                  <option value="house">Casa</option>
                  <option value="apartment">Departamento</option>
                </select>
              </div>
              <div class="field">
                <label>Tipo de operación <span class="req">*</span></label>
                <select v-model="form.transaction_type">
                  <option value="sale">Venta</option>
                  <option value="rent">Renta</option>
                </select>
              </div>
            </div>
          </fieldset>

          <!-- SECCIÓN: Ubicación -->
          <fieldset>
            <legend>Ubicación</legend>
            <div class="grid-2">
              <div class="field">
                <label>Ciudad <span class="req">*</span></label>
                <input v-model="form.city" type="text" placeholder="Ej. Tuxtla Gutiérrez" required />
              </div>
              <div class="field">
                <label>Dirección <span class="req">*</span></label>
                <input v-model="form.address" type="text" placeholder="Ej. Calle Reforma 123, Col. Centro" required />
              </div>
              <div class="field">
                <label>Latitud <span class="field">*</span></label>
                <input v-model="form.latitude" type="number" step="any" placeholder="Ej. 16.7521" required />
              </div>
              <div class="field">
                <label>Longitud <span class="field">*</span></label>
                <input v-model="form.longitude" type="number" step="any" placeholder="Ej. -93.1147" required />
              </div>
            </div>
            <p class="hint">💡 Puedes obtener las coordenadas haciendo clic derecho en Google Maps → "¿Qué hay aquí?"</p>
          </fieldset>

          <!-- SECCIÓN: Características -->
          <fieldset>
            <legend>Características</legend>
            <div class="grid-3">
              <div class="req">
                <label>Recámaras</label>
                <input v-model="form.bedrooms" type="number" min="0" placeholder="Ej. 3" />
              </div>
              <div class="req">
                <label>Baños</label>
                <input v-model="form.bathrooms" type="number" min="0" placeholder="Ej. 2" />
              </div>
              <div class="req">
                <label>Superficie (m²)</label>
                <input v-model="form.square_meters" type="number" min="0" placeholder="Ej. 120" />
              </div>
            </div>
          </fieldset>

          <!-- SECCIÓN: Descripción -->
          <fieldset>
            <legend>Descripción</legend>
            <div class="field">
              <label>Descripción de la propiedad</label>
              <textarea
                v-model="form.description"
                rows="5"
                placeholder="Describe las características principales, amenidades, estado de la propiedad, etc."
              />
            </div>
          </fieldset>

          <button type="submit" :disabled="loading">
            {{ loading ? 'Publicando...' : 'Publicar propiedad' }}
          </button>

        </form>
      </template>
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
  max-width: 860px;
  margin: auto;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 15px 40px rgba(0,0,0,0.08);
}

h1       { text-align: center; font-size: 30px; margin-bottom: 8px; }
.subtitle { text-align: center; color: #666; font-size: 14px; margin-bottom: 32px; }

.alert-success {
  background: #dcfce7; color: #166534;
  padding: 16px; border-radius: 10px;
  text-align: center; font-weight: 500;
}
.alert-error {
  background: #fee2e2; color: #991b1b;
  padding: 12px 14px; border-radius: 8px;
  font-size: 13px; margin-bottom: 18px;
}

/* FIELDSETS */
fieldset {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
}
legend {
  font-weight: 600;
  font-size: 14px;
  color: #0d2c54;
  padding: 0 8px;
  text-transform: uppercase;
  letter-spacing: .5px;
}

/* GRIDS */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }

/* FIELDS */
.field        { display: flex; flex-direction: column; gap: 6px; }
.field label  { font-size: 13px; color: #444; font-weight: 500; }
.req          { color: #ef4444; }

input, select, textarea {
  padding: 11px 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 14px;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #f59e0b;
}
textarea { resize: vertical; }

.hint {
  margin-top: 10px;
  font-size: 12px;
  color: #888;
}

button {
  width: 100%;
  margin-top: 8px;
  padding: 14px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: background .2s;
  font-family: inherit;
  font-size: 15px;
}
button:hover    { background: #e69008; }
button:disabled { opacity: .6; cursor: not-allowed; }

@media (max-width: 768px) {
  .container { padding: 24px; }
  .grid-2, .grid-3 { grid-template-columns: 1fr; }
}
</style>

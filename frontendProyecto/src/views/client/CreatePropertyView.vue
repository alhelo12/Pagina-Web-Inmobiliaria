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
const warning = ref('')
const error   = ref('')
const files = ref([])
const previews = ref([])

const MAX_FILES = 8
const MAX_SIZE_MB = 10
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

const fileToImage = (file) => new Promise((resolve, reject) => {
  const url = URL.createObjectURL(file)
  const img = new Image()
  img.onload = () => {
    URL.revokeObjectURL(url)
    resolve(img)
  }
  img.onerror = reject
  img.src = url
})

const canvasToBlob = (canvas, type, quality) => new Promise((resolve) => {
  canvas.toBlob((blob) => resolve(blob), type, quality)
})

const compressImage = async (file) => {
  const img = await fileToImage(file)
  const maxW = 1920
  const maxH = 1280
  const ratio = Math.min(maxW / img.width, maxH / img.height, 1)
  const width = Math.round(img.width * ratio)
  const height = Math.round(img.height * ratio)

  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')
  ctx.drawImage(img, 0, 0, width, height)

  let quality = 0.82
  let blob = await canvasToBlob(canvas, 'image/webp', quality)
  const maxBytes = 500 * 1024
  while (blob && blob.size > maxBytes && quality > 0.55) {
    quality -= 0.07
    blob = await canvasToBlob(canvas, 'image/webp', quality)
  }

  return new File([blob], `${file.name.replace(/\.[^.]+$/, '')}.webp`, { type: 'image/webp' })
}

const onFilesChange = async (event) => {
  const selected = Array.from(event.target.files || [])
  error.value = ''
  if (!selected.length) return
  if (selected.length > MAX_FILES) {
    error.value = `Puedes subir hasta ${MAX_FILES} imagenes`
    return
  }
  for (const file of selected) {
    if (!ALLOWED_TYPES.includes(file.type)) {
      error.value = 'Solo se permiten imagenes JPG, PNG o WEBP'
      return
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      error.value = `Cada imagen debe pesar maximo ${MAX_SIZE_MB}MB`
      return
    }
  }

  loading.value = true
  try {
    const compressed = []
    for (const file of selected) {
      compressed.push(await compressImage(file))
    }
    files.value = compressed
    previews.value = compressed.map((f) => URL.createObjectURL(f))
  } catch {
    error.value = 'No se pudieron procesar las imagenes'
  } finally {
    loading.value = false
  }
}

const submit = async () => {
  error.value   = ''
  warning.value = ''
  loading.value = true
  try {
    const { data: created } = await propertiesApi.create({
      title:            form.value.title,
      description:      form.value.description,
      price:            Number(form.value.price),
      property_type:    form.value.property_type,
      transaction_type: form.value.transaction_type,
      address:          form.value.address,
      city:             form.value.city,
      bedrooms:         form.value.bedrooms !== '' ? Number(form.value.bedrooms) : 0,
      bathrooms:        form.value.bathrooms !== '' ? Number(form.value.bathrooms) : 0,
      square_meters:    form.value.square_meters !== '' ? Number(form.value.square_meters) : 0,
      latitude:         form.value.latitude !== '' ? Number(form.value.latitude) : 0,
      longitude:        form.value.longitude !== '' ? Number(form.value.longitude) : 0
    })

    if (files.value.length) {
      let uploadErrors = 0
      for (let i = 0; i < files.value.length; i += 1) {
        try {
          await propertiesApi.uploadImage(created.id, files.value[i], i === 0)
        } catch {
          uploadErrors += 1
        }
      }
      if (uploadErrors > 0) {
        warning.value = `La propiedad se publico, pero ${uploadErrors} imagen(es) no se pudieron subir.`
      }
    }

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
    <div class="ambient"></div>
    <div class="container">
      <header class="hero">
        <p class="kicker">Panel admin</p>
        <h1>Nueva propiedad</h1>
        <p class="subtitle">Completa la informacion y envia para revision.</p>
      </header>

      <div v-if="success" class="alert alert-success">
        Propiedad enviada correctamente. Quedara en estado pendiente hasta ser aprobada por un asesor.
      </div>

      <template v-else>
        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="warning" class="alert alert-warning">{{ warning }}</div>

        <form @submit.prevent="submit" class="form">
          <fieldset class="card">
            <legend>Imagenes</legend>
            <div class="field">
              <label>Fotos de la propiedad <span class="req">*</span></label>
              <input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="onFilesChange" />
              <small class="help">Formatos: JPG, PNG, WEBP. Maximo 10MB por archivo. Se comprimen automaticamente.</small>
            </div>
            <div v-if="previews.length" class="preview-grid">
              <img v-for="(src, idx) in previews" :key="idx" :src="src" :alt="`preview-${idx}`" />
            </div>
          </fieldset>

          <fieldset class="card">
            <legend>Informacion general</legend>
            <div class="grid-2">
              <div class="field">
                <label>Titulo <span class="req">*</span></label>
                <input v-model="form.title" type="text" placeholder="Casa en fraccionamiento Las Palmas" required />
              </div>
              <div class="field">
                <label>Precio (MXN) <span class="req">*</span></label>
                <input v-model="form.price" type="number" min="0" placeholder="1500000" required />
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
                <label>Operacion <span class="req">*</span></label>
                <select v-model="form.transaction_type">
                  <option value="sale">Venta</option>
                  <option value="rent">Renta</option>
                </select>
              </div>
            </div>
          </fieldset>

          <fieldset class="card">
            <legend>Ubicacion</legend>
            <div class="grid-2">
              <div class="field">
                <label>Ciudad <span class="req">*</span></label>
                <input v-model="form.city" type="text" placeholder="Tuxtla Gutierrez" required />
              </div>
              <div class="field">
                <label>Direccion <span class="req">*</span></label>
                <input v-model="form.address" type="text" placeholder="Calle Reforma 123, Col. Centro" required />
              </div>
              <div class="field">
                <label>Latitud <span class="req">*</span></label>
                <input v-model="form.latitude" type="number" step="any" placeholder="16.7521" required />
              </div>
              <div class="field">
                <label>Longitud <span class="req">*</span></label>
                <input v-model="form.longitude" type="number" step="any" placeholder="-93.1147" required />
              </div>
            </div>
            <p class="hint">Tip: en Google Maps puedes copiar coordenadas con clic derecho.</p>
          </fieldset>

          <fieldset class="card">
            <legend>Caracteristicas</legend>
            <div class="grid-3">
              <div class="field">
                <label>Recamaras</label>
                <input v-model="form.bedrooms" type="number" min="0" placeholder="3" />
              </div>
              <div class="field">
                <label>Banos</label>
                <input v-model="form.bathrooms" type="number" min="0" placeholder="2" />
              </div>
              <div class="field">
                <label>Superficie (m2)</label>
                <input v-model="form.square_meters" type="number" min="0" placeholder="120" />
              </div>
            </div>
          </fieldset>

          <fieldset class="card">
            <legend>Descripcion</legend>
            <div class="field">
              <label>Detalles de la propiedad</label>
              <textarea
                v-model="form.description"
                rows="5"
                placeholder="Amenidades, estado del inmueble, orientacion, entorno y plusvalia."
              />
            </div>
          </fieldset>

          <button class="submit" type="submit" :disabled="loading">
            {{ loading ? 'Publicando...' : 'Publicar propiedad' }}
          </button>
        </form>
      </template>
    </div>
  </section>
</template>

<style scoped>
.create {
  --ink: #111827;
  --muted: #566074;
  --line: #dde3ed;
  --soft: #f5f8ff;
  --brand: #0d9488;
  --brand-deep: #0f766e;
  min-height: 100vh;
  padding: 56px 20px 72px;
  position: relative;
  background:
    radial-gradient(circle at 8% 12%, rgba(13, 148, 136, 0.18), transparent 28%),
    radial-gradient(circle at 92% 88%, rgba(37, 99, 235, 0.16), transparent 30%),
    linear-gradient(145deg, #f8fafc 0%, #eef3fb 100%);
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.ambient {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(17, 24, 39, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(17, 24, 39, 0.03) 1px, transparent 1px);
  background-size: 34px 34px;
  pointer-events: none;
}

.container {
  position: relative;
  max-width: 940px;
  margin: auto;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 36px;
  box-shadow: 0 28px 60px rgba(15, 23, 42, 0.12);
}

.hero {
  margin-bottom: 24px;
}

.kicker {
  margin: 0 0 8px;
  color: var(--brand-deep);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 12px;
}

h1 {
  margin: 0;
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.05;
  color: var(--ink);
}

.subtitle {
  margin: 10px 0 0;
  color: var(--muted);
  font-size: 15px;
}

.form {
  display: grid;
  gap: 16px;
}

.card {
  border: 1px solid var(--line);
  background: linear-gradient(180deg, #ffffff 0%, var(--soft) 100%);
  border-radius: 18px;
  padding: 18px 18px 16px;
  margin: 0;
}

legend {
  color: #0f172a;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0 8px;
}

.grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }

.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 13px; color: #374151; font-weight: 600; }
.req { color: #dc2626; }
.help { color: #667085; font-size: 12px; }

input, select, textarea {
  padding: 11px 12px;
  border-radius: 10px;
  border: 1px solid #d3dae5;
  font-size: 14px;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
  background: #fff;
  color: #0f172a;
  transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--brand);
  box-shadow: 0 0 0 4px rgba(13, 148, 136, 0.16);
  transform: translateY(-1px);
}

.hint {
  margin: 12px 2px 2px;
  font-size: 12px;
  color: #667085;
}

.preview-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
}

.preview-grid img {
  width: 100%;
  height: 90px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid #dbe3f0;
}

.alert {
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 14px;
  font-size: 14px;
  font-weight: 600;
}

.alert-success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #86efac;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.alert-warning {
  background: #fff7ed;
  color: #9a3412;
  border: 1px solid #fdba74;
}

.submit {
  margin-top: 6px;
  padding: 14px 20px;
  background: linear-gradient(120deg, var(--brand-deep), var(--brand));
  color: #fff;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
  transition: transform .2s ease, box-shadow .2s ease, filter .2s ease;
}

.submit:hover {
  filter: brightness(1.04);
  transform: translateY(-1px);
  box-shadow: 0 14px 26px rgba(15, 118, 110, 0.28);
}

.submit:disabled {
  opacity: .6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

@media (max-width: 768px) {
  .create {
    padding: 36px 14px 56px;
  }

  .container {
    padding: 22px;
    border-radius: 18px;
  }

  .grid-2, .grid-3 { grid-template-columns: 1fr; }
}
</style>

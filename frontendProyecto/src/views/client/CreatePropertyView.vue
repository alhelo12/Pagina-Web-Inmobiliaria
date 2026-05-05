<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { propertiesApi } from '@/api/properties'

const router = useRouter()

const steps = [
  'Informacion',
  'Fotos',
  'Ubicacion',
  'Caracteristicas',
  'Apartados'
]

const form = ref({
  title: '',
  description: '',
  price: '',
  property_type: '',
  transaction_type: 'sale',
  address: '',
  city: '',
  bedrooms: '',
  bathrooms: '',
  square_meters: '',
  latitude: '',
  longitude: ''
})

const currentStep = ref(0)
const loading = ref(false)
const success = ref(false)
const warning = ref('')
const error = ref('')

const generalFiles = ref([])
const generalPreviews = ref([])
const bedroomPhotos = ref([])
const bathroomPhotos = ref([])
const extras = ref([{ label: '', files: [], previews: [] }])

const MAX_GENERAL_FILES = 8
const MAX_EXTRA_FILES = 8
const MAX_SIZE_MB = 10
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

const bedroomsCount = computed(() => Math.max(0, Number(form.value.bedrooms) || 0))
const bathroomsCount = computed(() => Math.max(0, Number(form.value.bathrooms) || 0))
const progress = computed(() => `${((currentStep.value + 1) / steps.length) * 100}%`)
const isLastStep = computed(() => currentStep.value === steps.length - 1)

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

const validateFiles = (selected, maxFiles) => {
  if (selected.length > maxFiles) {
    error.value = `Puedes subir hasta ${maxFiles} imagenes`
    return false
  }

  for (const file of selected) {
    if (!ALLOWED_TYPES.includes(file.type)) {
      error.value = 'Solo se permiten imagenes JPG, PNG o WEBP'
      return false
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      error.value = `Cada imagen debe pesar maximo ${MAX_SIZE_MB}MB`
      return false
    }
  }

  return true
}

const compressFiles = async (selected) => {
  const compressed = []
  for (const file of selected) {
    compressed.push(await compressImage(file))
  }
  return compressed
}

const onGeneralFilesChange = async (event) => {
  const selected = Array.from(event.target.files || [])
  error.value = ''
  if (!selected.length || !validateFiles(selected, MAX_GENERAL_FILES)) return

  loading.value = true
  try {
    generalFiles.value = await compressFiles(selected)
    generalPreviews.value = generalFiles.value.map((file) => URL.createObjectURL(file))
  } catch {
    error.value = 'No se pudieron procesar las imagenes'
  } finally {
    loading.value = false
  }
}

const onSinglePhotoChange = async (event, collection, index) => {
  const selected = Array.from(event.target.files || [])
  error.value = ''
  if (!selected.length || !validateFiles(selected, 1)) return

  loading.value = true
  try {
    const [file] = await compressFiles(selected)
    const target = collection.value ?? collection
    target[index] = {
      file,
      preview: URL.createObjectURL(file)
    }
  } catch {
    error.value = 'No se pudo procesar la imagen'
  } finally {
    loading.value = false
  }
}

const addExtra = () => {
  extras.value.push({ label: '', files: [], previews: [] })
}

const removeExtra = (index) => {
  extras.value.splice(index, 1)
  if (!extras.value.length) addExtra()
}

const onExtraFilesChange = async (event, index) => {
  const selected = Array.from(event.target.files || [])
  error.value = ''
  if (!selected.length || !validateFiles(selected, MAX_EXTRA_FILES)) return

  loading.value = true
  try {
    const files = await compressFiles(selected)
    extras.value[index].files = files
    extras.value[index].previews = files.map((file) => URL.createObjectURL(file))
  } catch {
    error.value = 'No se pudieron procesar las imagenes'
  } finally {
    loading.value = false
  }
}

const hasValue = (value) => String(value ?? '').trim() !== ''

const validateStep = () => {
  error.value = ''

  if (currentStep.value === 0) {
    if (!hasValue(form.value.title) || form.value.title.trim().length < 10) {
      error.value = 'El titulo debe tener al menos 10 caracteres'
      return false
    }
    if (!hasValue(form.value.price) || Number(form.value.price) <= 0) {
      error.value = 'Ingresa un precio valido'
      return false
    }
    if (!form.value.property_type) {
      error.value = 'Selecciona el tipo de propiedad'
      return false
    }
  }

  if (currentStep.value === 1 && !generalFiles.value.length) {
    error.value = 'Agrega al menos una foto general de la propiedad'
    return false
  }

  if (currentStep.value === 2) {
    if (!hasValue(form.value.city) || form.value.city.trim().length < 2) {
      error.value = 'Ingresa la ciudad'
      return false
    }
    if (!hasValue(form.value.address) || form.value.address.trim().length < 10) {
      error.value = 'Ingresa una direccion mas completa'
      return false
    }
    if (hasValue(form.value.latitude) && (Number(form.value.latitude) < -90 || Number(form.value.latitude) > 90)) {
      error.value = 'La latitud debe estar entre -90 y 90'
      return false
    }
    if (hasValue(form.value.longitude) && (Number(form.value.longitude) < -180 || Number(form.value.longitude) > 180)) {
      error.value = 'La longitud debe estar entre -180 y 180'
      return false
    }
  }

  return true
}

const nextStep = () => {
  if (!validateStep()) return
  currentStep.value = Math.min(currentStep.value + 1, steps.length - 1)
}

const prevStep = () => {
  error.value = ''
  currentStep.value = Math.max(currentStep.value - 1, 0)
}

const buildPayload = () => ({
  title: form.value.title,
  description: form.value.description,
  price: Number(form.value.price),
  property_type: form.value.property_type,
  transaction_type: form.value.transaction_type,
  address: form.value.address,
  city: form.value.city,
  bedrooms: form.value.bedrooms !== '' ? Number(form.value.bedrooms) : 0,
  bathrooms: form.value.bathrooms !== '' ? Number(form.value.bathrooms) : 0,
  square_meters: form.value.square_meters !== '' ? Number(form.value.square_meters) : 0,
  latitude: form.value.latitude !== '' ? Number(form.value.latitude) : null,
  longitude: form.value.longitude !== '' ? Number(form.value.longitude) : null
})

const uploadPropertyImages = async (propertyId) => {
  let uploadErrors = 0

  for (let i = 0; i < generalFiles.value.length; i += 1) {
    try {
      await propertiesApi.uploadImage(propertyId, generalFiles.value[i], i === 0, {
        image_type: 'general'
      })
    } catch {
      uploadErrors += 1
    }
  }

  for (let i = 0; i < bedroomsCount.value; i += 1) {
    const photo = bedroomPhotos.value[i]
    if (!photo?.file) continue
    try {
      await propertiesApi.uploadImage(propertyId, photo.file, false, {
        label: `Recamara ${i + 1}`,
        image_type: 'bedroom'
      })
    } catch {
      uploadErrors += 1
    }
  }

  for (let i = 0; i < bathroomsCount.value; i += 1) {
    const photo = bathroomPhotos.value[i]
    if (!photo?.file) continue
    try {
      await propertiesApi.uploadImage(propertyId, photo.file, false, {
        label: `Bano ${i + 1}`,
        image_type: 'bathroom'
      })
    } catch {
      uploadErrors += 1
    }
  }

  for (const extra of extras.value) {
    const label = extra.label.trim()
    if (!label || !extra.files.length) continue
    for (const file of extra.files) {
      try {
        await propertiesApi.uploadImage(propertyId, file, false, {
          label,
          is_extra: true,
          image_type: 'extra'
        })
      } catch {
        uploadErrors += 1
      }
    }
  }

  return uploadErrors
}

const submit = async () => {
  if (!validateStep()) return

  error.value = ''
  warning.value = ''
  loading.value = true
  try {
    const { data: created } = await propertiesApi.create(buildPayload())
    const uploadErrors = await uploadPropertyImages(created.id)

    if (uploadErrors > 0) {
      warning.value = `La propiedad se publico, pero ${uploadErrors} imagen(es) no se pudieron subir.`
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
    <div class="container">
      <header class="hero">
        <p class="kicker">Panel admin</p>
        <h1>Nueva propiedad</h1>
        <p class="subtitle">Completa la publicacion paso a paso.</p>
      </header>

      <div v-if="success" class="alert alert-success">
        Propiedad enviada correctamente. Quedara en estado pendiente hasta ser aprobada por un asesor.
      </div>

      <template v-else>
        <div class="wizard-head">
          <div class="steps">
            <button
              v-for="(step, index) in steps"
              :key="step"
              type="button"
              class="step"
              :class="{ active: currentStep === index, done: currentStep > index }"
              @click="index < currentStep && (currentStep = index)"
            >
              <span>{{ index + 1 }}</span>
              {{ step }}
            </button>
          </div>
          <div class="progress">
            <div :style="{ width: progress }"></div>
          </div>
        </div>

        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="warning" class="alert alert-warning">{{ warning }}</div>

        <form @submit.prevent="submit" class="form">
          <fieldset v-if="currentStep === 0" class="step-panel">
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

          <fieldset v-if="currentStep === 1" class="step-panel">
            <legend>Fotos generales</legend>
            <div class="field">
              <label>Fotos de la propiedad <span class="req">*</span></label>
              <input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="onGeneralFilesChange" />
              <small class="help">Formatos: JPG, PNG, WEBP. La primera imagen sera la principal.</small>
            </div>
            <div v-if="generalPreviews.length" class="preview-grid">
              <img v-for="(src, idx) in generalPreviews" :key="idx" :src="src" :alt="`preview-${idx}`" />
            </div>
          </fieldset>

          <fieldset v-if="currentStep === 2" class="step-panel">
            <legend>Ubicacion</legend>
            <div class="location-layout">
              <div class="location-fields">
                <div class="field">
                  <label>Ciudad <span class="req">*</span></label>
                  <input v-model="form.city" type="text" placeholder="Tuxtla Gutierrez" required />
                </div>
                <div class="field">
                  <label>Direccion <span class="req">*</span></label>
                  <input v-model="form.address" type="text" placeholder="Calle Reforma 123, Col. Centro" required />
                </div>
                <div class="grid-2 compact">
                  <div class="field">
                    <label>Latitud</label>
                    <input v-model="form.latitude" type="number" step="any" placeholder="16.7521" />
                  </div>
                  <div class="field">
                    <label>Longitud</label>
                    <input v-model="form.longitude" type="number" step="any" placeholder="-93.1147" />
                  </div>
                </div>
              </div>
              <div class="map-slot">
                <div class="map-pin"></div>
                <strong>Mapa de ubicacion</strong>
                <small>Leaflet Maps</small>
              </div>
            </div>
          </fieldset>

          <fieldset v-if="currentStep === 3" class="step-panel">
            <legend>Caracteristicas y descripcion</legend>
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
            <div class="field">
              <label>Detalles de la propiedad</label>
              <textarea
                v-model="form.description"
                rows="6"
                placeholder="Amenidades, estado del inmueble, orientacion, entorno y plusvalia."
              />
            </div>
          </fieldset>

          <fieldset v-if="currentStep === 4" class="step-panel">
            <legend>Fotos por apartados</legend>

            <section v-if="bedroomsCount" class="section-block">
              <header>
                <h2>Recamaras</h2>
                <span>{{ bedroomsCount }} foto(s)</span>
              </header>
              <div class="slot-grid">
                <label v-for="index in bedroomsCount" :key="`bed-${index}`" class="photo-slot">
                  <img v-if="bedroomPhotos[index - 1]?.preview" :src="bedroomPhotos[index - 1].preview" :alt="`Recamara ${index}`" />
                  <span v-else>Recamara {{ index }}</span>
                  <input type="file" accept="image/jpeg,image/png,image/webp" @change="onSinglePhotoChange($event, bedroomPhotos, index - 1)" />
                </label>
              </div>
            </section>

            <section v-if="bathroomsCount" class="section-block">
              <header>
                <h2>Banos</h2>
                <span>{{ bathroomsCount }} foto(s)</span>
              </header>
              <div class="slot-grid">
                <label v-for="index in bathroomsCount" :key="`bath-${index}`" class="photo-slot">
                  <img v-if="bathroomPhotos[index - 1]?.preview" :src="bathroomPhotos[index - 1].preview" :alt="`Bano ${index}`" />
                  <span v-else>Bano {{ index }}</span>
                  <input type="file" accept="image/jpeg,image/png,image/webp" @change="onSinglePhotoChange($event, bathroomPhotos, index - 1)" />
                </label>
              </div>
            </section>

            <section class="section-block">
              <header>
                <h2>Extras</h2>
                <button type="button" class="link-btn" @click="addExtra">Agregar extra</button>
              </header>

              <div v-for="(extra, index) in extras" :key="index" class="extra-row">
                <div class="field">
                  <label>Nombre del extra</label>
                  <input v-model="extra.label" type="text" placeholder="Cocina, patio, sala..." />
                </div>
                <div class="field">
                  <label>Fotos del extra</label>
                  <input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="onExtraFilesChange($event, index)" />
                </div>
                <button type="button" class="remove-btn" @click="removeExtra(index)">Quitar</button>
                <div v-if="extra.previews.length" class="preview-grid extra-preview">
                  <img v-for="(src, imgIndex) in extra.previews" :key="imgIndex" :src="src" :alt="`${extra.label || 'Extra'} ${imgIndex + 1}`" />
                </div>
              </div>
            </section>
          </fieldset>

          <div class="actions">
            <button v-if="currentStep > 0" class="ghost" type="button" :disabled="loading" @click="prevStep">
              Atras
            </button>
            <button v-if="!isLastStep" class="submit" type="button" :disabled="loading" @click="nextStep">
              Siguiente
            </button>
            <button v-else class="submit" type="submit" :disabled="loading">
              {{ loading ? 'Publicando...' : 'Publicar propiedad' }}
            </button>
          </div>
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
  --soft: #f6f8fb;
  --brand: #0d9488;
  --brand-deep: #0f766e;
  min-height: 100vh;
  padding: 48px 20px 72px;
  background: #f4f7fb;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.container {
  max-width: 980px;
  margin: auto;
}

.hero {
  margin-bottom: 22px;
}

.kicker {
  margin: 0 0 8px;
  color: var(--brand-deep);
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 12px;
}

h1 {
  margin: 0;
  color: var(--ink);
  font-size: 38px;
  line-height: 1.1;
}

.subtitle {
  margin: 10px 0 0;
  color: var(--muted);
  font-size: 15px;
}

.wizard-head,
.step-panel {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
}

.wizard-head {
  padding: 16px;
  margin-bottom: 16px;
}

.steps {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}

.step {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  border: 1px solid #e1e7f0;
  border-radius: 10px;
  background: #f9fbff;
  color: #4b5563;
  font-size: 12px;
  font-weight: 800;
  cursor: default;
}

.step span {
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #e8eef7;
  color: #334155;
  font-size: 12px;
}

.step.done {
  cursor: pointer;
}

.step.active,
.step.done {
  border-color: rgba(13, 148, 136, 0.38);
  color: var(--brand-deep);
  background: #eefdfa;
}

.step.active span,
.step.done span {
  background: var(--brand);
  color: #fff;
}

.progress {
  height: 5px;
  margin-top: 14px;
  border-radius: 999px;
  background: #e5eaf2;
  overflow: hidden;
}

.progress div {
  height: 100%;
  background: var(--brand);
  transition: width .25s ease;
}

.form {
  display: grid;
  gap: 16px;
}

.step-panel {
  display: grid;
  gap: 18px;
  padding: 24px;
  margin: 0;
}

legend {
  color: #0f172a;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0 8px;
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.compact {
  gap: 10px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field label {
  font-size: 13px;
  color: #374151;
  font-weight: 700;
}

.req {
  color: #dc2626;
}

.help {
  color: #667085;
  font-size: 12px;
}

input,
select,
textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 11px 12px;
  border-radius: 10px;
  border: 1px solid #d3dae5;
  background: #fff;
  color: #0f172a;
  font-size: 14px;
  font-family: inherit;
  transition: border-color .2s ease, box-shadow .2s ease;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: var(--brand);
  box-shadow: 0 0 0 4px rgba(13, 148, 136, 0.16);
}

.location-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 18px;
  align-items: stretch;
}

.location-fields {
  display: grid;
  gap: 14px;
}

.map-slot {
  min-height: 255px;
  border: 1px dashed #b8c5d6;
  border-radius: 14px;
  background:
    linear-gradient(#eef3f9 1px, transparent 1px),
    linear-gradient(90deg, #eef3f9 1px, transparent 1px),
    #f8fafc;
  background-size: 28px 28px;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 8px;
  color: #526173;
}

.map-pin {
  width: 26px;
  height: 26px;
  border-radius: 50% 50% 50% 0;
  background: var(--brand);
  transform: rotate(-45deg);
  position: relative;
}

.map-pin::after {
  content: "";
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #fff;
  left: 8px;
  top: 8px;
}

.map-slot strong,
.map-slot small {
  transform: none;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
}

.preview-grid img {
  width: 100%;
  height: 92px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid #dbe3f0;
}

.section-block {
  display: grid;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e1e7f0;
  border-radius: 14px;
  background: #fbfcff;
}

.section-block header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.section-block h2 {
  margin: 0;
  font-size: 16px;
  color: var(--ink);
}

.section-block span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.slot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(135px, 1fr));
  gap: 10px;
}

.photo-slot {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 120px;
  border: 1px dashed #b8c5d6;
  border-radius: 12px;
  background: #fff;
  color: #526173;
  font-size: 13px;
  font-weight: 700;
  text-align: center;
  overflow: hidden;
  cursor: pointer;
}

.photo-slot input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.photo-slot img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.extra-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) auto;
  gap: 12px;
  align-items: end;
  padding: 14px;
  border: 1px solid #e5eaf2;
  border-radius: 12px;
  background: #fff;
}

.extra-preview {
  grid-column: 1 / -1;
}

.link-btn,
.remove-btn,
.ghost,
.submit {
  border: none;
  font-family: inherit;
  font-weight: 800;
  cursor: pointer;
}

.link-btn {
  color: var(--brand-deep);
  background: transparent;
  padding: 8px 0;
}

.remove-btn {
  min-height: 40px;
  padding: 0 12px;
  border-radius: 10px;
  color: #9f1239;
  background: #fff1f2;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.ghost,
.submit {
  min-height: 44px;
  padding: 0 20px;
  border-radius: 12px;
  font-size: 14px;
}

.ghost {
  color: #334155;
  background: #e8eef7;
}

.submit {
  color: #fff;
  background: var(--brand-deep);
  box-shadow: 0 12px 24px rgba(15, 118, 110, 0.22);
}

.submit:hover {
  background: var(--brand);
}

.submit:disabled,
.ghost:disabled {
  opacity: .6;
  cursor: not-allowed;
  box-shadow: none;
}

.alert {
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 14px;
  font-size: 14px;
  font-weight: 700;
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

@media (max-width: 860px) {
  .steps {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .location-layout,
  .grid-2,
  .grid-3,
  .extra-row {
    grid-template-columns: 1fr;
  }

  .map-slot {
    min-height: 220px;
  }
}

@media (max-width: 560px) {
  .create {
    padding: 34px 14px 56px;
  }

  h1 {
    font-size: 30px;
  }

  .step-panel,
  .wizard-head {
    border-radius: 12px;
    padding: 16px;
  }

  .steps {
    grid-template-columns: 1fr;
  }

  .actions {
    flex-direction: column-reverse;
  }
}
</style>

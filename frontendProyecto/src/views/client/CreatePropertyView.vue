<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { propertiesApi } from '@/api/properties'
import { normalizeImageUrl } from '@/utils/propertyImages'

const router = useRouter()
const route = useRoute()
const propertyId = computed(() => route.params.id)
const isEdit = computed(() => Boolean(propertyId.value))

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
const initialLoading = ref(false)
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

const returnPath = computed(() => (route.path.startsWith('/admin') ? '/admin/propiedades' : '/propiedades'))
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

  if (currentStep.value === 1 && !isEdit.value && !generalFiles.value.length) {
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

const loadProperty = async () => {
  if (!isEdit.value) return

  initialLoading.value = true
  error.value = ''
  try {
    const { data } = await propertiesApi.getById(propertyId.value)
    form.value = {
      title: data.title ?? '',
      description: data.description ?? '',
      price: data.price ?? '',
      property_type: data.property_type ?? '',
      transaction_type: data.transaction_type ?? 'sale',
      address: data.address ?? '',
      city: data.city ?? '',
      bedrooms: data.bedrooms ?? '',
      bathrooms: data.bathrooms ?? '',
      square_meters: data.square_meters ?? '',
      latitude: data.latitude ?? '',
      longitude: data.longitude ?? ''
    }
    generalPreviews.value = (data.images ?? [])
      .filter((image) => image.image_type === 'general' || image.is_main)
      .map((image) => normalizeImageUrl(image.image_url))
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'No se pudo cargar la propiedad'
  } finally {
    initialLoading.value = false
  }
}

const submit = async () => {
  if (!validateStep()) return

  error.value = ''
  warning.value = ''
  loading.value = true
  try {
    const { data: saved } = isEdit.value
      ? await propertiesApi.update(propertyId.value, buildPayload())
      : await propertiesApi.create(buildPayload())

    const uploadErrors = await uploadPropertyImages(saved.id)

    if (uploadErrors > 0) {
      warning.value = `La propiedad se guardó, pero ${uploadErrors} imagen(es) no se pudieron subir.`
    }

    success.value = true
    setTimeout(() => router.push(returnPath.value), 1800)
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al guardar la propiedad'
  } finally {
    loading.value = false
  }
}

onMounted(loadProperty)
</script>

<template>
  <section class="create">
    <div class="container">
      <header class="page-header">
        <div>
          <span class="kicker">Panel Admin</span>
          <h1>{{ isEdit ? 'Editar propiedad' : 'Nueva propiedad' }}</h1>
          <p class="subtitle">{{ isEdit ? 'Actualiza la informacion principal de la propiedad.' : 'Completa la publicacion paso a paso.' }}</p>
        </div>
        <div class="header-step-indicator">
          <span class="step-count">{{ currentStep + 1 }}/{{ steps.length }}</span>
          <span class="step-name">{{ steps[currentStep] }}</span>
        </div>
      </header>

      <div v-if="success" class="success-card">
        <div class="success-icon">✓</div>
        <h2>{{ isEdit ? 'Propiedad actualizada' : 'Propiedad publicada' }}</h2>
        <p>{{ isEdit ? 'Los cambios se guardaron correctamente. Redirigiendo...' : 'Quedara pendiente hasta ser aprobada. Redirigiendo...' }}</p>
      </div>

      <div v-if="!success && initialLoading" class="alert alert-warning">
        Cargando propiedad...
      </div>

      <template v-else-if="!success">

        <div class="wizard-nav">
          <button
            v-for="(step, index) in steps"
            :key="step"
            type="button"
            class="step-btn"
            :class="{ active: currentStep === index, done: currentStep > index }"
            @click="index < currentStep && (currentStep = index)"
          >
            <span class="step-circle">
              <span v-if="currentStep > index">✓</span>
              <span v-else>{{ index + 1 }}</span>
            </span>
            <span class="step-label">{{ step }}</span>
          </button>
        </div>

        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress }"></div>
        </div>

        <div v-if="error" class="alert alert-error">⚠ {{ error }}</div>
        <div v-if="warning" class="alert alert-warning">⚡ {{ warning }}</div>

        <form @submit.prevent="submit" class="form">

          <!-- STEP 1 -->
          <div v-if="currentStep === 0" class="step-panel">
            <div class="panel-header">
              <span class="panel-icon">📋</span>
              <div><h2>Informacion general</h2><p>Datos basicos de la propiedad</p></div>
            </div>
            <div class="fields-grid">
              <div class="field">
                <label>Titulo <span class="req">*</span></label>
                <input v-model="form.title" type="text" placeholder="Casa en fraccionamiento Las Palmas" />
              </div>
              <div class="field">
                <label>Precio (MXN) <span class="req">*</span></label>
                <div class="input-prefix">
                  <span>$</span>
                  <input v-model="form.price" type="number" min="0" placeholder="1500000" />
                </div>
              </div>
              <div class="field">
                <label>Tipo de propiedad <span class="req">*</span></label>
                <select v-model="form.property_type">
                  <option value="" disabled>Selecciona un tipo</option>
                  <option value="house">Casa</option>
                  <option value="apartment">Departamento</option>
                </select>
              </div>
              <div class="field">
                <label>Operacion <span class="req">*</span></label>
                <div class="toggle-group">
                  <button type="button" :class="['toggle-btn', { active: form.transaction_type === 'sale' }]" @click="form.transaction_type = 'sale'">Venta</button>
                  <button type="button" :class="['toggle-btn', { active: form.transaction_type === 'rent' }]" @click="form.transaction_type = 'rent'">Renta</button>
                </div>
              </div>
            </div>
          </div>

          <!-- STEP 2 -->
          <div v-if="currentStep === 1" class="step-panel">
            <div class="panel-header">
              <span class="panel-icon">📷</span>
              <div><h2>Fotos generales</h2><p>La primera imagen sera la principal</p></div>
            </div>
            <label class="upload-zone">
              <input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="onGeneralFilesChange" />
              <div class="upload-content">
                <div class="upload-icon">🖼</div>
                <strong>{{ isEdit ? 'Agrega nuevas fotos' : 'Arrastra tus fotos aqui' }}</strong>
                <span>o haz clic para seleccionar</span>
                <small>{{ isEdit ? 'Las fotos actuales se conservan' : `JPG, PNG, WEBP � Max ${MAX_GENERAL_FILES} fotos � ${MAX_SIZE_MB}MB c/u` }}</small>
              </div>
            </label>
            <div v-if="generalPreviews.length" class="preview-grid">
              <div v-for="(src, idx) in generalPreviews" :key="idx" class="preview-item">
                <img :src="src" :alt="`preview-${idx}`" />
                <span v-if="idx === 0" class="main-badge">Principal</span>
              </div>
            </div>
          </div>

          <!-- STEP 3 -->
          <div v-if="currentStep === 2" class="step-panel">
            <div class="panel-header">
              <span class="panel-icon">📍</span>
              <div><h2>Ubicacion</h2><p>Donde se encuentra la propiedad</p></div>
            </div>
            <div class="location-layout">
              <div class="location-fields">
                <div class="field">
                  <label>Ciudad <span class="req">*</span></label>
                  <input v-model="form.city" type="text" placeholder="Tuxtla Gutierrez" />
                </div>
                <div class="field">
                  <label>Direccion <span class="req">*</span></label>
                  <input v-model="form.address" type="text" placeholder="Calle Reforma 123, Col. Centro" />
                </div>
                <div class="grid-2">
                  <div class="field"><label>Latitud</label><input v-model="form.latitude" type="number" step="any" placeholder="16.7521" /></div>
                  <div class="field"><label>Longitud</label><input v-model="form.longitude" type="number" step="any" placeholder="-93.1147" /></div>
                </div>
              </div>
              <div class="map-slot">
                <div class="map-pin-icon">📍</div>
                <strong>Mapa de ubicacion</strong>
                <small>Ingresa lat/lng para previsualizar</small>
              </div>
            </div>
          </div>

          <!-- STEP 4 -->
          <div v-if="currentStep === 3" class="step-panel">
            <div class="panel-header">
              <span class="panel-icon">🏠</span>
              <div><h2>Caracteristicas</h2><p>Detalles fisicos de la propiedad</p></div>
            </div>
            <div class="features-cards">
              <div class="feature-card">
                <span class="feature-emoji">🛏</span>
                <label>Recamaras</label>
                <input v-model="form.bedrooms" type="number" min="0" placeholder="0" />
              </div>
              <div class="feature-card">
                <span class="feature-emoji">🛁</span>
                <label>Banos</label>
                <input v-model="form.bathrooms" type="number" min="0" placeholder="0" />
              </div>
              <div class="feature-card">
                <span class="feature-emoji">📐</span>
                <label>Superficie m²</label>
                <input v-model="form.square_meters" type="number" min="0" placeholder="0" />
              </div>
            </div>
            <div class="field">
              <label>Descripcion de la propiedad</label>
              <textarea v-model="form.description" rows="5" placeholder="Amenidades, estado del inmueble, orientacion, entorno y plusvalia..." />
            </div>
          </div>

          <!-- STEP 5 -->
          <div v-if="currentStep === 4" class="step-panel">
            <div class="panel-header">
              <span class="panel-icon">🖼</span>
              <div><h2>Fotos por apartados</h2><p>Agrega fotos especificas de cada espacio</p></div>
            </div>

            <div v-if="bedroomsCount" class="section-block">
              <div class="section-block-header">
                <span>🛏 Recamaras</span>
                <span class="count-badge">{{ bedroomsCount }} foto(s)</span>
              </div>
              <div class="slot-grid">
                <label v-for="index in bedroomsCount" :key="`bed-${index}`" class="photo-slot">
                  <img v-if="bedroomPhotos[index - 1]?.preview" :src="bedroomPhotos[index - 1].preview" :alt="`Recamara ${index}`" />
                  <div v-else class="slot-empty"><span>+</span><small>Recamara {{ index }}</small></div>
                  <input type="file" accept="image/jpeg,image/png,image/webp" @change="onSinglePhotoChange($event, bedroomPhotos, index - 1)" />
                </label>
              </div>
            </div>

            <div v-if="bathroomsCount" class="section-block">
              <div class="section-block-header">
                <span>🛁 Banos</span>
                <span class="count-badge">{{ bathroomsCount }} foto(s)</span>
              </div>
              <div class="slot-grid">
                <label v-for="index in bathroomsCount" :key="`bath-${index}`" class="photo-slot">
                  <img v-if="bathroomPhotos[index - 1]?.preview" :src="bathroomPhotos[index - 1].preview" :alt="`Bano ${index}`" />
                  <div v-else class="slot-empty"><span>+</span><small>Bano {{ index }}</small></div>
                  <input type="file" accept="image/jpeg,image/png,image/webp" @change="onSinglePhotoChange($event, bathroomPhotos, index - 1)" />
                </label>
              </div>
            </div>

            <div class="section-block">
              <div class="section-block-header">
                <span>✨ Extras</span>
                <button type="button" class="add-extra-btn" @click="addExtra">+ Agregar espacio</button>
              </div>
              <div v-for="(extra, index) in extras" :key="index" class="extra-row">
                <div class="field"><label>Nombre del espacio</label><input v-model="extra.label" type="text" placeholder="Cocina, patio, sala..." /></div>
                <div class="field"><label>Fotos</label><input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="onExtraFilesChange($event, index)" /></div>
                <button type="button" class="remove-btn" @click="removeExtra(index)">✕ Quitar</button>
                <div v-if="extra.previews.length" class="preview-grid extra-preview">
                  <div v-for="(src, imgIndex) in extra.previews" :key="imgIndex" class="preview-item">
                    <img :src="src" :alt="`${extra.label || 'Extra'} ${imgIndex + 1}`" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ACTIONS -->
          <div class="actions">
            <button v-if="currentStep > 0" class="btn-back" type="button" :disabled="loading" @click="prevStep">← Atras</button>
            <div class="actions-right">
              <span class="step-hint">Paso {{ currentStep + 1 }} de {{ steps.length }}</span>
              <button v-if="!isLastStep" class="btn-next" type="button" :disabled="loading" @click="nextStep">Siguiente →</button>
              <button v-else class="btn-next btn-publish" type="submit" :disabled="loading">{{ loading ? "Guardando..." : (isEdit ? "✓ Guardar cambios" : "✓ Publicar propiedad") }}</button>
            </div>
          </div>

        </form>
      </template>
    </div>
  </section>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

* { box-sizing: border-box; }

.create {
  --gold: #d4a34a;
  --gold-light: #f0c36f;
  --navy: #07172d;
  --navy-mid: #0f2a45;
  --cream: #f5f2ec;
  --white: #ffffff;
  --muted: #65717e;
  --line: #e5e0d6;
  --error: #991b1b;
  --error-bg: #fef2f2;
  min-height: 100vh;
  padding: 48px 20px 72px;
  background: var(--cream);
  font-family: "Poppins", sans-serif;
}
.container { max-width: 960px; margin: 0 auto; }

/* HEADER */
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 32px; }
.kicker { display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--gold); margin-bottom: 6px; }
h1 { font-size: 36px; font-weight: 800; color: var(--navy); margin: 0 0 6px; line-height: 1.1; }
.subtitle { font-size: 14px; color: var(--muted); margin: 0; }
.header-step-indicator { text-align: right; flex-shrink: 0; }
.step-count { display: block; font-size: 28px; font-weight: 800; color: var(--navy); line-height: 1; }
.step-name { font-size: 12px; color: var(--muted); font-weight: 500; }

/* WIZARD NAV */
.wizard-nav { display: flex; gap: 8px; background: var(--white); border: 1px solid var(--line); border-radius: 16px; padding: 14px; margin-bottom: 0; box-shadow: 0 2px 12px rgba(7,23,45,0.06); }
.step-btn { flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px; padding: 10px 8px; border: 1.5px solid var(--line); border-radius: 10px; background: #faf9f6; color: var(--muted); font-size: 12px; font-weight: 600; font-family: "Poppins", sans-serif; cursor: default; transition: all 0.2s; }
.step-btn.done { cursor: pointer; }
.step-btn.active { border-color: var(--gold); background: #fdf8ee; color: var(--navy); }
.step-btn.done { border-color: rgba(212,163,74,0.4); background: #fdf8ee; color: var(--navy); }
.step-circle { width: 24px; height: 24px; border-radius: 50%; background: var(--line); color: var(--muted); display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0; transition: all 0.2s; }
.step-btn.active .step-circle, .step-btn.done .step-circle { background: var(--gold); color: var(--navy); }
.step-label { display: none; }
@media (min-width: 640px) { .step-label { display: block; } }

/* PROGRESS */
.progress-bar { height: 4px; background: var(--line); border-radius: 0 0 8px 8px; overflow: hidden; margin-bottom: 24px; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--gold), var(--gold-light)); transition: width 0.3s ease; }

/* ALERTS */
.alert { display: flex; align-items: center; gap: 10px; padding: 12px 16px; border-radius: 10px; font-size: 13px; font-weight: 500; margin-bottom: 16px; }
.alert-error { background: var(--error-bg); color: var(--error); border: 1px solid #fecaca; }
.alert-warning { background: #fff7ed; color: #9a3412; border: 1px solid #fdba74; }

/* STEP PANEL */
.step-panel { background: var(--white); border: 1px solid var(--line); border-radius: 16px; padding: 28px; box-shadow: 0 2px 16px rgba(7,23,45,0.06); display: flex; flex-direction: column; gap: 24px; }
.panel-header { display: flex; align-items: flex-start; gap: 14px; padding-bottom: 20px; border-bottom: 1px solid var(--line); }
.panel-icon { font-size: 28px; flex-shrink: 0; line-height: 1; margin-top: 2px; }
.panel-header h2 { font-size: 18px; font-weight: 700; color: var(--navy); margin: 0 0 4px; }
.panel-header p { font-size: 13px; color: var(--muted); margin: 0; }

/* FIELDS */
.fields-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 13px; font-weight: 600; color: var(--navy); }
.req { color: var(--gold); }

input[type="text"], input[type="number"], select, textarea {
  width: 100%; padding: 11px 14px; border: 1.5px solid var(--line); border-radius: 10px;
  background: #faf9f6; color: var(--navy); font-size: 14px; font-family: "Poppins", sans-serif;
  transition: border-color 0.2s, box-shadow 0.2s; outline: none;
}
input:focus, select:focus, textarea:focus { border-color: var(--gold); background: var(--white); box-shadow: 0 0 0 3px rgba(212,163,74,0.15); }
input::placeholder, textarea::placeholder { color: #b5ae9f; }

.input-prefix { display: flex; align-items: center; border: 1.5px solid var(--line); border-radius: 10px; background: #faf9f6; overflow: hidden; transition: border-color 0.2s, box-shadow 0.2s; }
.input-prefix:focus-within { border-color: var(--gold); box-shadow: 0 0 0 3px rgba(212,163,74,0.15); }
.input-prefix span { padding: 11px 12px; font-size: 14px; font-weight: 600; color: var(--muted); background: #f0ece4; border-right: 1px solid var(--line); }
.input-prefix input { border: none; border-radius: 0; background: transparent; box-shadow: none !important; }

.toggle-group { display: flex; border: 1.5px solid var(--line); border-radius: 10px; overflow: hidden; }
.toggle-btn { flex: 1; padding: 11px; border: none; background: #faf9f6; color: var(--muted); font-size: 14px; font-weight: 600; font-family: "Poppins", sans-serif; cursor: pointer; transition: all 0.2s; }
.toggle-btn:first-child { border-right: 1px solid var(--line); }
.toggle-btn.active { background: var(--gold); color: var(--navy); }

/* UPLOAD */
.upload-zone { display: block; cursor: pointer; position: relative; }
.upload-zone input[type="file"] { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; }
.upload-content { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 40px 20px; border: 2px dashed var(--line); border-radius: 14px; background: #faf9f6; text-align: center; transition: border-color 0.2s, background 0.2s; }
.upload-zone:hover .upload-content { border-color: var(--gold); background: #fdf8ee; }
.upload-icon { font-size: 36px; margin-bottom: 4px; }
.upload-content strong { font-size: 15px; color: var(--navy); font-weight: 700; }
.upload-content span { font-size: 13px; color: var(--muted); }
.upload-content small { font-size: 12px; color: #b5ae9f; }

/* PREVIEW */
.preview-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; }
.preview-item { position: relative; border-radius: 10px; overflow: hidden; border: 1.5px solid var(--line); aspect-ratio: 4/3; }
.preview-item img { width: 100%; height: 100%; object-fit: cover; }
.main-badge { position: absolute; top: 6px; left: 6px; background: var(--gold); color: var(--navy); font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 20px; }

/* LOCATION */
.location-layout { display: grid; grid-template-columns: 1fr 300px; gap: 18px; }
.location-fields { display: flex; flex-direction: column; gap: 14px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.map-slot { min-height: 220px; border: 2px dashed var(--line); border-radius: 14px; background: linear-gradient(#f0ece4 1px, transparent 1px), linear-gradient(90deg, #f0ece4 1px, transparent 1px), #faf9f6; background-size: 28px 28px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; color: var(--muted); text-align: center; }
.map-pin-icon { font-size: 32px; }
.map-slot strong { font-size: 14px; color: var(--navy); font-weight: 600; }
.map-slot small { font-size: 12px; }

/* FEATURES */
.features-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.feature-card { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 20px 16px; background: #faf9f6; border: 1.5px solid var(--line); border-radius: 14px; text-align: center; }
.feature-emoji { font-size: 28px; }
.feature-card label { font-size: 13px; font-weight: 600; color: var(--navy); }
.feature-card input { text-align: center; font-size: 18px; font-weight: 700; padding: 8px; max-width: 100px; }

/* SECTION BLOCKS */
.section-block { border: 1.5px solid var(--line); border-radius: 14px; overflow: hidden; }
.section-block-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; background: #faf9f6; border-bottom: 1px solid var(--line); font-size: 14px; font-weight: 700; color: var(--navy); }
.count-badge { font-size: 11px; font-weight: 600; color: var(--muted); background: var(--line); padding: 3px 10px; border-radius: 20px; }
.add-extra-btn { background: var(--gold); color: var(--navy); border: none; border-radius: 8px; padding: 6px 14px; font-size: 12px; font-weight: 700; font-family: "Poppins", sans-serif; cursor: pointer; transition: background 0.2s; }
.add-extra-btn:hover { background: var(--gold-light); }
.slot-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; padding: 16px; }
.photo-slot { position: relative; aspect-ratio: 4/3; border: 2px dashed #d4c9b8; border-radius: 12px; overflow: hidden; cursor: pointer; transition: border-color 0.2s; }
.photo-slot:hover { border-color: var(--gold); }
.photo-slot input[type="file"] { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; }
.photo-slot img { width: 100%; height: 100%; object-fit: cover; }
.slot-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 4px; color: var(--muted); }
.slot-empty span { font-size: 24px; font-weight: 300; color: var(--gold); }
.slot-empty small { font-size: 11px; font-weight: 600; }
.extra-row { display: grid; grid-template-columns: 1fr 1fr auto; gap: 12px; align-items: end; padding: 16px; border-bottom: 1px solid var(--line); }
.extra-row:last-child { border-bottom: none; }
.extra-preview { grid-column: 1/-1; }
.remove-btn { padding: 10px 14px; border: 1.5px solid #fecaca; border-radius: 10px; background: #fef2f2; color: var(--error); font-size: 12px; font-weight: 700; font-family: "Poppins", sans-serif; cursor: pointer; white-space: nowrap; transition: background 0.2s; }
.remove-btn:hover { background: #fee2e2; }

/* ACTIONS */
.form { display: flex; flex-direction: column; gap: 16px; }
.actions { display: flex; align-items: center; justify-content: space-between; background: var(--white); border: 1px solid var(--line); border-radius: 14px; padding: 16px 20px; box-shadow: 0 2px 12px rgba(7,23,45,0.06); }
.actions-right { display: flex; align-items: center; gap: 14px; }
.step-hint { font-size: 12px; color: var(--muted); font-weight: 500; }
.btn-back { padding: 11px 22px; border: 1.5px solid var(--line); border-radius: 10px; background: transparent; color: var(--navy); font-size: 14px; font-weight: 600; font-family: "Poppins", sans-serif; cursor: pointer; transition: background 0.2s; }
.btn-back:hover { background: #f0ece4; }
.btn-back:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-next { padding: 11px 28px; border: none; border-radius: 10px; background: var(--navy); color: var(--white); font-size: 14px; font-weight: 700; font-family: "Poppins", sans-serif; cursor: pointer; transition: background 0.2s, box-shadow 0.2s; box-shadow: 0 4px 14px rgba(7,23,45,0.2); }
.btn-next:hover { background: var(--navy-mid); }
.btn-next:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; }
.btn-publish { background: var(--gold); color: var(--navy); box-shadow: 0 4px 14px rgba(212,163,74,0.35); }
.btn-publish:hover { background: var(--gold-light); }

/* SUCCESS */
.success-card { background: var(--white); border: 1px solid var(--line); border-radius: 16px; padding: 60px 40px; text-align: center; box-shadow: 0 4px 24px rgba(7,23,45,0.08); }
.success-icon { width: 64px; height: 64px; background: linear-gradient(135deg, var(--gold), var(--gold-light)); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 800; color: var(--navy); margin: 0 auto 20px; }
.success-card h2 { font-size: 24px; color: var(--navy); margin: 0 0 8px; }
.success-card p { color: var(--muted); font-size: 15px; margin: 0; }

/* RESPONSIVE */
@media (max-width: 860px) {
  .fields-grid, .location-layout, .grid-2 { grid-template-columns: 1fr; }
  .wizard-nav { flex-wrap: wrap; }
  .step-btn { flex: 1 1 calc(50% - 4px); }
}
@media (max-width: 560px) {
  .create { padding: 32px 14px 56px; }
  h1 { font-size: 28px; }
  .step-panel { padding: 18px; }
  .features-cards { grid-template-columns: 1fr; }
  .extra-row { grid-template-columns: 1fr; }
  .actions { flex-direction: column; gap: 10px; }
  .actions-right { width: 100%; justify-content: flex-end; }
  .page-header { flex-direction: column; gap: 8px; }
}
</style>

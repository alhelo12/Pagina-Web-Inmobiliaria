<script setup>
import { computed, onMounted, onUnmounted, ref, nextTick, watch } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import L from 'leaflet'
import { propertiesApi } from '@/api/properties'
import { normalizeImageUrl } from '@/utils/propertyImages'
import { formatPropertyTitle } from '@/utils/titleFormatter'
import { useToast } from '@/composables/useToast'

const { addToast } = useToast()
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const propertyId = computed(() => route.params.id)
const isEdit = computed(() => Boolean(propertyId.value))

const needsEmailVerification = computed(() =>
  auth.role === 'client' && !auth.isEmailVerified
)

const sendingEmail = ref(false)
const emailSent = ref(false)

const resendEmail = async () => {
  sendingEmail.value = true
  emailSent.value = false
  try {
    await auth.sendVerificationEmail()
    emailSent.value = true
  } catch {
    // silent
  } finally {
    sendingEmail.value = false
  }
}

const steps = [
  'Informacion',
  'Fotos',
  'Ubicacion',
  'Caracteristicas',
  'Apartados'
]

const MEXICO_CITIES = [
  'Acapulco', 'Aguascalientes', 'Almoloya de Alquisellas', 'Alvaro Obregon',
  'Amecameca', 'Apizaco', 'Ario de Rosales',
  'Baja California', 'Baja California Sur',
  'Benito Juarez', 'Cabo San Lucas', 'Cadereyta de Montes', 'Calvillo',
  'Campeche', 'Cancun', 'Celaya', 'Chapala', 'Chihuahua', 'Chilpancingo',
  'Chiapa de Corzo', 'Ciudad Acuna', 'Ciudad del Carmen', 'Ciudad Juarez',
  'Ciudad Lopez Mateos', 'Ciudad Madero', 'Ciudad Nezahualcoyotl', 'Ciudad Obregon',
  'Ciudad Satelite', 'Ciudad Valles', 'Coatepec', 'Colima', 'Comitan de Dominguez',
  'Cordoba', 'Cosoleacaque', 'Cuauhtemoc', 'Cuernavaca', 'Culiacan',
  'Distrito Federal',
  'Ecatepec de Morelos', 'El Marques', 'Empalme', 'Ensenada', 'Erongaricuaro',
  'Fresnillo', 'Gomez Palacio', 'Guadalajara', 'Guanajuato', 'Guaymas',
  'Hermosillo', 'Huejutla de Reyes', 'Huixtla', 'Irapuato', 'Istapa',
  'Ixtapaluca', 'Ixtlahuaca',
  'Jalapa', 'Jesus Maria',
  'La Paz', 'La Trinitaria', 'Lagos de Moreno', 'Leon', 'Loreto', 'Los Cabos',
  'Los Reyes de Salgado', 'Manzanillo', 'Matehuala', 'Mazatlan',
  'Merida', 'Mexicali', 'Mexico City', 'Miraflores', 'Monclova',
  'Monterrey', 'Morelia', 'Motozintla de Mendoza',
  'Naucalpan de Juarez', 'Nogales', 'Nuevo Laredo',
  'Oaxaca de Juarez', 'Ocosingo', 'Orizaba',
  'Palenque', 'Patzcuaro', 'Piedras Negras', 'Poza Rica de Hidalgo',
  'Puebla', 'Puerto Escondido', 'Puerto Vallarta',
  'Queretaro', 'Queretaro City',
  'Reynosa', 'Rosarito',
  'Salamanca', 'San Andres Cholula', 'San Cristobal de las Casas',
  'San Juan del Rio', 'San Luis Potosi', 'San Miguel de Allende',
  'San Nicolas de los Garza', 'San Pedro Garza Garcia', 'Santa Catarina',
  'Santiago Ixcuintla', 'Santiago Papasquiaro', 'Santo Tomas Ajoloapan',
  'Tampico', 'Tapachula', 'Taxco de Alarcon', 'Tecate', 'Tecamac',
  'Texcoco de Mora', 'Tijuana', 'Tlaxcala', 'Toluca', 'Tonala', 'Torreon',
  'Tuxtla Gutierrez',
  'Uruapan', 'Uriu',
  'Valladolid', 'Veracruz', 'Villahermosa', 'Xalapa', 'Zamora', 'Zihuatanejo',
].filter((v, i, a) => a.indexOf(v) === i).sort()

const citySearch = ref('')
const showCityDropdown = ref(false)

const filteredCities = computed(() => {
  const q = citySearch.value.toLowerCase()
  return MEXICO_CITIES.filter((c) => c.toLowerCase().includes(q)).slice(0, 20)
})

const selectCity = (city) => {
  form.value.city = city
  citySearch.value = ''
  showCityDropdown.value = false
}

const onCityInput = () => {
  showCityDropdown.value = true
}

const onCityBlur = () => {
  setTimeout(() => { showCityDropdown.value = false }, 200)
  if (form.value.city && !MEXICO_CITIES.includes(form.value.city)) {
    form.value.city = MEXICO_CITIES.find((c) => c.toLowerCase() === form.value.city.toLowerCase()) || ''
  }
}

const form = ref({
  title: '',
  description: '',
  price: '',
  property_type: '',
  transaction_type: 'sale',
  address: '',
  city: 'Tuxtla Gutierrez',
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

let mapInstance = null
let mapMarker = null
const mapContainer = ref(null)

const isDirty = ref(false)
const markDirty = () => { isDirty.value = true }
const formWatcher = watch(form.value, () => { isDirty.value = true }, { deep: true })

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

const syncGeneralFiles = () => {
  generalFiles.value = generalPreviews.value
    .filter((item) => item.file)
    .map((item) => item.file)
}

const onGeneralFilesChange = async (event) => {
  const selected = Array.from(event.target.files || [])
  error.value = ''
  event.target.value = ''
  if (!selected.length) return

  const [file] = selected
  if (generalPreviews.value.length >= MAX_GENERAL_FILES) {
    error.value = `Puedes subir hasta ${MAX_GENERAL_FILES} imagenes generales`
    return
  }
  if (!validateFiles([file], 1)) return

  loading.value = true
  try {
    const [compressed] = await compressFiles([file])
    generalPreviews.value.push({
      file: compressed,
      preview: URL.createObjectURL(compressed),
      name: file.name
    })
    syncGeneralFiles()
  } catch {
    error.value = 'No se pudo procesar la imagen'
  } finally {
    loading.value = false
  }
}

const removeGeneralPhoto = (index) => {
  const [removed] = generalPreviews.value.splice(index, 1)
  if (removed?.file && removed.preview) URL.revokeObjectURL(removed.preview)
  syncGeneralFiles()
}

const moveGeneralPhoto = (index, direction) => {
  const nextIndex = index + direction
  if (nextIndex < 0 || nextIndex >= generalPreviews.value.length) return
  const [photo] = generalPreviews.value.splice(index, 1)
  generalPreviews.value.splice(nextIndex, 0, photo)
  syncGeneralFiles()
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

const initMap = () => {
  nextTick(() => {
    if (!mapContainer.value) return
    if (mapInstance) mapInstance.remove()

    const lat = Number(form.value.latitude) || 16.7521
    const lng = Number(form.value.longitude) || -93.1147

    mapInstance = L.map(mapContainer.value, { zoomControl: true }).setView([lat, lng], 15)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '&copy; OpenStreetMap'
    }).addTo(mapInstance)

    mapMarker = L.marker([lat, lng], { draggable: true }).addTo(mapInstance)

    mapMarker.on('dragend', () => {
      const pos = mapMarker.getLatLng()
      form.value.latitude = pos.lat.toFixed(6)
      form.value.longitude = pos.lng.toFixed(6)
    })

    mapInstance.on('click', (e) => {
      mapMarker.setLatLng(e.latlng)
      form.value.latitude = e.latlng.lat.toFixed(6)
      form.value.longitude = e.latlng.lng.toFixed(6)
    })

    setTimeout(() => mapInstance.invalidateSize(), 100)
  })
}

const destroyMap = () => {
  if (mapInstance) { mapInstance.remove(); mapInstance = null; mapMarker = null }
}

const moveMarker = () => {
  const lat = Number(form.value.latitude)
  const lng = Number(form.value.longitude)
  if (mapMarker && lat && lng && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
    mapMarker.setLatLng([lat, lng])
    if (mapInstance) mapInstance.setView([lat, lng], mapInstance.getZoom())
  }
}

const STREET_PREFIXES = /^(calle|av|avenida|blvd|boulevard|privada|cerrada|andador|prolongacion|pasaje|circuito|periferico|carretera|camino)\b\.?\s*/i
const sanitizeAddress = (addr) => addr.replace(STREET_PREFIXES, '').replace(/#/g, ' ').replace(/\s+/g, ' ').trim()
const fixCity = (city) => (city || '').replace(/\s+/g, ' ').trim().replace(/guitierre?z/gi, 'Gutierrez').replace(/tuxtla\s*guit/i, 'Tuxtla Guit') || 'Tuxtla Gutierrez'

const searchAddress = async () => {
  const rawAddr = form.value.address?.trim()
  const city = form.value.city?.trim()
  if (!rawAddr || rawAddr.length < 5) {
    error.value = 'Escribe una direccion para buscar'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const addr = sanitizeAddress(rawAddr)
    const cityInput = form.value.city?.trim()
    const city = fixCity(cityInput)
    const parts = [addr, city, 'Chiapas', 'Mexico'].filter(Boolean)
    const q = parts.join(', ')
    const url = `https://nominatim.openstreetmap.org/search?format=json&limit=5&q=${encodeURIComponent(q)}`
    console.log('[searchAddress] URL:', url)
    const res = await fetch(url, {
      headers: { 'Accept-Language': 'es' }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    console.log('[searchAddress] Resultados:', data.length)
    if (data.length) {
      form.value.latitude = parseFloat(data[0].lat).toFixed(6)
      form.value.longitude = parseFloat(data[0].lon).toFixed(6)
      moveMarker()
    } else {
      error.value = 'No se encontro la direccion. Prueba con un nombre de calle mas general.'
    }
  } catch (err) {
    console.error('[searchAddress] Error:', err)
    error.value = 'Error al buscar la direccion: ' + err.message
  } finally {
    loading.value = false
  }
}

const removeBedroomPhoto = (index) => {
  if (bedroomPhotos.value[index]?.preview) URL.revokeObjectURL(bedroomPhotos.value[index].preview)
  bedroomPhotos.value[index] = null
}

const removeBathroomPhoto = (index) => {
  if (bathroomPhotos.value[index]?.preview) URL.revokeObjectURL(bathroomPhotos.value[index].preview)
  bathroomPhotos.value[index] = null
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

  if (currentStep.value === 3 && !hasValue(form.value.description)) {
    error.value = 'Agrega una descripcion de la propiedad'
    return false
  }

  return true
}

onBeforeRouteLeave((to, from, next) => {
  if (isDirty.value && !success.value) {
    const answer = window.confirm('Tienes cambios sin guardar. Salir de todas formas?')
    if (!answer) return next(false)
  }
  next()
})

watch(currentStep, (step) => {
  if (step === 2) initMap()
  else if (mapInstance) destroyMap()
})

watch([() => form.value.latitude, () => form.value.longitude], moveMarker)

const formatTitle = () => {
  form.value.title = formatPropertyTitle(form.value.title)
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
  title: formatPropertyTitle(form.value.title),
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
    const images = data.images ?? []

    generalPreviews.value = images
      .filter((img) => img.image_type === 'general' || img.is_main)
      .map((img) => ({
        preview: normalizeImageUrl(img.image_url),
        name: img.label || 'Foto registrada',
        existing: true
      }))

    images.filter((img) => img.image_type === 'bedroom').forEach((img) => {
      const idx = parseInt(img.label?.match(/\d+/)?.[0] || '1') - 1
      bedroomPhotos.value[idx] = { preview: normalizeImageUrl(img.image_url) }
    })

    images.filter((img) => img.image_type === 'bathroom').forEach((img) => {
      const idx = parseInt(img.label?.match(/\d+/)?.[0] || '1') - 1
      bathroomPhotos.value[idx] = { preview: normalizeImageUrl(img.image_url) }
    })

    const extrasFromApi = images.filter((img) => img.is_extra)
    if (extrasFromApi.length) {
      const groups = {}
      extrasFromApi.forEach((img) => {
        const label = img.label || 'Extra'
        if (!groups[label]) groups[label] = { label, files: [], previews: [] }
        groups[label].previews.push(normalizeImageUrl(img.image_url))
      })
      extras.value = Object.values(groups)
    }
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
      warning.value = `La propiedad se guardo, pero ${uploadErrors} imagen(es) no se pudieron subir.`
    }

    const msg = isEdit.value ? 'Propiedad actualizada correctamente' : 'Propiedad publicada correctamente'
    addToast({ message: msg, type: 'success' })
    success.value = true
    setTimeout(() => router.push(returnPath.value), 1800)
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al guardar la propiedad'
  } finally {
    loading.value = false
  }
}

onMounted(loadProperty)
onUnmounted(() => { destroyMap(); formWatcher() })
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
        <div class="success-icon">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>
        </div>
        <h2>{{ isEdit ? 'Propiedad actualizada' : 'Propiedad publicada' }}</h2>
        <p>{{ isEdit ? 'Los cambios se guardaron correctamente. Redirigiendo...' : 'Quedara pendiente hasta ser aprobada. Redirigiendo...' }}</p>
      </div>

      <div v-if="!success && initialLoading" class="alert alert-warning">
        Cargando propiedad...
      </div>

      <div v-else-if="needsEmailVerification" class="verify-card">
        <div class="verify-icon">
          <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>
        </div>
        <h2>Verifica tu correo electronico</h2>
        <p>Para publicar una propiedad, primero debes verificar tu correo <strong>{{ auth.userEmail }}</strong>.</p>
        <p class="verify-hint">Revisa tu bandeja de entrada y la carpeta de spam para encontrar el email de verificacion.</p>
        <button class="verify-btn" :disabled="sendingEmail" @click="resendEmail">
          {{ sendingEmail ? 'Enviando...' : emailSent ? 'Enviado. Revisa tu correo' : 'Reenviar email de verificacion' }}
        </button>
        <p v-if="emailSent" class="verify-sent">Email reenviado correctamente</p>
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
              <svg v-if="currentStep > index" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>
              <span v-else>{{ index + 1 }}</span>
            </span>
            <span class="step-label">{{ step }}</span>
          </button>
        </div>

        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress }"></div>
        </div>

        <div v-if="error" class="alert alert-error">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m21.7 18-8-14a2 2 0 0 0-3.4 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3Z"/><path d="M12 9v4M12 17h.01"/></svg>
          {{ error }}
        </div>
        <div v-if="warning" class="alert alert-warning">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2 3 14h8l-1 8 10-12h-8l1-8Z"/></svg>
          {{ warning }}
        </div>

        <form @submit.prevent="submit" class="form">

          <!-- STEP 1 -->
          <div v-if="currentStep === 0" class="step-panel">
            <div class="panel-header">
              <span class="panel-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="4" width="12" height="18" rx="2"/><path d="M9 4a3 3 0 0 1 6 0M9 9h6M9 13h6M9 17h4"/></svg>
              </span>
              <div><h2>Informacion general</h2><p>Datos basicos de la propiedad</p></div>
            </div>
            <div class="fields-grid">
              <div class="field">
                <label>Titulo <span class="req">*</span></label>
                <input v-model="form.title" type="text" placeholder="Casa en Fraccionamiento Las Palmas" @blur="formatTitle" />
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
              <span class="panel-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 21v-7h6v7"/></svg>
              </span>
              <div>
                <h2>Fotos de fachada</h2>
                <p>Agrega las imagenes una por una para conservar el orden.</p>
              </div>
            </div>

            <div class="photo-uploader">
              <label :class="['upload-zone', { disabled: generalPreviews.length >= MAX_GENERAL_FILES || loading }]">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  :disabled="generalPreviews.length >= MAX_GENERAL_FILES || loading"
                  @change="onGeneralFilesChange"
                />
                <div class="upload-content">
                  <div class="upload-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
                  </div>
                  <strong>{{ generalPreviews.length ? 'Agregar otra foto' : 'Agregar foto principal' }}</strong>
                  <span>Selecciona una imagen por vez</span>
                  <small>{{ generalPreviews.length }}/{{ MAX_GENERAL_FILES }} fotos - JPG, PNG o WEBP - {{ MAX_SIZE_MB }}MB c/u</small>
                </div>
              </label>

              <div class="upload-guidance">
                <strong>Orden de publicacion</strong>
                <span>La foto marcada como Principal sera la primera que se suba.</span>
              </div>
            </div>

            <div v-if="generalPreviews.length" class="ordered-photos">
              <article v-for="(photo, idx) in generalPreviews" :key="`${photo.preview}-${idx}`" class="ordered-photo">
                <div class="photo-frame">
                  <img :src="photo.preview" :alt="`Foto general ${idx + 1}`" />
                  <span v-if="idx === 0" class="main-badge">Principal</span>
                  <span class="order-badge">{{ idx + 1 }}</span>
                </div>
                <div class="photo-meta">
                  <strong>{{ photo.name || `Foto ${idx + 1}` }}</strong>
                  <span v-if="!photo.existing">Lista para subir</span>
                </div>
                <div v-if="!photo.existing" class="photo-actions">
                  <button type="button" :disabled="idx === 0" aria-label="Mover antes" @click="moveGeneralPhoto(idx, -1)">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m18 15-6-6-6 6"/></svg>
                  </button>
                  <button type="button" :disabled="idx === generalPreviews.length - 1" aria-label="Mover despues" @click="moveGeneralPhoto(idx, 1)">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
                  </button>
                  <button type="button" class="danger" aria-label="Quitar foto" @click="removeGeneralPhoto(idx)">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>
                  </button>
                </div>
              </article>
            </div>

            <div v-else class="empty-photos">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 21v-7h6v7"/></svg>
              <div>
                <strong>Aun no hay fotos de fachada</strong>
                <span>Agrega al menos una para continuar.</span>
              </div>
            </div>
          </div>

          <!-- STEP 3 -->
          <div v-if="currentStep === 2" class="step-panel">
            <div class="panel-header">
              <span class="panel-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 10c0 5.5-8 11-8 11s-8-5.5-8-11a8 8 0 1 1 16 0Z"/><path d="M12 10.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z"/></svg>
              </span>
              <div><h2>Ubicacion</h2><p>Donde se encuentra la propiedad</p></div>
            </div>
            <div class="location-layout">
              <div class="location-fields">
                <div class="field">
                  <label>Ciudad <span class="req">*</span></label>
                  <div class="city-select-wrapper">
                    <div class="city-display" @click="showCityDropdown = !showCityDropdown">
                      <span>{{ form.city || 'Selecciona una ciudad' }}</span>
                      <span class="city-arrow">
                        <svg v-if="showCityDropdown" viewBox="0 0 24 24" aria-hidden="true"><path d="m18 15-6-6-6 6"/></svg>
                        <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
                      </span>
                    </div>
                    <div v-if="showCityDropdown" class="city-dropdown">
                      <input
                        v-model="citySearch"
                        type="text"
                        placeholder="Buscar ciudad..."
                        class="city-search-input"
                        @click.stop
                      />
                      <div class="city-list">
                        <div
                          v-for="city in filteredCities"
                          :key="city"
                          class="city-option"
                          :class="{ active: form.city === city }"
                          @click="selectCity(city)"
                        >{{ city }}</div>
                        <div v-if="!filteredCities.length" class="city-no-results">Sin resultados</div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="field">
                  <label>Direccion <span class="req">*</span></label>
                  <div class="input-row">
                    <input v-model="form.address" type="text" placeholder="Calle Reforma 123, Col. Centro" @keyup.enter="searchAddress" />
                    <button type="button" class="btn-search-map" :disabled="loading" @click="searchAddress">Buscar en mapa</button>
                  </div>
                </div>
                <div class="grid-2">
                  <div class="field"><label>Latitud</label><input v-model="form.latitude" type="number" step="any" placeholder="16.7521" /></div>
                  <div class="field"><label>Longitud</label><input v-model="form.longitude" type="number" step="any" placeholder="-93.1147" /></div>
                </div>
              </div>
              <div ref="mapContainer" class="map-container"></div>
            </div>
          </div>

          <!-- STEP 4 -->
          <div v-if="currentStep === 3" class="step-panel">
            <div class="panel-header">
              <span class="panel-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 21v-7h6v7"/></svg>
              </span>
              <div><h2>Caracteristicas</h2><p>Detalles fisicos de la propiedad</p></div>
            </div>
            <div class="features-cards">
              <div class="feature-card">
                <span class="feature-emoji">
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 11V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v6M4 21v-8h16v8M2 13h20M7 11V8h4v3M13 11V8h4v3"/></svg>
                </span>
                <label>Recamaras</label>
                <input v-model="form.bedrooms" type="number" min="0" placeholder="0" />
              </div>
              <div class="feature-card">
                <span class="feature-emoji">
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 12V5a3 3 0 0 1 6 0M5 12h16v2a6 6 0 0 1-6 6H9a6 6 0 0 1-6-6v-2h2ZM8 20v2M16 20v2"/></svg>
                </span>
                <label>baños</label>
                <input v-model="form.bathrooms" type="number" min="0" placeholder="0" />
              </div>
              <div class="feature-card">
                <span class="feature-emoji">
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21h18M7 21V7h10v14M7 7l5-4 5 4M10 11h4M10 15h4"/></svg>
                </span>
                <label>Superficie m2</label>
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
              <span class="panel-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 15 4-4 4 4 3-3 7 7"/><circle cx="16" cy="9" r="1.5"/></svg>
              </span>
              <div><h2>Fotos por apartados</h2><p>Agrega fotos especificas de cada espacio</p></div>
            </div>

            <div v-if="bedroomsCount" class="section-block">
              <div class="section-block-header">
                <span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 11V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v6M4 21v-8h16v8M2 13h20M7 11V8h4v3M13 11V8h4v3"/></svg> Recamaras</span>
                <span class="count-badge">{{ bedroomsCount }} foto(s)</span>
              </div>
              <div class="slot-grid">
                <label v-for="index in bedroomsCount" :key="`bed-${index}`" class="photo-slot">
                  <img v-if="bedroomPhotos[index - 1]?.preview" :src="bedroomPhotos[index - 1].preview" :alt="`Recamara ${index}`" />
                  <div v-else class="slot-empty">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
                    <small>Recamara {{ index }}</small>
                  </div>
                  <input type="file" accept="image/jpeg,image/png,image/webp" @change="onSinglePhotoChange($event, bedroomPhotos, index - 1)" />
                  <button v-if="bedroomPhotos[index - 1]?.preview" type="button" class="slot-remove" @click.prevent="removeBedroomPhoto(index - 1)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
                </label>
              </div>
            </div>

            <div v-if="bathroomsCount" class="section-block">
              <div class="section-block-header">
                <span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 12V5a3 3 0 0 1 6 0M5 12h16v2a6 6 0 0 1-6 6H9a6 6 0 0 1-6-6v-2h2ZM8 20v2M16 20v2"/></svg> baños</span>
                <span class="count-badge">{{ bathroomsCount }} foto(s)</span>
              </div>
              <div class="slot-grid">
                <label v-for="index in bathroomsCount" :key="`bath-${index}`" class="photo-slot">
                  <img v-if="bathroomPhotos[index - 1]?.preview" :src="bathroomPhotos[index - 1].preview" :alt="`Bano ${index}`" />
                  <div v-else class="slot-empty">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
                    <small>Bano {{ index }}</small>
                  </div>
                  <input type="file" accept="image/jpeg,image/png,image/webp" @change="onSinglePhotoChange($event, bathroomPhotos, index - 1)" />
                  <button v-if="bathroomPhotos[index - 1]?.preview" type="button" class="slot-remove" @click.prevent="removeBathroomPhoto(index - 1)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
                </label>
              </div>
            </div>

            <div class="section-block">
              <div class="section-block-header">
                <span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.4 5 5.6.8-4 3.9.9 5.5-4.9-2.6-4.9 2.6.9-5.5-4-3.9 5.6-.8L12 3Z"/></svg> Extras</span>
                <button type="button" class="add-extra-btn" @click="addExtra">
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
                  Agregar espacio
                </button>
              </div>
              <div v-for="(extra, index) in extras" :key="index" class="extra-row">
                <div class="field"><label>Nombre del espacio</label><input v-model="extra.label" type="text" placeholder="Cocina, patio, sala..." /></div>
                <div class="field"><label>Fotos</label><input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="onExtraFilesChange($event, index)" /></div>
                <button type="button" class="remove-btn" @click="removeExtra(index)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg> Quitar</button>
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
            <button v-if="currentStep > 0" class="btn-back" type="button" :disabled="loading" @click="prevStep">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m7 7-7-7 7-7"/></svg>
              Atras
            </button>
            <div class="actions-right">
              <span class="step-hint">Paso {{ currentStep + 1 }} de {{ steps.length }}</span>
              <button v-if="!isLastStep" class="btn-next" type="button" :disabled="loading" @click="nextStep">
                Siguiente
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>
              </button>
              <button v-else class="btn-next btn-publish" type="submit" :disabled="loading">
                <svg v-if="!loading" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>
                {{ loading ? "Guardando..." : (isEdit ? "Guardar cambios" : "Publicar propiedad") }}
              </button>
            </div>
          </div>

        </form>
      </template>
    </div>

  </section>
</template>

<style scoped>


* { box-sizing: border-box; }

svg {
  width: 18px;
  height: 18px;
  display: block;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex-shrink: 0;
}

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
.step-circle svg { width: 14px; height: 14px; }
.step-btn.active .step-circle, .step-btn.done .step-circle { background: var(--gold); color: var(--navy); }
.step-label { display: none; }
@media (min-width: 640px) { .step-label { display: block; } }

/* PROGRESS */
.progress-bar { height: 4px; background: var(--line); border-radius: 0 0 8px 8px; overflow: hidden; margin-bottom: 24px; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--gold), var(--gold-light)); transition: width 0.3s ease; }

/* ALERTS */
.alert { display: flex; align-items: center; gap: 10px; padding: 12px 16px; border-radius: 10px; font-size: 13px; font-weight: 500; margin-bottom: 16px; }
.alert svg { width: 16px; height: 16px; }
.alert-error { background: var(--error-bg); color: var(--error); border: 1px solid #fecaca; }
.alert-warning { background: #fff7ed; color: #9a3412; border: 1px solid #fdba74; }

/* STEP PANEL */
.step-panel { background: var(--white); border: 1px solid var(--line); border-radius: 16px; padding: 28px; box-shadow: 0 2px 16px rgba(7,23,45,0.06); display: flex; flex-direction: column; gap: 24px; }
.panel-header { display: flex; align-items: flex-start; gap: 14px; padding-bottom: 20px; border-bottom: 1px solid var(--line); }
.panel-icon { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 12px; background: #f0ece4; color: var(--navy); flex-shrink: 0; margin-top: 2px; }
.panel-icon svg { width: 22px; height: 22px; }
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
.upload-zone.disabled { cursor: not-allowed; opacity: 0.65; }
.upload-zone.disabled input[type="file"] { cursor: not-allowed; }
.upload-icon { display: grid; place-items: center; width: 48px; height: 48px; border-radius: 12px; margin-bottom: 4px; background: #f0ece4; color: var(--navy); }
.upload-content strong { font-size: 15px; color: var(--navy); font-weight: 700; }
.upload-content span { font-size: 13px; color: var(--muted); }
.upload-content small { font-size: 12px; color: #b5ae9f; }
.photo-uploader { display: grid; grid-template-columns: minmax(0, 1fr) 230px; gap: 14px; align-items: stretch; }
.photo-uploader .upload-content { min-height: 190px; justify-content: center; }
.upload-guidance { display: flex; flex-direction: column; justify-content: center; gap: 8px; padding: 18px; border: 1.5px solid rgba(212,163,74,0.3); border-radius: 14px; background: #fdf8ee; color: var(--navy); }
.upload-guidance strong { font-size: 14px; font-weight: 800; }
.upload-guidance span { color: var(--muted); font-size: 13px; line-height: 1.6; }

/* PREVIEW */
.preview-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; }
.preview-item { position: relative; border-radius: 10px; overflow: hidden; border: 1.5px solid var(--line); aspect-ratio: 4/3; }
.preview-item img { width: 100%; height: 100%; object-fit: cover; }
.main-badge { position: absolute; top: 6px; left: 6px; background: var(--gold); color: var(--navy); font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 20px; }
.ordered-photos { display: grid; gap: 10px; }
.ordered-photo { display: grid; grid-template-columns: 112px minmax(0, 1fr) auto; gap: 14px; align-items: center; padding: 10px; border: 1.5px solid var(--line); border-radius: 14px; background: #fff; transition: border-color 0.2s, box-shadow 0.2s; }
.ordered-photo:hover { border-color: rgba(212,163,74,0.55); box-shadow: 0 8px 18px rgba(7,23,45,0.06); }
.photo-frame { position: relative; width: 112px; aspect-ratio: 4/3; overflow: hidden; border-radius: 10px; background: #f0ece4; }
.photo-frame img { width: 100%; height: 100%; object-fit: cover; }
.order-badge { position: absolute; right: 6px; bottom: 6px; min-width: 24px; height: 24px; display: grid; place-items: center; border-radius: 50%; background: rgba(7,23,45,0.82); color: #fff; font-size: 11px; font-weight: 800; }
.photo-meta { min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.photo-meta strong { color: var(--navy); font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.photo-meta span { color: var(--muted); font-size: 12px; }
.photo-actions { display: flex; gap: 6px; }
.photo-actions button { width: 34px; height: 34px; display: grid; place-items: center; border: 1.5px solid var(--line); border-radius: 9px; background: #faf9f6; color: var(--navy); transition: background 0.2s, border-color 0.2s; }
.photo-actions button:hover:not(:disabled) { border-color: var(--gold); background: #fdf8ee; }
.photo-actions button:disabled { opacity: 0.35; cursor: not-allowed; }
.photo-actions .danger { color: var(--error); border-color: #fecaca; background: #fff8f8; }
.photo-actions .danger:hover:not(:disabled) { background: #fef2f2; border-color: #fca5a5; }
.empty-photos { display: flex; align-items: center; gap: 12px; padding: 16px; border: 1.5px dashed var(--line); border-radius: 14px; background: #faf9f6; color: var(--muted); }
.empty-photos > svg { width: 30px; height: 30px; color: var(--gold); }
.empty-photos strong { display: block; color: var(--navy); font-size: 14px; }
.empty-photos span { display: block; margin-top: 2px; font-size: 12px; }

/* LOCATION */
.location-layout { display: grid; grid-template-columns: 1fr 300px; gap: 18px; }
.location-fields { display: flex; flex-direction: column; gap: 14px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.input-row { display: flex; gap: 8px; }
.input-row input { flex: 1; }
.btn-search-map { padding: 11px 16px; border: 1.5px solid var(--gold); border-radius: 10px; background: var(--gold); color: var(--navy); font-size: 13px; font-weight: 700; font-family: "Poppins", sans-serif; cursor: pointer; white-space: nowrap; transition: background 0.2s; }
.btn-search-map:hover { background: var(--gold-light); }
.btn-search-map:disabled { opacity: 0.5; cursor: not-allowed; }
.map-container { min-height: 220px; border: 2px dashed var(--line); border-radius: 14px; }
.city-select-wrapper { position: relative; }
.city-display { display: flex; align-items: center; justify-content: space-between; padding: 11px 14px; border: 1.5px solid var(--line); border-radius: 10px; background: #faf9f6; cursor: pointer; font-size: 14px; color: var(--navy); transition: border-color 0.2s; }
.city-display:hover, .city-select-wrapper:focus-within .city-display { border-color: var(--gold); background: var(--white); }
.city-arrow { color: var(--muted); }
.city-arrow svg { width: 16px; height: 16px; }
.city-dropdown { position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: var(--white); border: 1.5px solid var(--line); border-radius: 12px; box-shadow: 0 8px 24px rgba(7,23,45,0.15); z-index: 50; overflow-y: auto; }
.city-search-input { width: 100%; padding: 10px 14px; border: none; border-bottom: 1px solid var(--line); background: #faf9f6; font-size: 13px; font-family: "Poppins", sans-serif; outline: none; }
.city-list { max-height: 240px; overflow-y: auto; }
.city-option { padding: 10px 14px; font-size: 13px; color: var(--navy); cursor: pointer; transition: background 0.15s; }
.city-option:hover { background: #fdf8ee; }
.city-option.active { background: #fdf8ee; color: var(--gold); font-weight: 600; }
.city-no-results { padding: 10px 14px; font-size: 12px; color: var(--muted); text-align: center; }

/* FEATURES */
.features-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.feature-card { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 20px 16px; background: #faf9f6; border: 1.5px solid var(--line); border-radius: 14px; text-align: center; }
.feature-emoji { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 12px; background: #f0ece4; color: var(--navy); }
.feature-emoji svg { width: 24px; height: 24px; }
.feature-card label { font-size: 13px; font-weight: 600; color: var(--navy); }
.feature-card input { text-align: center; font-size: 18px; font-weight: 700; padding: 8px; max-width: 100px; }

/* SECTION BLOCKS */
.section-block { border: 1.5px solid var(--line); border-radius: 14px; overflow: hidden; }
.section-block-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 18px; background: #faf9f6; border-bottom: 1px solid var(--line); font-size: 14px; font-weight: 700; color: var(--navy); }
.section-block-header > span:first-child { display: inline-flex; align-items: center; gap: 8px; min-width: 0; }
.section-block-header svg { width: 17px; height: 17px; color: var(--gold); }
.count-badge { font-size: 11px; font-weight: 600; color: var(--muted); background: var(--line); padding: 3px 10px; border-radius: 20px; }
.add-extra-btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; background: var(--gold); color: var(--navy); border: none; border-radius: 8px; padding: 6px 14px; font-size: 12px; font-weight: 700; font-family: "Poppins", sans-serif; cursor: pointer; transition: background 0.2s; }
.add-extra-btn svg { width: 13px; height: 13px; }
.add-extra-btn:hover { background: var(--gold-light); }
.slot-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; padding: 16px; }
.photo-slot { position: relative; aspect-ratio: 4/3; border: 2px dashed #d4c9b8; border-radius: 12px; overflow: hidden; cursor: pointer; transition: border-color 0.2s; }
.photo-slot:hover { border-color: var(--gold); }
.photo-slot input[type="file"] { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; }
.photo-slot img { width: 100%; height: 100%; object-fit: cover; }
.slot-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 4px; color: var(--muted); }
.slot-empty svg { width: 24px; height: 24px; color: var(--gold); }
.slot-empty small { font-size: 11px; font-weight: 600; }
.slot-remove { position: absolute; top: 6px; right: 6px; width: 26px; height: 26px; display: grid; place-items: center; border: 1px solid rgba(255,255,255,0.7); border-radius: 50%; background: rgba(7,23,45,0.78); color: #fff; cursor: pointer; transition: background 0.2s; }
.slot-remove:hover { background: var(--error); }
.slot-remove svg { width: 13px; height: 13px; }
.extra-row { display: grid; grid-template-columns: 1fr 1fr auto; gap: 12px; align-items: end; padding: 16px; border-bottom: 1px solid var(--line); }
.extra-row:last-child { border-bottom: none; }
.extra-preview { grid-column: 1/-1; }
.remove-btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 10px 14px; border: 1.5px solid #fecaca; border-radius: 10px; background: #fef2f2; color: var(--error); font-size: 12px; font-weight: 700; font-family: "Poppins", sans-serif; cursor: pointer; white-space: nowrap; transition: background 0.2s; }
.remove-btn svg { width: 13px; height: 13px; }
.remove-btn:hover { background: #fee2e2; }

/* ACTIONS */
.form { display: flex; flex-direction: column; gap: 16px; }
.actions { display: flex; align-items: center; justify-content: space-between; background: var(--white); border: 1px solid var(--line); border-radius: 14px; padding: 16px 20px; box-shadow: 0 2px 12px rgba(7,23,45,0.06); }
.actions-right { display: flex; align-items: center; gap: 14px; }
.step-hint { font-size: 12px; color: var(--muted); font-weight: 500; }
.btn-back { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 11px 22px; border: 1.5px solid var(--line); border-radius: 10px; background: transparent; color: var(--navy); font-size: 14px; font-weight: 600; font-family: "Poppins", sans-serif; cursor: pointer; transition: background 0.2s; }
.btn-back svg { width: 16px; height: 16px; }
.btn-back:hover { background: #f0ece4; }
.btn-back:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-next { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 11px 28px; border: none; border-radius: 10px; background: var(--navy); color: var(--white); font-size: 14px; font-weight: 700; font-family: "Poppins", sans-serif; cursor: pointer; transition: background 0.2s, box-shadow 0.2s; box-shadow: 0 4px 14px rgba(7,23,45,0.2); }
.btn-next svg { width: 16px; height: 16px; }
.btn-next:hover { background: var(--navy-mid); }
.btn-next:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; }
.btn-publish { background: var(--gold); color: var(--navy); box-shadow: 0 4px 14px rgba(212,163,74,0.35); }
.btn-publish:hover { background: var(--gold-light); }

/* VERIFY GATE */
.verify-card { background: var(--white); border: 1px solid var(--line); border-radius: 16px; padding: 60px 40px; text-align: center; box-shadow: 0 4px 24px rgba(7,23,45,0.08); max-width: 480px; margin: 40px auto; }
.verify-icon { width: 64px; height: 64px; background: linear-gradient(135deg, var(--gold), var(--gold-light)); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--navy); margin: 0 auto 20px; }
.verify-icon svg { width: 28px; height: 28px; }
.verify-card h2 { font-size: 22px; color: var(--navy); margin: 0 0 12px; }
.verify-card p { color: var(--muted); font-size: 14px; margin: 0 0 8px; }
.verify-hint { font-size: 13px; color: var(--muted); margin-bottom: 24px !important; }
.verify-btn { padding: 12px 28px; border: none; border-radius: 10px; background: var(--gold); color: var(--navy); font-size: 14px; font-weight: 700; cursor: pointer; }
.verify-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.verify-sent { margin-top: 12px !important; color: #065f46 !important; font-weight: 600; }

/* SUCCESS */
.success-card { background: var(--white); border: 1px solid var(--line); border-radius: 16px; padding: 60px 40px; text-align: center; box-shadow: 0 4px 24px rgba(7,23,45,0.08); }
.success-icon { width: 64px; height: 64px; background: linear-gradient(135deg, var(--gold), var(--gold-light)); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--navy); margin: 0 auto 20px; }
.success-icon svg { width: 30px; height: 30px; }
.success-card h2 { font-size: 24px; color: var(--navy); margin: 0 0 8px; }
.success-card p { color: var(--muted); font-size: 15px; margin: 0; }

/* RESPONSIVE */
@media (max-width: 860px) {
  .fields-grid, .location-layout, .grid-2, .photo-uploader { grid-template-columns: 1fr; }
  .wizard-nav { flex-wrap: wrap; }
  .step-btn { flex: 1 1 calc(50% - 4px); }
}
@media (max-width: 560px) {
  .create { padding: 32px 14px 56px; }
  h1 { font-size: 28px; }
  .step-panel { padding: 18px; }
  .features-cards { grid-template-columns: 1fr; }
  .ordered-photo { grid-template-columns: 88px minmax(0, 1fr); }
  .photo-frame { width: 88px; }
  .photo-actions { grid-column: 1/-1; justify-content: flex-end; }
  .extra-row { grid-template-columns: 1fr; }
  .actions { flex-direction: column; gap: 10px; }
  .actions-right { width: 100%; justify-content: flex-end; }
  .page-header { flex-direction: column; gap: 8px; }
}
</style>


<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/composables/useToast'
import Breadcrumb from '@/components/shared/Breadcrumb.vue'

const props = defineProps({
  role: {
    type: String,
    required: true,
    validator: (v) => ['client', 'advisor'].includes(v)
  },
  title: {
    type: String,
    default: 'Mi Perfil'
  },
  eyebrow: {
    type: String,
    default: ''
  }
})

const { addToast } = useToast()
const auth = useAuthStore()

const loading = ref(true)
const saving = ref(false)
const error = ref('')

const form = ref({
  full_name: '',
  email: '',
  phone: ''
})

const originalData = ref({})

const fetchProfile = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/users/${auth.userId}`, {
      headers: { ...auth.authHeaders }
    })
    if (!response.ok) throw new Error('Error al cargar perfil')
    const data = await response.json()
    form.value.full_name = data.full_name || ''
    form.value.email = data.email || ''
    form.value.phone = data.phone || ''
    originalData.value = { ...form.value }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const hasChanges = () => {
  return form.value.full_name !== originalData.value.full_name ||
         form.value.phone !== originalData.value.phone
}

const saveProfile = async () => {
  if (!hasChanges()) {
    addToast({ message: 'No hay cambios para guardar', type: 'info' })
    return
  }

  saving.value = true
  error.value = ''
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/users/${auth.userId}`, {
      method: 'PUT',
      headers: {
        ...auth.authHeaders,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        full_name: form.value.full_name,
        phone: form.value.phone
      })
    })
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Error al guardar')
    }
    const data = await response.json()
    originalData.value = { ...form.value }
    addToast({ message: 'Perfil actualizado correctamente', type: 'success' })
  } catch (err) {
    error.value = err.message
    addToast({ message: err.message, type: 'error' })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchProfile()
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordError = ref('')
const passwordSaving = ref(false)

const validatePasswordForm = () => {
  passwordError.value = ''
  if (!passwordForm.value.current_password) {
    passwordError.value = 'Ingresa tu contraseña actual'
    return false
  }
  if (!passwordForm.value.new_password) {
    passwordError.value = 'Ingresa una nueva contraseña'
    return false
  }
  if (passwordForm.value.new_password.length < 8) {
    passwordError.value = 'La nueva contraseña debe tener al menos 8 caracteres'
    return false
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = 'Las contraseñas nuevas no coinciden'
    return false
  }
  if (passwordForm.value.current_password === passwordForm.value.new_password) {
    passwordError.value = 'La nueva contraseña debe ser diferente a la actual'
    return false
  }
  return true
}

const changePassword = async () => {
  if (!validatePasswordForm()) return

  passwordSaving.value = true
  passwordError.value = ''
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/change-password`, {
      method: 'POST',
      headers: {
        ...auth.authHeaders,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        current_password: passwordForm.value.current_password,
        new_password: passwordForm.value.new_password
      })
    })
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Error al cambiar contraseña')
    }
    passwordForm.value = { current_password: '', new_password: '', confirm_password: '' }
    addToast({ message: 'Contraseña cambiada correctamente', type: 'success' })
  } catch (err) {
    passwordError.value = err.message
    addToast({ message: err.message, type: 'error' })
  } finally {
    passwordSaving.value = false
  }
}
</script>

<template>
  <section class="profile-page">
    <header class="page-header">
      <p>{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
    </header>

    <Breadcrumb :crumbs="[{ label: title, path: `/${role}/perfil` }]" />

    <div v-if="loading" class="state">Cargando perfil...</div>
    <div v-else-if="error && !form.email" class="state error-msg">{{ error }}</div>

    <template v-else>
      <div class="cards-grid">
        <article class="card">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
          <div class="card-content">
            <h3>Información Personal</h3>
            <p>Actualiza tu información de contacto</p>
          </div>

          <div class="form-fields">
            <div class="field">
              <label>Nombre completo</label>
              <input v-model="form.full_name" type="text" placeholder="Tu nombre completo" />
            </div>

            <div class="field">
              <label>Email</label>
              <input v-model="form.email" type="email" disabled class="disabled" />
              <span class="hint">El email no se puede cambiar</span>
            </div>

            <div class="field">
              <label>Teléfono</label>
              <input v-model="form.phone" type="tel" placeholder="Tu número de teléfono" />
            </div>

            <div v-if="error" class="field-error">{{ error }}</div>

            <button
              class="btn-save"
              :disabled="saving || !hasChanges()"
              @click="saveProfile"
            >
              <span v-if="saving">Guardando...</span>
              <span v-else>Guardar cambios</span>
            </button>
          </div>
        </article>

        <article class="card">
          <div class="card-icon lock">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          </div>
          <div class="card-content">
            <h3>Seguridad</h3>
            <p>Cambia tu contraseña cuando lo necesites</p>
          </div>

          <div class="form-fields">
            <div class="field">
              <label>Contraseña actual</label>
              <input v-model="passwordForm.current_password" type="password" placeholder="Tu contraseña actual" />
            </div>

            <div class="field">
              <label>Nueva contraseña</label>
              <input v-model="passwordForm.new_password" type="password" placeholder="Mínimo 8 caracteres" />
              <span class="hint">La contraseña debe tener al menos 8 caracteres</span>
            </div>

            <div class="field">
              <label>Confirmar nueva contraseña</label>
              <input v-model="passwordForm.confirm_password" type="password" placeholder="Repite la nueva contraseña" />
            </div>

            <div v-if="passwordError" class="field-error">{{ passwordError }}</div>

            <button
              class="btn-save"
              :disabled="passwordSaving || !passwordForm.current_password || !passwordForm.new_password || !passwordForm.confirm_password"
              @click="changePassword"
            >
              <span v-if="passwordSaving">Cambiando...</span>
              <span v-else>Cambiar contraseña</span>
            </button>
          </div>
        </article>
      </div>
    </template>
  </section>
</template>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
}

.page-header {
  margin-bottom: 8px;
}

.page-header p {
  margin: 0 0 4px;
  color: var(--color-gold);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.page-header h1 {
  margin: 0;
  color: var(--color-navy);
  font-size: 28px;
  font-weight: 800;
}

.state {
  padding: 24px;
  text-align: center;
  color: var(--color-muted);
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
  font-size: 14px;
}

.error-msg {
  color: #991b1b;
}

.cards-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
}

.card {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08);
  transition: 0.3s ease;
}

.card:hover {
  border-color: var(--color-gold);
  box-shadow: 0 14px 32px rgba(7, 23, 45, 0.12);
}

.card-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: rgba(214, 168, 72, 0.12);
  color: var(--color-gold);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}

.card-icon.lock {
  background: rgba(7, 23, 45, 0.08);
  color: var(--color-navy);
}

.card-content {
  margin-bottom: 20px;
}

.card-content h3 {
  margin: 0 0 6px;
  color: var(--color-navy);
  font-size: 18px;
  font-weight: 700;
}

.card-content p {
  margin: 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.4;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px
}

.field label {
  color: var(--color-navy);
  font-size: 13px;
  font-weight: 600
}

.field input {
  padding: 12px 14px;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-navy);
  background: #fff;
  transition: 0.3s ease
}

.field input::placeholder {
  color: #9ca3af
}

.field input:focus {
  outline: none;
  border-color: var(--color-gold);
  box-shadow: 0 0 0 3px rgba(214, 168, 72, 0.12)
}

.field input.disabled {
  background: #f3f4f6;
  color: var(--color-muted);
  cursor: not-allowed
}

.field .hint {
  color: var(--color-muted);
  font-size: 11px
}

.field-error {
  padding: 10px 14px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 13px
}

.btn-save {
  margin-top: 8px;
  padding: 12px 20px;
  background: var(--color-navy);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s ease
}

.btn-save:hover:not(:disabled) {
  background: #0a1525
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed
}

@media (max-width: 768px) {
  .cards-grid { grid-template-columns: 1fr; }
  .page-header h1 { font-size: 24px; }
}
@media (max-width: 480px) {
  .profile-page { padding: 16px; }
  .card { padding: 16px; }
  .card-content h3 { font-size: 16px; }
  .field input { padding: 10px 12px; font-size: 13px; }
  .btn-save { width: 100%; }
}
</style>

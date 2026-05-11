<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { usePropertyStore } from '@/stores/propertyStore'
import { storeToRefs } from 'pinia'
import { appointmentsApi } from '@/api/appointments'
import ClientDashboardHeader from '@/components/client/dashboard/ClientDashboardHeader.vue'
import Toast from '@/components/shared/Toast.vue'
import AppIcon from '@/components/shared/AppIcon.vue'

const router = useRouter()
const auth = useAuthStore()
const propertyStore = usePropertyStore()
const { properties, loading: propsLoading } = storeToRefs(propertyStore)

const appointments = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const showForm = ref(false)
const toastState = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const showToast = (message, type = 'success') => {
  clearTimeout(toastTimeout)
  toastState.value = { show: true, message, type }
  toastTimeout = setTimeout(() => { toastState.value.show = false }, 3000)
}

// Formulario de nueva cita
const form = ref({
  property_id: '',
  scheduled_date: '',
  scheduled_time: '',
  notes: '',
  appointment_type: 'viewing'
})

const myProperties = computed(() => {
  const uid = Number(auth.userId)
  return properties.value.filter(p => p.submitted_by_user_id === uid)
})

const today = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().split('T')[0]
})

const minDateTime = computed(() => {
  const now = new Date()
  now.setHours(now.getHours() + 1)
  return now.toISOString().slice(0, 16)
})

const fetchAppointments = async () => {
  try {
    const { data } = await appointmentsApi.getByClient()
    appointments.value = data.appointments || data.items || data
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Error al cargar citas'
    console.error('Error fetching appointments:', err)
  } finally {
    loading.value = false
  }
}

const fetchProperties = async () => {
  if (!propsLoading.value) {
    await propertyStore.fetchProperties()
  }
}

const statusMap = {
  pending: { label: 'Pendiente', cls: 'pendiente' },
  confirmed: { label: 'Confirmada', cls: 'confirmada' },
  completed: { label: 'Completada', cls: 'completada' },
  cancelled: { label: 'Cancelada', cls: 'cancelada' }
}

const validateForm = () => {
  error.value = ''
  if (!form.value.property_id) {
    error.value = 'Selecciona una propiedad'
    return false
  }
  if (!form.value.scheduled_date || !form.value.scheduled_time) {
    error.value = 'Selecciona fecha y hora'
    return false
  }
  if (form.value.notes.length > 500) {
    error.value = 'Las notas no pueden superar 500 caracteres'
    return false
  }
  return true
}

const createAppointment = async () => {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    const dateTime = `${form.value.scheduled_date}T${form.value.scheduled_time}`
    await appointmentsApi.create({
      client_id: Number(auth.userId),
      property_id: parseInt(form.value.property_id),
      scheduled_date: dateTime,
      notes: form.value.notes,
      appointment_type: form.value.appointment_type
    })
    showForm.value = false
    form.value = { property_id: '', scheduled_date: '', scheduled_time: '', notes: '', appointment_type: 'viewing' }
    await fetchAppointments()
    showToast('Cita solicitada correctamente', 'success')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message
    showToast(error.value, 'error')
  } finally {
    saving.value = false
  }
}

const cancelAppointment = async (appointmentId) => {
  if (!confirm('¿Cancelar esta cita?')) return
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/appointments/${appointmentId}`, {
      method: 'DELETE',
      headers: { ...auth.authHeaders }
    })
    if (!response.ok) throw new Error('Error al cancelar cita')
    await fetchAppointments()
    showToast('Cita cancelada', 'info')
  } catch (err) {
    error.value = err.message
    showToast(err.message, 'error')
  }
}

const formattedDateTime = (dateTime) => {
  if (!dateTime) return 'Sin fecha'
  const date = new Date(dateTime)
  return date.toLocaleDateString('es-MX', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

onMounted(async () => {
  await Promise.all([fetchAppointments(), fetchProperties()])
})

onUnmounted(() => {
  clearTimeout(toastTimeout)
})
</script>

<template>
  <section class="appointments-page">
    <ClientDashboardHeader
      eyebrow="Panel de Cliente"
      title="Mis Citas"
    />

    <div class="header-actions">
      <button v-if="!showForm" class="btn-add" @click="showForm = true">
        + Solicitar nueva cita
      </button>
      <button v-else class="btn-cancel" @click="showForm = false">
        <AppIcon name="x" :size="14" /> Cancelar
      </button>
    </div>

    <!-- Formulario nueva cita -->
    <div v-if="showForm" class="form-card">
      <h3>Nueva Cita</h3>
      <div class="form-grid">
        <div class="form-group">
          <label>Tipo de visita</label>
          <select v-model="form.appointment_type">
            <option value="viewing">Visita</option>
            <option value="inspection">Inspección</option>
          </select>
        </div>
        <div class="form-group">
          <label>Propiedad</label>
          <select v-model="form.property_id">
            <option value="">-- Seleccionar propiedad --</option>
            <option v-for="p in myProperties" :key="p.id" :value="p.id">
              {{ p.title }} ({{ p.city }})
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>Fecha</label>
          <input type="date" v-model="form.scheduled_date" :min="today" />
        </div>
        <div class="form-group">
          <label>Hora</label>
          <input type="time" v-model="form.scheduled_time" :min="today === form.scheduled_date ? minDateTime.slice(11, 16) : '08:00'" />
        </div>
        <div class="form-group form-group-full">
          <label>Notas (opcional)</label>
          <textarea v-model="form.notes" rows="3" placeholder="Detalles adicionales para el asesor..." maxlength="500"></textarea>
        </div>
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
      <div class="form-actions">
        <button class="btn-save" :disabled="saving" @click="createAppointment">
          <span v-if="saving">Guardando...</span>
          <span v-else>Solicitar cita</span>
        </button>
      </div>
    </div>

    <!-- Estado de carga -->
    <div v-if="loading && !showForm" class="state">
      <div class="spinner"></div>
      <p>Cargando citas...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error && !loading && !showForm" class="state error-msg">{{ error }}</div>

    <!-- Lista de citas -->
    <div v-else-if="!loading" class="content">
      <div v-if="!appointments.length && !showForm" class="empty-state">
        <div class="empty-icon"><AppIcon name="calendar" :size="48" /></div>
        <h3>No tienes citas programadas</h3>
        <p>Solicita una cita para visitar tus propiedades o propiedades de tu interés.</p>
      </div>

      <div v-else class="appointments-list">
        <article v-for="appt in appointments" :key="appt.id" :class="['appointment-card', { pending: appt.status === 'pending' }]">
          <div class="appointment-header">
            <div class="appointment-type">
              <span :class="['type-badge', appt.appointment_type]"><AppIcon :name="appt.appointment_type === 'viewing' ? 'eye' : 'search'" :size="12" /> {{ appt.appointment_type === 'viewing' ? 'Visita' : 'Inspección' }}</span>
            </div>
            <div class="appointment-status">
              <span :class="['badge', statusMap[appt.status]?.cls]">{{ statusMap[appt.status]?.label }}</span>
            </div>
          </div>
          <div class="appointment-body">
            <div class="appointment-info">
              <h4>{{ appt.property?.title || 'Propiedad' }}</h4>
              <p class="detail">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                {{ appt.property?.city || 'Sin ciudad' }}
              </p>
              <p class="detail">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                {{ formattedDateTime(appt.scheduled_date) }}
              </p>
            </div>
            <div v-if="appt.notes" class="appointment-notes">{{ appt.notes }}</div>
          </div>
          <div v-if="appt.status === 'pending'" class="appointment-actions">
            <button class="btn-cancel" @click="cancelAppointment(appt.id)">Cancelar</button>
          </div>
        </article>
      </div>
    </div>

    <Toast :visible="toastState.show" :message="toastState.message" :type="toastState.type" @close="toastState.show = false" />
  </section>
</template>

<style scoped>
.appointments-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-add {
  padding: 10px 18px;
  background: var(--color-gold);
  color: var(--color-navy);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: 0.3s ease;
}

.btn-add:hover {
  filter: brightness(1.03);
  box-shadow: 0 10px 18px rgba(7, 23, 45, 0.12);
}

.btn-cancel {
  padding: 10px 18px;
  background: #eee7dc;
  color: #40566e;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: 0.3s ease;
}

.btn-cancel:hover {
  background: #ddd0bb;
}

.form-card {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 10px 26px rgba(7, 23, 45, 0.08);
}

.form-card h3 {
  margin: 0 0 20px;
  color: var(--color-navy);
  font-size: 18px;
  font-weight: 700;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group-full {
  grid-column: 1 / -1;
}

.form-group label {
  color: var(--color-navy);
  font-size: 13px;
  font-weight: 600;
}

.form-group select,
.form-group input,
.form-group textarea {
  padding: 10px 14px;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-navy);
  background: #fff;
  transition: 0.3s ease;
  font-family: inherit;
}

.form-group select:focus,
.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-gold);
  box-shadow: 0 0 0 3px rgba(214, 168, 72, 0.12);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  gap: 10px;
}

.btn-save {
  padding: 12px 24px;
  background: var(--color-navy);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s ease;
}

.btn-save:hover:not(:disabled) {
  background: #0a1525;
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  padding: 10px 14px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 13px;
  margin-bottom: 12px;
}

.state {
  padding: 24px;
  text-align: center;
  color: var(--color-muted);
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 10px;
}

.error-msg {
  color: #991b1b;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #eadfcf;
  border-top-color: var(--color-gold);
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
}

.empty-icon { color: var(--color-gold); display: block; margin-bottom: 16px; }

.empty-state h3 {
  margin: 0 0 8px;
  color: var(--color-navy);
  font-size: 18px;
}

.empty-state p {
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
}

.appointments-list {
  display: grid;
  gap: 16px;
}

.appointment-card {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
  box-shadow: 0 10px 24px rgba(7, 23, 45, 0.08);
  transition: 0.3s ease;
}

.appointment-card:hover {
  border-color: var(--color-gold);
  box-shadow: 0 14px 32px rgba(7, 23, 45, 0.12);
}

.appointment-card.pending {
  border-left: 3px solid var(--color-gold);
}

.appointment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 12px;
}

.appointment-type span {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-navy);
}

.type-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.type-badge.viewing {
  background: #f7efe0;
  color: #8b7230;
}

.type-badge.inspection {
  background: #ede9fe;
  color: #7c3aed;
}

.badge {
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.badge.pendiente { background: #fff3ce; color: #856404; }
.badge.confirmada { background: #dff7e9; color: #166534; }
.badge.completada { background: #dbeafe; color: #1e40af; }
.badge.cancelada { background: #fee2e2; color: #991b1b; }

.appointment-body {
  padding: 0 20px 16px;
}

.appointment-info h4 {
  margin: 0 0 6px;
  color: var(--color-navy);
  font-size: 15px;
  font-weight: 700;
}

.detail {
  margin: 0 0 4px;
  color: var(--color-muted);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.appointment-notes {
  padding-top: 10px;
  font-size: 13px;
  color: var(--color-muted);
  border-top: 1px solid var(--color-line);
}

.appointment-actions {
  padding: 0 20px 16px;
  display: flex;
  justify-content: flex-end;
}

.appointment-actions .btn-cancel {
  background: var(--color-navy);
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: 0.3s ease;
}

.appointment-actions .btn-cancel:hover {
  background: #0a1525;
}

@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { appointmentsApi } from '@/api/appointments'
import AdvisorDashboardHeader from '@/components/advisor/dashboard/AdvisorDashboardHeader.vue'
import Toast from '@/components/shared/Toast.vue'

const auth = useAuthStore()

const appointments = ref([])
const loading = ref(true)
const error = ref('')
const toastState = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null
const processingId = ref(null)

const showToast = (message, type = 'success') => {
  clearTimeout(toastTimeout)
  toastState.value = { show: true, message, type }
  toastTimeout = setTimeout(() => { toastState.value.show = false }, 3000)
}

const statusMap = {
  pending: { label: 'Pendiente', cls: 'pendiente' },
  confirmed: { label: 'Confirmada', cls: 'confirmada' },
  completed: { label: 'Completada', cls: 'completada' },
  cancelled: { label: 'Cancelada', cls: 'cancelada' }
}

const fetchAppointments = async () => {
  try {
    const { data } = await appointmentsApi.getByAdvisor()
    appointments.value = data.items || data
  } catch (err) {
    error.value = err.response?.data?.detail || err.message
  } finally {
    loading.value = false
  }
}

const updateStatus = async (id, status) => {
  processingId.value = id
  try {
    const { data } = await appointmentsApi.updateStatus(id, status)
    const idx = appointments.value.findIndex(a => a.id === id)
    if (idx !== -1) appointments.value[idx] = data
    showToast(`Cita ${status === 'confirmed' ? 'confirmada' : status === 'cancelled' ? 'cancelada' : 'completada'}`, 'success')
  } catch (err) {
    showToast(err.response?.data?.detail || err.message, 'error')
  } finally {
    processingId.value = null
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' })
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const [h, m] = timeStr.split(':')
  return `${h}:${m}`
}

const pendingCount = computed(() => appointments.value.filter(a => a.status === 'pending').length)
const confirmedCount = computed(() => appointments.value.filter(a => a.status === 'confirmed').length)

onMounted(() => {
  fetchAppointments()
})
</script>

<template>
  <div class="appointments-page">
    <AdvisorDashboardHeader title="Citas" subtitle="Gestiona las citas con tus clientes" />

    <div class="metrics-row">
      <div class="metric-card">
        <span class="metric-value">{{ appointments.length }}</span>
        <span class="metric-label">Total</span>
      </div>
      <div class="metric-card">
        <span class="metric-value pending">{{ pendingCount }}</span>
        <span class="metric-label">Pendientes</span>
      </div>
      <div class="metric-card">
        <span class="metric-value confirmed">{{ confirmedCount }}</span>
        <span class="metric-label">Confirmadas</span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando citas...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="appointments.length === 0" class="empty-state">
      <div class="empty-icon">📅</div>
      <h3>No hay citas</h3>
      <p>Las citas de tus clientes aparecerán aquí</p>
    </div>

    <div v-else class="appointments-list">
      <div v-for="apt in appointments" :key="apt.id" class="appointment-card">
        <div class="apt-header">
          <div class="apt-property">
            <span class="apt-type">{{ apt.appointment_type === 'viewing' ? 'Visita' : 'Consulta' }}</span>
            <h4>{{ apt.property?.title || 'Propiedad' }}</h4>
          </div>
          <span :class="['apt-status', statusMap[apt.status]?.cls]">
            {{ statusMap[apt.status]?.label }}
          </span>
        </div>

        <div class="apt-details">
          <div class="apt-datetime">
            <span class="detail-label">Fecha</span>
            <span class="detail-value">{{ formatDate(apt.scheduled_date) }}</span>
          </div>
          <div class="apt-datetime">
            <span class="detail-label">Hora</span>
            <span class="detail-value">{{ formatTime(apt.scheduled_time) }}</span>
          </div>
          <div class="apt-client">
            <span class="detail-label">Cliente</span>
            <span class="detail-value">{{ apt.client?.name || 'Cliente' }}</span>
          </div>
        </div>

        <p v-if="apt.notes" class="apt-notes">{{ apt.notes }}</p>

        <div v-if="apt.status === 'pending'" class="apt-actions">
          <button 
            @click="updateStatus(apt.id, 'confirmed')" 
            :disabled="processingId === apt.id"
            class="btn-confirm"
          >
            ✓ Confirmar
          </button>
          <button 
            @click="updateStatus(apt.id, 'cancelled')" 
            :disabled="processingId === apt.id"
            class="btn-cancel"
          >
            ✕ Cancelar
          </button>
        </div>

        <div v-else-if="apt.status === 'confirmed'" class="apt-actions">
          <button 
            @click="updateStatus(apt.id, 'completed')" 
            :disabled="processingId === apt.id"
            class="btn-complete"
          >
            ✓ Completar
          </button>
        </div>
      </div>
    </div>

    <Toast :show="toastState.show" :message="toastState.message" :type="toastState.type" />
  </div>
</template>

<style scoped>
.appointments-page { padding: 32px; max-width: 1000px; margin: 0 auto; }
.metrics-row { display: flex; gap: 16px; margin-bottom: 28px; }
.metric-card { flex: 1; background: var(--color-card); border: 1px solid var(--color-line); border-radius: 12px; padding: 20px; text-align: center; }
.metric-value { display: block; font-size: 28px; font-weight: 800; color: var(--color-navy); }
.metric-value.pending { color: #f59e0b; }
.metric-value.confirmed { color: #10b981; }
.metric-label { font-size: 13px; color: var(--color-muted); }

.loading-state, .error-state, .empty-state { text-align: center; padding: 60px 20px; color: var(--color-muted); }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.spinner { width: 40px; height: 40px; border: 3px solid var(--color-line); border-top-color: var(--color-gold); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }

.appointments-list { display: flex; flex-direction: column; gap: 16px; }
.appointment-card { background: var(--color-card); border: 1px solid var(--color-line); border-radius: 12px; padding: 20px; }
.apt-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.apt-property h4 { margin: 4px 0 0; font-size: 16px; color: var(--color-navy); }
.apt-type { font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--color-gold); letter-spacing: .5px; }
.apt-status { font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 6px; }
.apt-status.pendiente { background: #fef3c7; color: #d97706; }
.apt-status.confirmada { background: #d1fae5; color: #059669; }
.apt-status.completada { background: #dbeafe; color: #2563eb; }
.apt-status.cancelada { background: #fee2e2; color: #dc2626; }

.apt-details { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px; }
.detail-label { display: block; font-size: 11px; color: var(--color-muted); text-transform: uppercase; }
.detail-value { font-size: 14px; font-weight: 600; color: var(--color-navy); }
.apt-notes { font-size: 13px; color: var(--color-muted); padding: 12px; background: #f8f9fa; border-radius: 8px; margin-bottom: 12px; }

.apt-actions { display: flex; gap: 10px; padding-top: 12px; border-top: 1px solid var(--color-line); }
.apt-actions button { padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: .2s; border: none; }
.btn-confirm { background: #10b981; color: white; }
.btn-confirm:hover:not(:disabled) { background: #059669; }
.btn-cancel { background: #fee2e2; color: #dc2626; }
.btn-cancel:hover:not(:disabled) { background: #fecaca; }
.btn-complete { background: #2563eb; color: white; }
.btn-complete:hover:not(:disabled) { background: #1d4ed8; }
.apt-actions button:disabled { opacity: 0.6; cursor: not-allowed; }

@media (max-width: 600px) {
  .apt-details { grid-template-columns: 1fr; }
  .metrics-row { flex-direction: column; }
}
</style>
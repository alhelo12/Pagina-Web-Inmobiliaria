<script setup>
import { ref, computed, onMounted } from 'vue'
import { appointmentsApi } from '@/api/appointments'
import AdvisorDashboardHeader from '@/components/advisor/dashboard/AdvisorDashboardHeader.vue'
import Toast from '@/components/shared/Toast.vue'
import AppIcon from '@/components/shared/AppIcon.vue'

const appointments = ref([])
const loading = ref(true)
const error = ref('')
const toastState = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null
const processingId = ref(null)

const showToast = (message, type = 'success') => {
  clearTimeout(toastTimeout)
  toastState.value = { show: true, message, type }
  toastTimeout = setTimeout(() => { toastState.value.show = false }, 4000)
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
    appointments.value = data.appointments || data.items || data
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

const formattedDateTime = (dateTime) => {
  if (!dateTime) return 'Sin fecha'
  const date = new Date(dateTime)
  return date.toLocaleDateString('es-MX', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

const pendingCount = computed(() => appointments.value.filter(a => a.status === 'pending').length)
const confirmedCount = computed(() => appointments.value.filter(a => a.status === 'confirmed').length)

onMounted(() => {
  fetchAppointments()
})
</script>

<template>
  <section class="appointments-page">
    <AdvisorDashboardHeader eyebrow="Panel del Asesor" title="Mis Citas" />
    <Breadcrumb :crumbs="[{ label: 'Citas', path: '/advisor/citas' }]" />

    <section class="metrics">
      <article class="card">
        <div class="card-icon total-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <span>Total</span>
        <strong>{{ appointments.length }}</strong>
        <small>Citas registradas</small>
      </article>
      <article class="card">
        <div class="card-icon pending-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <span>Pendientes</span>
        <strong>{{ pendingCount }}</strong>
        <small>Por confirmar</small>
      </article>
      <article class="card">
        <div class="card-icon confirmed-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <span>Confirmadas</span>
        <strong>{{ confirmedCount }}</strong>
        <small>Agendadas</small>
      </article>
    </section>

    <div v-if="loading" class="state">
      <div class="spinner"></div>
      <p>Cargando citas...</p>
    </div>

    <div v-else-if="error" class="state error-msg">{{ error }}</div>

    <div v-else-if="!appointments.length" class="empty-state">
      <div class="empty-icon"><AppIcon name="calendar" :size="48" /></div>
      <h3>No hay citas</h3>
      <p>Las citas de tus clientes aparecerán aquí</p>
    </div>

    <div v-else class="appointments-list">
      <article v-for="apt in appointments" :key="apt.id" class="appointment-card">
        <div class="appointment-header">
          <div class="appointment-type">
            <span :class="['type-badge', apt.appointment_type]"><AppIcon :name="apt.appointment_type === 'viewing' ? 'eye' : 'search'" :size="12" /> {{ apt.appointment_type === 'viewing' ? 'Visita' : 'Inspección' }}</span>
          </div>
          <span :class="['badge', statusMap[apt.status]?.cls]">{{ statusMap[apt.status]?.label }}</span>
        </div>

        <div class="appointment-body">
          <div class="appointment-info">
            <h4>{{ apt.property?.title || 'Propiedad' }}</h4>
            <p class="detail">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              {{ apt.property?.city || 'Sin ciudad' }}
            </p>
            <p class="detail">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              {{ formattedDateTime(apt.scheduled_date) }}
            </p>
          </div>
          <div v-if="apt.notes" class="appointment-notes">{{ apt.notes }}</div>
        </div>

        <div v-if="apt.status === 'pending'" class="appointment-actions">
          <button @click="updateStatus(apt.id, 'confirmed')" :disabled="processingId === apt.id" class="btn-confirm">
            ✓ Confirmar
          </button>
          <button @click="updateStatus(apt.id, 'cancelled')" :disabled="processingId === apt.id" class="btn-cancel">
            <AppIcon name="x" :size="14" /> Cancelar
          </button>
        </div>

        <div v-else-if="apt.status === 'confirmed'" class="appointment-actions">
          <button @click="updateStatus(apt.id, 'completed')" :disabled="processingId === apt.id" class="btn-complete">
            ✓ Completar
          </button>
        </div>
      </article>
    </div>

    <Toast :visible="toastState.show" :message="toastState.message" :type="toastState.type" />
  </section>
</template>

<style scoped>
.appointments-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.card {
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 10px 24px rgba(7, 23, 45, 0.08);
  transition: 0.3s ease;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 32px rgba(7, 23, 45, 0.12);
}

.card-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.total-icon { background: #e8edf0; color: var(--color-navy-2); }
.pending-icon { background: #fff3ce; color: #856404; }
.confirmed-icon { background: #dff7e9; color: #166534; }

.card span {
  color: var(--color-muted);
  font-size: 13px;
  font-weight: 600;
}

.card strong {
  display: block;
  margin-top: 8px;
  color: var(--color-navy);
  font-size: 30px;
  font-weight: 700;
}

.card small {
  color: #87909b;
  font-size: 12px;
}

.state {
  padding: 60px;
  text-align: center;
  color: var(--color-muted);
  background: var(--color-card);
  border: 1px solid var(--color-line);
  border-radius: 12px;
}

.error-msg { color: #991b1b; }

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-line);
  border-top-color: var(--color-gold);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin { to { transform: rotate(360deg); } }

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
  display: flex;
  flex-direction: column;
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

.appointment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 12px;
}

.type-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.type-badge.viewing { background: #f7efe0; color: #8b7230; }
.type-badge.inspection { background: #ede9fe; color: #7c3aed; }

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
  gap: 10px;
}

.appointment-actions button {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s ease;
  border: none;
}

.btn-confirm { background: #10b981; color: white; }
.btn-confirm:hover:not(:disabled) { background: #059669; }
.btn-cancel { background: #fee2e2; color: #dc2626; }
.btn-cancel:hover:not(:disabled) { background: #fecaca; }
.btn-complete { background: #2563eb; color: white; }
.btn-complete:hover:not(:disabled) { background: #1d4ed8; }
.appointment-actions button:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 900px) {
  .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 600px) {
  .metrics { grid-template-columns: 1fr; }
  .appointment-actions { flex-direction: column; }
}
</style>
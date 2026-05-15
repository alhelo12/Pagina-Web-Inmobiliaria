<template>
  <div class="advisor-post-sale">
    <div class="view-header">
      <h1>Seguimiento Post-Venta</h1>
      <p>Gestiona los seguimientos de tus clientes</p>
    </div>

    <div v-if="loading" class="loading">
      <p>Cargando...</p>
    </div>

    <div v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-value">{{ stats.total_followups || 0 }}</span>
          <span class="stat-label">Total Seguimientos</span>
        </div>
        <div class="stat-card pending">
          <span class="stat-value">{{ stats.pending || 0 }}</span>
          <span class="stat-label">Pendientes</span>
        </div>
        <div class="stat-card completed">
          <span class="stat-value">{{ stats.completed || 0 }}</span>
          <span class="stat-label">Completados</span>
        </div>
        <div class="stat-card score">
          <span class="stat-value">{{ stats.avg_satisfaction_score?.toFixed(1) || '0.0' }}</span>
          <span class="stat-label">Satisfacción Promedio</span>
        </div>
      </div>

      <div v-if="overdue.length > 0" class="overdue-section">
        <h2>Seguimientos Vencidos</h2>
        <div class="followups-list">
          <div v-for="followup in overdue" :key="followup.id" class="followup-card overdue">
            <div class="followup-header">
              <div>
                <span class="followup-type">{{ getTypeLabel(followup.followup_type) }}</span>
                <p class="client-name">{{ followup.client?.full_name || 'N/A' }}</p>
              </div>
              <div class="actions">
                <button class="btn-complete" @click="openCompleteModal(followup)">Completar</button>
                <button class="btn-skip" @click="openSkipModal(followup)">Omitir</button>
              </div>
            </div>
            <p class="scheduled-date">Programado: {{ formatDate(followup.scheduled_date) }}</p>
          </div>
        </div>
      </div>

      <div class="pending-section">
        <h2>Próximos Seguimientos</h2>

        <div v-if="pendingFollowups.length === 0" class="empty-state">
          <p>No hay seguimientos pendientes</p>
        </div>

        <div v-else class="followups-list">
          <div v-for="followup in pendingFollowups" :key="followup.id" class="followup-card">
            <div class="followup-header">
              <div>
                <span class="followup-type">{{ getTypeLabel(followup.followup_type) }}</span>
                <p class="client-name">{{ followup.client?.full_name || 'N/A' }}</p>
              </div>
              <div class="actions">
                <button class="btn-complete" @click="openCompleteModal(followup)">Completar</button>
                <button class="btn-skip" @click="openSkipModal(followup)">Omitir</button>
              </div>
            </div>
            <p class="scheduled-date">Programado: {{ formatDate(followup.scheduled_date) }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCompleteModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal">
        <h3>Completar Seguimiento</h3>
        <p>{{ selectedFollowup?.client?.full_name }} - {{ getTypeLabel(selectedFollowup?.followup_type) }}</p>

        <div v-if="selectedFollowup?.followup_type === 'satisfaction_survey'" class="rating-section">
          <label>Calificación del cliente:</label>
          <div class="stars">
            <button
              v-for="star in 5"
              :key="star"
              type="button"
              class="star-btn"
              :class="{ active: star <= modalRating }"
              @click="modalRating = star"
            >
              {{ star <= modalRating ? '★' : '☆' }}
            </button>
          </div>
        </div>

        <textarea v-model="modalNotes" placeholder="Notas del seguimiento..." rows="3"></textarea>

        <div class="modal-actions">
          <button class="btn-cancel" @click="closeModals">Cancelar</button>
          <button class="btn-confirm" @click="completeFollowup">Confirmar</button>
        </div>
      </div>
    </div>

    <div v-if="showSkipModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal">
        <h3>Omitir Seguimiento</h3>
        <p>{{ selectedFollowup?.client?.full_name }} - {{ getTypeLabel(selectedFollowup?.followup_type) }}</p>

        <textarea v-model="skipReason" placeholder="Razón para omitir..." rows="3" required></textarea>

        <div class="modal-actions">
          <button class="btn-cancel" @click="closeModals">Cancelar</button>
          <button class="btn-confirm" @click="skipFollowup">Confirmar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { postSaleApi } from '../../api/postSale.js'

const loading = ref(true)
const stats = ref({})
const pendingFollowups = ref([])
const overdue = ref([])

const showCompleteModal = ref(false)
const showSkipModal = ref(false)
const selectedFollowup = ref(null)
const modalNotes = ref('')
const modalRating = ref(0)
const skipReason = ref('')

onMounted(async () => {
  try {
    const [statsRes, pendingRes, overdueRes] = await Promise.all([
      postSaleApi.getStats(),
      postSaleApi.getPending(),
      postSaleApi.getOverdue()
    ])

    stats.value = statsRes.data
    pendingFollowups.value = pendingRes.data || []
    overdue.value = overdueRes.data || []
  } catch (error) {
    console.error('Error cargando datos:', error)
  } finally {
    loading.value = false
  }
})

function openCompleteModal(followup) {
  selectedFollowup.value = followup
  modalNotes.value = ''
  modalRating.value = 0
  showCompleteModal.value = true
}

function openSkipModal(followup) {
  selectedFollowup.value = followup
  skipReason.value = ''
  showSkipModal.value = true
}

function closeModals() {
  showCompleteModal.value = false
  showSkipModal.value = false
  selectedFollowup.value = null
}

async function completeFollowup() {
  try {
    await postSaleApi.complete(selectedFollowup.value.id, {
      notes: modalNotes.value || undefined,
      satisfaction_score: modalRating.value > 0 ? modalRating.value : undefined
    })

    pendingFollowups.value = pendingFollowups.value.filter(f => f.id !== selectedFollowup.value.id)
    overdue.value = overdue.value.filter(f => f.id !== selectedFollowup.value.id)
    stats.value.pending = (stats.value.pending || 1) - 1
    stats.value.completed = (stats.value.completed || 0) + 1

    closeModals()
  } catch (error) {
    console.error('Error completando seguimiento:', error)
    alert('Error al completar el seguimiento')
  }
}

async function skipFollowup() {
  if (!skipReason.value.trim()) {
    alert('Debes proporcionar una razón')
    return
  }

  try {
    await postSaleApi.skip(selectedFollowup.value.id, { reason: skipReason.value })

    pendingFollowups.value = pendingFollowups.value.filter(f => f.id !== selectedFollowup.value.id)
    overdue.value = overdue.value.filter(f => f.id !== selectedFollowup.value.id)
    stats.value.pending = (stats.value.pending || 1) - 1
    stats.value.skipped = (stats.value.skipped || 0) + 1

    closeModals()
  } catch (error) {
    console.error('Error omitiendo seguimiento:', error)
    alert('Error al omitir el seguimiento')
  }
}

function getTypeLabel(type) {
  const labels = {
    satisfaction_survey: 'Encuesta de Satisfacción',
    check_in_call: 'Llamada de Seguimiento',
    referral_request: 'Solicitud de Referido',
    maintenance_reminder: 'Recordatorio de Mantenimiento'
  }
  return labels[type] || type
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.advisor-post-sale {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.view-header {
  margin-bottom: 24px;
}

.view-header h1 {
  margin: 0 0 8px;
  font-size: 1.8rem;
  color: #1e293b;
}

.view-header p {
  margin: 0;
  color: #64748b;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 0.85rem;
  color: #64748b;
}

.stat-card.pending .stat-value { color: #f59e0b; }
.stat-card.completed .stat-value { color: #22c55e; }
.stat-card.score .stat-value { color: #3b82f6; }

.overdue-section, .pending-section {
  margin-bottom: 24px;
}

.overdue-section h2, .pending-section h2 {
  margin: 0 0 16px;
  font-size: 1.3rem;
  color: #1e293b;
}

.empty-state {
  text-align: center;
  padding: 40px;
  background: #f8fafc;
  border-radius: 12px;
  color: #94a3b8;
}

.followups-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.followup-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #e2e8f0;
}

.followup-card.overdue {
  border-left-color: #dc2626;
  background: #fef2f2;
}

.followup-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.followup-type {
  font-weight: 600;
  color: #334155;
}

.client-name {
  margin: 4px 0 0;
  font-size: 0.9rem;
  color: #64748b;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-complete, .btn-skip, .btn-confirm, .btn-cancel {
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  border: none;
  transition: background 0.2s;
}

.btn-complete {
  background: #22c55e;
  color: white;
}

.btn-complete:hover { background: #16a34a; }

.btn-skip {
  background: #f1f5f9;
  color: #64748b;
}

.btn-skip:hover { background: #e2e8f0; }

.scheduled-date {
  margin: 0;
  font-size: 0.85rem;
  color: #94a3b8;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 16px;
  padding: 24px;
  width: 90%;
  max-width: 450px;
}

.modal h3 {
  margin: 0 0 8px;
  color: #1e293b;
}

.modal p {
  margin: 0 0 16px;
  color: #64748b;
  font-size: 0.9rem;
}

.modal textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  font-family: inherit;
  margin-bottom: 16px;
}

.modal textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

.rating-section {
  margin-bottom: 16px;
}

.rating-section label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #334155;
}

.stars {
  display: flex;
  gap: 8px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #cbd5e1;
  transition: color 0.2s;
}

.star-btn.active {
  color: #f59e0b;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-cancel {
  background: #f1f5f9;
  color: #64748b;
}

.btn-confirm {
  background: #3b82f6;
  color: white;
}
</style>

<template>
  <div class="advisor-post-sale">
    <div class="view-header">
      <p class="eyebrow-label">Panel del Asesor</p>
      <h1 class="serif-display">Seguimiento Post-Venta</h1>
      <p class="view-sub">Gestiona los seguimientos de tus clientes</p>
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
        <p class="eyebrow-label">Atención</p>
        <h2 class="serif-display">Seguimientos Vencidos</h2>
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
        <p class="eyebrow-label">Agenda</p>
        <h2 class="serif-display">Próximos Seguimientos</h2>

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
      <div
        ref="completeDialogRef"
        class="modal"
        role="dialog"
        aria-modal="true"
        aria-label="Completar seguimiento"
      >
        <h3>Completar Seguimiento</h3>
        <p>{{ selectedFollowup?.client?.full_name }} - {{ getTypeLabel(selectedFollowup?.followup_type) }}</p>

        <div v-if="selectedFollowup?.followup_type === 'satisfaction_survey'" class="rating-section">
          <label id="rating-label">Calificación del cliente:</label>
          <div class="stars" role="radiogroup" aria-labelledby="rating-label">
            <button
              v-for="star in 5"
              :key="star"
              type="button"
              role="radio"
              :aria-checked="star === modalRating"
              :tabindex="star === (modalRating || 1) ? 0 : -1"
              :aria-label="`${star} de 5`"
              class="star-btn"
              :class="{ active: star <= modalRating }"
              @click="modalRating = star"
              @keydown.left.prevent="modalRating = Math.max(1, (modalRating || 1) - 1)"
              @keydown.right.prevent="modalRating = Math.min(5, (modalRating || 0) + 1)"
            >
              {{ star <= modalRating ? '★' : '☆' }}
            </button>
          </div>
        </div>

        <textarea v-model="modalNotes" placeholder="Notas del seguimiento..." aria-label="Notas del seguimiento" rows="3"></textarea>

        <div class="modal-actions">
          <button class="btn-cancel" @click="closeModals">Cancelar</button>
          <button class="btn-confirm" @click="completeFollowup">Confirmar</button>
        </div>
      </div>
    </div>

    <div v-if="showSkipModal" class="modal-overlay" @click.self="closeModals">
      <div
        ref="skipDialogRef"
        class="modal"
        role="dialog"
        aria-modal="true"
        aria-label="Omitir seguimiento"
      >
        <h3>Omitir Seguimiento</h3>
        <p>{{ selectedFollowup?.client?.full_name }} - {{ getTypeLabel(selectedFollowup?.followup_type) }}</p>

        <textarea v-model="skipReason" placeholder="Razón para omitir..." aria-label="Razón para omitir" rows="3" required></textarea>

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
import { useDialog } from '@/composables/useDialog'

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

const { dialogRef: completeDialogRef } = useDialog(showCompleteModal, closeModals)
const { dialogRef: skipDialogRef } = useDialog(showSkipModal, closeModals)

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
    console.error('Error cargando datos:', error?.response?.status ?? error?.message)
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
    console.error('Error completando seguimiento:', error?.response?.status ?? error?.message)
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
    console.error('Error omitiendo seguimiento:', error?.response?.status ?? error?.message)
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
  background: var(--color-ivory);
}

.view-header {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-line);
}

.view-header h1 {
  margin: 0 0 8px;
  font-size: clamp(28px, 4vw, 40px);
  font-weight: 500;
  color: var(--color-petrol);
}

.view-sub {
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--color-muted);
  background: #fff;
  border: 1px solid var(--color-line);
  border-radius: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: none;
}

.stat-card.score {
  background: var(--color-ivory-2);
}

.stat-value {
  display: block;
  font-family: var(--serif);
  font-size: 34px;
  font-weight: 500;
  line-height: 1;
  color: var(--color-petrol);
}

.stat-label {
  display: block;
  margin-top: 8px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.stat-card.pending .stat-value { color: var(--color-brass-ink); }
.stat-card.completed .stat-value { color: var(--color-success); }
.stat-card.score .stat-value { color: var(--color-petrol); }

.overdue-section, .pending-section {
  margin-bottom: 24px;
}

.overdue-section h2, .pending-section h2 {
  margin: 0 0 16px;
  font-size: 26px;
  font-weight: 500;
  color: var(--color-petrol);
}

.empty-state {
  text-align: center;
  padding: 40px;
  background: #fff;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  color: var(--color-muted);
}

.followups-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.followup-card {
  background: #fff;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  padding: 16px;
  box-shadow: none;
}

.followup-card.overdue {
  border-color: var(--color-danger);
  background: var(--color-danger-soft);
}

.followup-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.followup-type {
  font-weight: 600;
  font-size: 11px;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--color-petrol);
}

.client-name {
  margin: 4px 0 0;
  font-family: var(--serif);
  font-size: 18px;
  color: var(--color-petrol);
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-complete, .btn-skip, .btn-confirm, .btn-cancel {
  min-height: 44px;
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
  border: 1px solid transparent;
  transition: background 0.2s ease;
}

.btn-complete {
  background: var(--color-petrol);
  color: #fff;
  border-color: var(--color-petrol);
}

.btn-complete:hover { background: var(--color-ink); }

.btn-skip {
  background: transparent;
  border-color: var(--color-line);
  color: var(--color-petrol);
}

.btn-skip:hover { border-color: var(--color-brass); }

.scheduled-date {
  margin: 8px 0 0;
  padding-top: 10px;
  border-top: 1px solid var(--color-line);
  font-size: 0.85rem;
  color: var(--color-muted);
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
  z-index: var(--z-modal);
}

.modal {
  background: #fff;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 450px;
}

.modal h3 {
  margin: 0 0 8px;
  font-family: var(--serif);
  font-weight: 500;
  font-size: 24px;
  color: var(--color-petrol);
}

.modal p {
  margin: 0 0 16px;
  color: var(--color-muted);
  font-size: 0.9rem;
}

.modal textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  font-family: inherit;
  margin-bottom: 16px;
  background: #fff;
  color: var(--color-petrol);
}

.modal textarea:focus {
  outline: none;
  border-color: var(--color-petrol);
}

.rating-section {
  margin-bottom: 16px;
}

.rating-section label {
  display: block;
  font-weight: 600;
  font-size: 11px;
  letter-spacing: .14em;
  text-transform: uppercase;
  margin-bottom: 8px;
  color: var(--color-petrol);
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
  color: var(--color-line);
  transition: color 0.2s;
}

.star-btn.active {
  color: var(--color-brass);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-cancel {
  background: transparent;
  border-color: var(--color-line);
  color: var(--color-petrol);
}

.btn-confirm {
  background: var(--color-petrol);
  border-color: var(--color-petrol);
  color: #fff;
}

@media (max-width: 768px) {
  .advisor-post-sale { padding: 16px; }
  .followup-header { flex-direction: column; align-items: flex-start; gap: 10px; }
  .actions { width: 100%; }
  .actions button { flex: 1; }
}
</style>

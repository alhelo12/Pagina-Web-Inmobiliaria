<template>
  <div class="post-sale-view">
    <div class="view-header">
      <p class="eyebrow-label">Panel de Cliente</p>
      <h1 class="serif-display">Seguimiento Post-Venta</h1>
      <p class="view-sub">Encuestas y seguimiento después de tu compra/renta</p>
    </div>

    <div v-if="loading" class="loading">
      <p>Cargando...</p>
    </div>

    <div v-else>
      <div v-if="pendingSurvey" class="survey-alert">
        <p class="eyebrow-label">Acción requerida</p>
        <h2 class="serif-display">Tienes una encuesta pendiente</h2>
        <SatisfactionSurvey
          :followup="pendingSurvey"
          @completed="onSurveyCompleted"
          @skip="onSurveySkipped"
        />
      </div>

      <div class="followups-section">
        <p class="eyebrow-label">Historial</p>
        <h2 class="serif-display">Historial de Seguimientos</h2>

        <div v-if="followups.length === 0" class="empty-state">
          <p>No hay seguimientos registrados</p>
        </div>

        <div v-else class="followups-list">
          <div
            v-for="followup in followups"
            :key="followup.id"
            class="followup-card"
            :class="followup.status"
          >
            <div class="followup-header">
              <span class="followup-type">{{ getTypeLabel(followup.followup_type) }}</span>
              <span class="followup-status" :class="followup.status">
                {{ getStatusLabel(followup.status) }}
              </span>
            </div>

            <div class="followup-details">
              <p><strong>Propiedad:</strong> {{ followup.property?.title || 'N/A' }}</p>
              <p><strong>Programado:</strong> {{ formatDate(followup.scheduled_date) }}</p>
              <p v-if="followup.completed_date">
                <strong>Completado:</strong> {{ formatDate(followup.completed_date) }}
              </p>
              <p v-if="followup.satisfaction_score">
                <strong>Calificación:</strong> {{ '★'.repeat(followup.satisfaction_score) }}{{ '☆'.repeat(5 - followup.satisfaction_score) }}
              </p>
              <p v-if="followup.notes"><strong>Notas:</strong> {{ followup.notes }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { postSaleApi } from '../../api/postSale.js'
import SatisfactionSurvey from '../../components/shared/SatisfactionSurvey.vue'

const loading = ref(true)
const followups = ref([])
const pendingSurvey = ref(null)

onMounted(async () => {
  try {
    const response = await postSaleApi.getList({ page: 1, per_page: 50 })
    followups.value = response.data.followups || []

    pendingSurvey.value = followups.value.find(
      f => f.followup_type === 'satisfaction_survey' && f.status === 'pending'
    ) || null
  } catch (error) {
    console.error('Error cargando seguimientos:', error)
  } finally {
    loading.value = false
  }
})

function onSurveyCompleted(followupId) {
  const followup = followups.value.find(f => f.id === followupId)
  if (followup) {
    followup.status = 'completed'
    followup.completed_date = new Date().toISOString()
  }
  pendingSurvey.value = null
}

function onSurveySkipped(followupId) {
  const followup = followups.value.find(f => f.id === followupId)
  if (followup) {
    followup.status = 'skipped'
  }
  pendingSurvey.value = null
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

function getStatusLabel(status) {
  const labels = {
    pending: 'Pendiente',
    completed: 'Completado',
    skipped: 'Omitido'
  }
  return labels[status] || status
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.post-sale-view {
  padding: 24px;
  max-width: 900px;
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

.survey-alert {
  background: #faf5e9;
  border: 1px solid var(--color-brass);
  border-left: 3px solid var(--color-brass);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.survey-alert h2 {
  margin: 0 0 16px;
  font-size: 24px;
  font-weight: 500;
  color: var(--color-petrol);
}

.followups-section h2 {
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
  border-left: 3px solid var(--color-line);
  border-radius: 12px;
  padding: 16px;
  box-shadow: none;
}

.followup-card.completed {
  border-left-color: #166534;
}

.followup-card.pending {
  border-left-color: var(--color-brass);
}

.followup-card.skipped {
  border-left-color: var(--color-muted);
}

.followup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.followup-type {
  font-weight: 600;
  font-size: 11px;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--color-petrol);
}

.followup-status {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.followup-status.pending {
  background: #f4e8cd;
  color: #7a5c1e;
}

.followup-status.completed {
  background: #e2f0e5;
  color: #166534;
}

.followup-status.skipped {
  background: transparent;
  border: 1px solid var(--color-line);
  color: var(--color-muted);
}

.followup-details p {
  margin: 4px 0;
  font-size: 0.9rem;
  color: var(--color-muted);
}

.followup-details strong {
  color: var(--color-petrol);
}

@media (max-width: 768px) {
  .post-sale-view { padding: 16px; }
  .followup-header { flex-direction: column; align-items: flex-start; gap: 8px; }
}
</style>

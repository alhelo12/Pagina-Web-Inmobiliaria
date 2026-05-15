<template>
  <div class="post-sale-view">
    <div class="view-header">
      <h1>Seguimiento Post-Venta</h1>
      <p>Encuestas y seguimiento después de tu compra/renta</p>
    </div>

    <div v-if="loading" class="loading">
      <p>Cargando...</p>
    </div>

    <div v-else>
      <div v-if="pendingSurvey" class="survey-alert">
        <h2>Tienes una encuesta pendiente</h2>
        <SatisfactionSurvey
          :followup="pendingSurvey"
          @completed="onSurveyCompleted"
          @skip="onSurveySkipped"
        />
      </div>

      <div class="followups-section">
        <h2>Historial de Seguimientos</h2>

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

.survey-alert {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.survey-alert h2 {
  margin: 0 0 16px;
  font-size: 1.2rem;
  color: #92400e;
}

.followups-section h2 {
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

.followup-card.completed {
  border-left-color: #22c55e;
}

.followup-card.pending {
  border-left-color: #f59e0b;
}

.followup-card.skipped {
  border-left-color: #94a3b8;
}

.followup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.followup-type {
  font-weight: 600;
  color: #334155;
}

.followup-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.followup-status.pending {
  background: #fef3c7;
  color: #92400e;
}

.followup-status.completed {
  background: #dcfce7;
  color: #166534;
}

.followup-status.skipped {
  background: #f1f5f9;
  color: #64748b;
}

.followup-details p {
  margin: 4px 0;
  font-size: 0.9rem;
  color: #475569;
}

.followup-details strong {
  color: #1e293b;
}
</style>

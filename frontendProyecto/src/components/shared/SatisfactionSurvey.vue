<template>
  <div class="survey-container">
    <div class="survey-header">
      <h3>Encuesta de Satisfacción</h3>
      <p class="survey-subtitle">Tu opinión nos ayuda a mejorar nuestro servicio</p>
    </div>

    <div v-if="followup" class="survey-content">
      <div class="property-info">
        <span class="property-label">Propiedad:</span>
        <span class="property-name">{{ followup.property?.title || 'N/A' }}</span>
      </div>

      <div class="rating-section">
        <label>¿Cómo calificarías tu experiencia?</label>
        <div class="stars">
          <button
            v-for="star in 5"
            :key="star"
            type="button"
            class="star-btn"
            :class="{ active: star <= rating }"
            @click="rating = star"
          >
            {{ star <= rating ? '★' : '☆' }}
          </button>
        </div>
        <span class="rating-text">{{ ratingText }}</span>
      </div>

      <div class="notes-section">
        <label for="notes">Comentarios adicionales (opcional)</label>
        <textarea
          id="notes"
          v-model="notes"
          placeholder="Cuéntanos sobre tu experiencia..."
          rows="4"
        ></textarea>
      </div>

      <div class="survey-actions">
        <button class="btn-skip" @click="$emit('skip', followup.id)">Omitir</button>
        <button
          class="btn-submit"
          :disabled="rating === 0 || submitting"
          @click="submitSurvey"
        >
          {{ submitting ? 'Enviando...' : 'Enviar Encuesta' }}
        </button>
      </div>
    </div>

    <div v-else class="no-survey">
      <p>No hay encuesta disponible</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { postSaleApi } from '../../api/postSale.js'

const props = defineProps({
  followup: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['completed', 'skip'])

const rating = ref(0)
const notes = ref('')
const submitting = ref(false)

const ratingText = computed(() => {
  const texts = ['', 'Muy mala', 'Mala', 'Regular', 'Buena', 'Excelente']
  return texts[rating.value] || ''
})

async function submitSurvey() {
  if (rating.value === 0) return

  submitting.value = true
  try {
    await postSaleApi.complete(props.followup.id, {
      satisfaction_score: rating.value,
      notes: notes.value || undefined
    })
    emit('completed', props.followup.id)
  } catch (error) {
    console.error('Error al enviar encuesta:', error)
    alert('Error al enviar la encuesta. Intenta nuevamente.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.survey-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.survey-header {
  margin-bottom: 20px;
  text-align: center;
}

.survey-header h3 {
  margin: 0 0 8px;
  font-size: 1.5rem;
  color: #1e293b;
}

.survey-subtitle {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}

.property-info {
  background: #f1f5f9;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.property-label {
  font-weight: 600;
  color: #475569;
  margin-right: 8px;
}

.property-name {
  color: #1e293b;
}

.rating-section {
  text-align: center;
  margin-bottom: 20px;
}

.rating-section label {
  display: block;
  font-weight: 600;
  margin-bottom: 12px;
  color: #334155;
}

.stars {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 8px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 2.5rem;
  cursor: pointer;
  color: #cbd5e1;
  transition: color 0.2s, transform 0.2s;
}

.star-btn:hover {
  transform: scale(1.1);
}

.star-btn.active {
  color: #f59e0b;
}

.rating-text {
  font-size: 0.9rem;
  color: #64748b;
}

.notes-section {
  margin-bottom: 20px;
}

.notes-section label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #334155;
}

.notes-section textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  font-family: inherit;
}

.notes-section textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.survey-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-skip {
  padding: 10px 20px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #64748b;
  transition: background 0.2s;
}

.btn-skip:hover {
  background: #e2e8f0;
}

.btn-submit {
  padding: 10px 24px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-submit:hover:not(:disabled) {
  background: #2563eb;
}

.btn-submit:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.no-survey {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
}
</style>

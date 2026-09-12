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
        <label id="rating-label">¿Cómo calificarías tu experiencia?</label>
        <div class="stars" role="radiogroup" aria-labelledby="rating-label">
          <button
            v-for="star in 5"
            :key="star"
            type="button"
            class="star-btn"
            role="radio"
            :aria-checked="star === rating"
            :aria-label="`${star} de 5`"
            :class="{ active: star <= rating }"
            @click="rating = star"
            @keydown.left.prevent="rating = star > 1 ? star - 1 : 5"
            @keydown.right.prevent="rating = star < 5 ? star + 1 : 1"
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
  background: var(--color-card);
  border: 1px solid var(--color-line);
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
  color: var(--color-ink);
}

.survey-subtitle {
  margin: 0;
  color: var(--color-muted);
  font-size: 0.9rem;
}

.property-info {
  background: var(--color-ivory);
  border: 1px solid var(--color-line);
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.property-label {
  font-weight: 600;
  color: var(--color-muted);
  margin-right: 8px;
}

.property-name {
  color: var(--color-ink);
}

.rating-section {
  text-align: center;
  margin-bottom: 20px;
}

.rating-section label {
  display: block;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--color-petrol);
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
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-line);
  transition: color 0.2s, transform 0.2s;
}

.star-btn:hover {
  transform: scale(1.1);
}

.star-btn.active {
  color: var(--color-brass);
}

.rating-text {
  font-size: 0.9rem;
  color: var(--color-muted);
}

.notes-section {
  margin-bottom: 20px;
}

.notes-section label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--color-petrol);
}

.notes-section textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  font-family: inherit;
  background: var(--color-card);
}

.notes-section textarea:focus {
  outline: none;
  border-color: var(--color-petrol);
  box-shadow: 0 0 0 3px rgba(16, 45, 45, 0.12);
}

.survey-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-skip {
  min-height: 44px;
  padding: 10px 20px;
  background: var(--color-ivory);
  border: 1px solid var(--color-line);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--color-muted);
  transition: background 0.2s;
}

.btn-skip:hover {
  background: var(--color-line);
}

.btn-submit {
  min-height: 44px;
  padding: 10px 24px;
  background: var(--color-petrol);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-submit:hover:not(:disabled) {
  background: var(--color-ink);
}

.btn-submit:disabled {
  background: var(--color-muted);
  cursor: not-allowed;
}

.no-survey {
  text-align: center;
  padding: 40px;
  color: var(--color-muted);
}
</style>

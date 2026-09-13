<script setup>
import { ref, onMounted } from 'vue'
import { notificationPreferencesApi } from '@/api/notificationPreferences'
import { useAuthStore } from '@/stores/authStore'
import { getNotificationMeta, getTypeFilters } from '@/constants/notifications'
import { useDialog } from '@/composables/useDialog'
import AppIcon from '@/components/shared/AppIcon.vue'

const emit = defineEmits(['close'])
const auth = useAuthStore()
const preferences = ref([])
const loading = ref(true)

const isOpen = ref(true)
const { dialogRef } = useDialog(isOpen, () => emit('close'))

const visibleTypes = getTypeFilters(auth.role).map(t => [t.key, { label: t.label, color: t.color, icon: getNotificationMeta(t.key).icon }])

const getPref = (type) => {
  const p = preferences.value.find(pref => pref.type === type)
  return p ? p.enabled : true
}

const toggle = async (type) => {
  const current = getPref(type)
  try {
    const { data } = await notificationPreferencesApi.update(type, !current)
    const idx = preferences.value.findIndex(p => p.type === type)
    if (idx !== -1) {
      preferences.value[idx] = data
    } else {
      preferences.value.push(data)
    }
  } catch (e) {
    // revert on error
  }
}

onMounted(async () => {
  try {
    const { data } = await notificationPreferencesApi.getAll()
    preferences.value = data.preferences
  } catch (e) {
    // fallback: assume all enabled
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="preferences-overlay" @click.self="$emit('close')">
    <div
      ref="dialogRef"
      class="preferences-panel"
      role="dialog"
      aria-modal="true"
      aria-label="Preferencias de notificación"
    >
      <div class="panel-header">
        <h3>Preferencias de notificación</h3>
        <button class="close-btn" aria-label="Cerrar" @click="$emit('close')">
          <AppIcon name="x" :size="18" />
        </button>
      </div>

      <div v-if="loading" class="loading">Cargando...</div>

      <div v-else class="pref-list">
        <div
          v-for="[type, meta] in visibleTypes"
          :key="type"
          class="pref-item"
        >
          <div class="pref-info">
            <span
              class="pref-icon"
              :style="{ backgroundColor: meta.color + '20', color: meta.color }"
            >
              <AppIcon :name="meta.icon" :size="16" />
            </span>
            <div>
              <strong>{{ meta.label }}</strong>
            </div>
          </div>
          <label class="toggle">
            <input
              type="checkbox"
              :checked="getPref(type)"
              :aria-label="`Notificaciones de ${meta.label}`"
              @change="toggle(type)"
            />
            <span class="slider"></span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.preferences-overlay {
  position: fixed;
  inset: 0;
  background: rgba(7, 27, 28, 0.4);
  backdrop-filter: blur(4px);
  z-index: var(--z-modal);
  display: grid;
  place-items: center;
  padding: 16px;
}

.preferences-panel {
  background: #ffffff;
  border-radius: 12px;
  width: 100%;
  max-width: 420px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 48px rgba(7, 27, 28, 0.24);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-line);
}

.panel-header h3 {
  margin: 0;
  color: var(--color-ink);
  font-size: 16px;
  font-weight: 700;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 7px;
  transition: color 0.2s ease;
  min-width: 44px;
  min-height: 44px;
  display: grid;
  place-items: center;
}

.close-btn:hover {
  color: var(--color-ink);
}

.loading {
  padding: 40px;
  text-align: center;
  color: var(--color-muted);
}

.pref-list {
  overflow-y: auto;
  padding: 8px 0;
}

.pref-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  gap: 12px;
}

.pref-item:hover {
  background: var(--color-ivory-2);
}

.pref-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.pref-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.pref-info strong {
  display: block;
  color: var(--color-ink);
  font-size: 13px;
  font-weight: 600;
}

.pref-info small {
  color: var(--color-muted);
  font-size: 11px;
}

/* Toggle switch */
.toggle {
  position: relative;
  width: 44px;
  height: 24px;
  flex-shrink: 0;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  inset: 0;
  background: var(--color-line);
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.slider::before {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  background: #ffffff;
  border-radius: 50%;
  transition: transform 0.3s ease;
}

.toggle input:checked + .slider {
  background: var(--color-brass);
}

.toggle input:checked + .slider::before {
  transform: translateX(20px);
}

.toggle input:focus-visible + .slider {
  outline: 2px solid var(--color-brass);
  outline-offset: 2px;
}
</style>

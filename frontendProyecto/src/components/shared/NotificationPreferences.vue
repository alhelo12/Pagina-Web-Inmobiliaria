<script setup>
import { ref, onMounted } from 'vue'
import { notificationPreferencesApi } from '@/api/notificationPreferences'
import { useAuthStore } from '@/stores/authStore'
import { NOTIFICATION_META } from '@/constants/notifications'
import AppIcon from '@/components/shared/AppIcon.vue'

const emit = defineEmits(['close'])
const auth = useAuthStore()
const preferences = ref([])
const loading = ref(true)

const visibleTypes = Object.entries(NOTIFICATION_META)
  .filter(([, meta]) => meta.roles.includes(auth.role))

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
    <div class="preferences-panel">
      <div class="panel-header">
        <h3>Preferencias de notificación</h3>
        <button class="close-btn" @click="$emit('close')">
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
              <small>{{ meta.roles.includes('client') && meta.roles.includes('advisor') ? 'Cliente y asesor' : meta.roles.includes('client') ? 'Solo cliente' : 'Solo asesor' }}</small>
            </div>
          </div>
          <label class="toggle">
            <input
              type="checkbox"
              :checked="getPref(type)"
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
  background: rgba(7, 23, 45, 0.4);
  backdrop-filter: blur(4px);
  z-index: 5000;
  display: grid;
  place-items: center;
  padding: 16px;
}

.preferences-panel {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 420px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 48px rgba(7, 23, 45, 0.24);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e7ebf3;
}

.panel-header h3 {
  margin: 0;
  color: #07172d;
  font-size: 16px;
  font-weight: 700;
}

.close-btn {
  background: transparent;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: color 0.2s ease;
}

.close-btn:hover {
  color: #07172d;
}

.loading {
  padding: 40px;
  text-align: center;
  color: #65717e;
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
  background: #f8fafc;
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
  border-radius: 10px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.pref-info strong {
  display: block;
  color: #07172d;
  font-size: 13px;
  font-weight: 600;
}

.pref-info small {
  color: #9ca3af;
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
  background: #d1d5db;
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
  background: #d6a848;
}

.toggle input:checked + .slider::before {
  transform: translateX(20px);
}
</style>

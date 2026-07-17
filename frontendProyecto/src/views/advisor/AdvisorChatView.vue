<script setup>
import ChatView from '@/components/shared/ChatView.vue'

const props = defineProps({
  role: { type: String, default: 'advisor' }
})
</script>

<template>
  <ChatView :role="props.role" eyebrow="Panel del Asesor" title="Mensajes" />
</template>
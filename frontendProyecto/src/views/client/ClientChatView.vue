<script setup>
import ChatView from '@/components/shared/ChatView.vue'

const props = defineProps({
  role: { type: String, default: 'client' }
})
</script>

<template>
  <ChatView :role="props.role" eyebrow="Panel de Cliente" title="Mensajes" />
</template>
<script setup lang="ts">
const props = defineProps<{
  variant?: 'success' | 'warning' | 'error' | 'info'
  dismissible?: boolean
  icon?: string[]
}>()

const emit = defineEmits<{
  dismiss: []
}>()

const visible = ref(true)

const variantConfig = computed(() => {
  const configs: Record<string, { bg: string; border: string; text: string; icon: string[] }> = {
    success: {
      bg: 'bg-[var(--color-success-light)]',
      border: 'border-[var(--color-success)]',
      text: 'text-[var(--color-success-dark)]',
      icon: ['fas', 'check-circle'],
    },
    warning: {
      bg: 'bg-[var(--color-warning-light)]',
      border: 'border-[var(--color-warning)]',
      text: 'text-[var(--color-warning-dark)]',
      icon: ['fas', 'exclamation-triangle'],
    },
    error: {
      bg: 'bg-[var(--color-error-light)]',
      border: 'border-[var(--color-error)]',
      text: 'text-[var(--color-error-dark)]',
      icon: ['fas', 'times-circle'],
    },
    info: {
      bg: 'bg-[var(--color-info-light)]',
      border: 'border-[var(--color-info)]',
      text: 'text-[var(--color-info-dark)]',
      icon: ['fas', 'info-circle'],
    },
  }
  return configs[props.variant ?? 'info']
})

function dismiss() {
  visible.value = false
  emit('dismiss')
}
</script>

<template>
  <div
    v-if="visible"
    class="flex items-start gap-3 p-4 border-l-4 rounded-[var(--radius-md)]"
    :class="[variantConfig.bg, variantConfig.border, variantConfig.text]"
    role="alert"
  >
    <font-awesome-icon
      :icon="icon ?? variantConfig.icon"
      class="mt-0.5 shrink-0"
    />
    <div class="flex-1 text-sm">
      <slot />
    </div>
    <button
      v-if="dismissible"
      class="shrink-0 opacity-70 hover:opacity-100 cursor-pointer"
      @click="dismiss"
    >
      <font-awesome-icon :icon="['fas', 'xmark']" />
    </button>
  </div>
</template>

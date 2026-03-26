<script setup lang="ts">
const props = defineProps<{
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'gray'
  size?: 'sm' | 'md'
  dot?: boolean
}>()

const variantClasses: Record<string, string> = {
  primary: 'bg-(--color-primary-50) text-(--color-primary-700)',
  success: 'bg-(--color-success-light) text-(--color-success-dark)',
  warning: 'bg-(--color-warning-light) text-(--color-warning-dark)',
  error: 'bg-(--color-error-light) text-(--color-error-dark)',
  info: 'bg-(--color-info-light) text-(--color-info-dark)',
  gray: 'bg-(--interactive-hover) text-(--text-secondary)',
}

const dotColors: Record<string, string> = {
  primary: 'bg-(--color-primary)',
  success: 'bg-(--color-success)',
  warning: 'bg-(--color-warning)',
  error: 'bg-(--color-error)',
  info: 'bg-(--color-info)',
  gray: 'bg-(--text-muted)',
}

const sizeClasses: Record<string, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
}
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 font-medium rounded-full"
    :class="[variantClasses[variant ?? 'gray'], sizeClasses[size ?? 'sm']]"
  >
    <span v-if="dot" class="w-1.5 h-1.5 rounded-full" :class="dotColors[variant ?? 'gray']" />
    <slot />
  </span>
</template>

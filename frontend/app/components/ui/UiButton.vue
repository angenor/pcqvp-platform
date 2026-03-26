<script setup lang="ts">
const props = defineProps<{
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  icon?: string[]
  iconPosition?: 'left' | 'right'
  to?: string
  block?: boolean
}>()

defineEmits<{
  click: [e: MouseEvent]
}>()

const variantClasses: Record<string, string> = {
  primary: 'bg-(--color-primary) !text-white hover:bg-(--color-primary-700) hover:!text-white shadow-sm',
  secondary: 'bg-(--interactive-hover) !text-(--text-primary) hover:bg-(--interactive-active) hover:!text-(--text-primary)',
  outline: 'border border-(--border-default) !text-(--text-primary) hover:bg-(--interactive-hover) hover:!text-(--text-primary)',
  ghost: '!text-(--text-secondary) hover:bg-(--interactive-hover) hover:!text-(--text-primary)',
  danger: 'bg-(--color-error) !text-white hover:bg-(--color-error-dark) hover:!text-white shadow-sm',
  success: 'bg-(--color-success) !text-white hover:bg-(--color-success-dark) hover:!text-white shadow-sm',
}

const sizeClasses: Record<string, string> = {
  sm: 'px-2.5 py-1.5 text-xs gap-1.5',
  md: 'px-4 py-2 text-sm gap-2',
  lg: 'px-5 py-2.5 text-base gap-2',
}

const classes = computed(() => [
  'inline-flex items-center justify-center font-medium rounded-md transition-colors cursor-pointer',
  'disabled:opacity-50 disabled:cursor-not-allowed',
  variantClasses[props.variant ?? 'primary'],
  sizeClasses[props.size ?? 'md'],
  props.block ? 'w-full' : '',
])

const component = computed(() => props.to ? resolveComponent('NuxtLink') : 'button')
</script>

<template>
  <component
    :is="component"
    :to="to"
    :disabled="disabled || loading"
    :class="classes"
    @click="!to && $emit('click', $event)"
  >
    <UiLoadingSpinner v-if="loading" size="sm" :color="variant === 'outline' || variant === 'ghost' || variant === 'secondary' ? 'primary' : 'white'" />
    <font-awesome-icon v-if="icon && !loading && (iconPosition ?? 'left') === 'left'" :icon="icon" />
    <slot />
    <font-awesome-icon v-if="icon && !loading && iconPosition === 'right'" :icon="icon" />
  </component>
</template>

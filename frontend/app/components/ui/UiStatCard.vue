<script setup lang="ts">
const props = defineProps<{
  label: string
  value: string | number
  icon?: string[]
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'info'
  trend?: number
  trendLabel?: string
  loading?: boolean
  to?: string
}>()

const iconBgClasses: Record<string, string> = {
  primary: 'bg-(--color-primary-50) text-(--color-primary)',
  success: 'bg-(--color-success-light) text-(--color-success)',
  warning: 'bg-(--color-warning-light) text-(--color-warning)',
  error: 'bg-(--color-error-light) text-(--color-error)',
  info: 'bg-(--color-info-light) text-(--color-info)',
}

const component = computed(() => props.to ? resolveComponent('NuxtLink') : 'div')
</script>

<template>
  <component
    :is="component"
    :to="to"
    class="block p-5 rounded-lg border border-(--border-default) transition-all"
    :class="to ? 'hover:shadow-md cursor-pointer' : ''"
    :style="{ backgroundColor: 'var(--bg-card)' }"
  >
    <!-- Skeleton -->
    <div v-if="loading" class="animate-pulse space-y-3">
      <div class="h-4 w-24 rounded bg-(--interactive-hover)" />
      <div class="h-8 w-16 rounded bg-(--interactive-hover)" />
    </div>

    <!-- Content -->
    <div v-else>
      <div class="flex items-center justify-between mb-3">
        <p class="text-sm font-medium text-(--text-secondary)">{{ label }}</p>
        <div
          v-if="icon"
          class="w-10 h-10 rounded-lg flex items-center justify-center"
          :class="iconBgClasses[variant ?? 'primary']"
        >
          <font-awesome-icon :icon="icon" />
        </div>
      </div>
      <p class="text-2xl font-bold font-mono text-(--text-primary)">{{ value }}</p>
      <div v-if="trend !== undefined" class="flex items-center gap-1 mt-2 text-sm">
        <font-awesome-icon
          :icon="['fas', trend >= 0 ? 'arrow-trend-up' : 'arrow-trend-down']"
          :class="trend >= 0 ? 'text-(--color-success)' : 'text-(--color-error)'"
          class="text-xs"
        />
        <span :class="trend >= 0 ? 'text-(--color-success)' : 'text-(--color-error)'">
          {{ Math.abs(trend) }}%
        </span>
        <span v-if="trendLabel" class="text-(--text-muted)">{{ trendLabel }}</span>
      </div>
    </div>
  </component>
</template>

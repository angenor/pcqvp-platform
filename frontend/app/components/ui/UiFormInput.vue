<script setup lang="ts">
const props = defineProps<{
  modelValue?: string | number
  type?: 'text' | 'email' | 'password' | 'number' | 'date'
  label?: string
  placeholder?: string
  required?: boolean
  error?: string
  disabled?: boolean
  icon?: string[]
}>()

defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const inputId = computed(() => `input-${Math.random().toString(36).slice(2, 9)}`)
</script>

<template>
  <div>
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium mb-1 text-(--text-secondary)"
    >
      {{ label }}
      <span v-if="required" class="text-(--color-error)">*</span>
    </label>
    <div class="relative">
      <div
        v-if="icon"
        class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-(--text-muted)"
      >
        <font-awesome-icon :icon="icon" class="text-sm" />
      </div>
      <input
        :id="inputId"
        :type="type ?? 'text'"
        :value="modelValue"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        class="w-full px-3 py-2 text-sm border rounded-md transition-colors outline-none"
        :class="[
          icon ? 'pl-9' : '',
          error
            ? 'border-(--color-error) focus:ring-2 focus:ring-(--color-error)/20'
            : 'border-(--border-default) focus:ring-2 focus:ring-(--color-primary)/20 focus:border-(--border-focus)',
          disabled ? 'opacity-50 cursor-not-allowed' : '',
        ]"
        :style="{
          backgroundColor: disabled ? 'var(--bg-input-disabled)' : 'var(--bg-input)',
          color: 'var(--text-primary)',
        }"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />
    </div>
    <p v-if="error" class="mt-1 text-xs text-(--color-error)">{{ error }}</p>
  </div>
</template>

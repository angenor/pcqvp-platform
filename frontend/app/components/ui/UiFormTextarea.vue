<script setup lang="ts">
const props = defineProps<{
  modelValue?: string
  label?: string
  rows?: number
  required?: boolean
  error?: string
  disabled?: boolean
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()

const textareaId = computed(() => `textarea-${Math.random().toString(36).slice(2, 9)}`)
</script>

<template>
  <div>
    <label
      v-if="label"
      :for="textareaId"
      class="block text-sm font-medium mb-1 text-(--text-secondary)"
    >
      {{ label }}
      <span v-if="required" class="text-(--color-error)">*</span>
    </label>
    <textarea
      :id="textareaId"
      :value="modelValue"
      :rows="rows ?? 4"
      :required="required"
      :disabled="disabled"
      class="w-full px-3 py-2 text-sm border rounded-md transition-colors outline-none resize-y"
      :class="[
        error
          ? 'border-(--color-error) focus:ring-2 focus:ring-(--color-error)/20'
          : 'border-(--border-default) focus:ring-2 focus:ring-(--color-primary)/20 focus:border-(--border-focus)',
        disabled ? 'opacity-50 cursor-not-allowed' : '',
      ]"
      :style="{
        backgroundColor: disabled ? 'var(--bg-input-disabled)' : 'var(--bg-input)',
        color: 'var(--text-primary)',
      }"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />
    <p v-if="error" class="mt-1 text-xs text-(--color-error)">{{ error }}</p>
  </div>
</template>

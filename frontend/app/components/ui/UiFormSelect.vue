<script setup lang="ts">
const props = defineProps<{
  modelValue?: string | number
  options: { value: string | number; label: string }[]
  label?: string
  icon?: string
  placeholder?: string
  required?: boolean
  error?: string
  disabled?: boolean
}>()

defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const selectId = computed(() => `select-${Math.random().toString(36).slice(2, 9)}`)
</script>

<template>
  <div>
    <label
      v-if="label"
      :for="selectId"
      class="block text-sm font-medium mb-1 text-(--text-secondary)"
    >
      <font-awesome-icon v-if="icon" :icon="icon" class="mr-1.5 text-(--color-primary)" />
      {{ label }}
      <span v-if="required" class="text-(--color-error)">*</span>
    </label>
    <select
      :id="selectId"
      :value="modelValue"
      :required="required"
      :disabled="disabled"
      class="w-full px-3 py-2 text-sm border rounded-md transition-colors outline-none appearance-none cursor-pointer"
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
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    >
      <option v-if="placeholder" value="" disabled :selected="!modelValue">
        {{ placeholder }}
      </option>
      <option v-for="opt in options" :key="opt.value" :value="opt.value">
        {{ opt.label }}
      </option>
    </select>
    <p v-if="error" class="mt-1 text-xs text-(--color-error)">{{ error }}</p>
  </div>
</template>

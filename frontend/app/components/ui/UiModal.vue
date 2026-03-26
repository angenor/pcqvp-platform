<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean
  title?: string
  description?: string
  size?: 'sm' | 'md' | 'lg'
  closable?: boolean
  danger?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  close: []
}>()

const sizeClasses: Record<string, string> = {
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
}

function close() {
  if (props.closable !== false) {
    emit('update:modelValue', false)
    emit('close')
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 flex items-center justify-center p-4"
        :style="{ zIndex: 'var(--z-modal)' }"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="close"
        />

        <!-- Content -->
        <div
          class="relative w-full rounded-lg border border-(--border-default) p-6"
          :class="sizeClasses[size ?? 'md']"
          :style="{
            backgroundColor: 'var(--bg-card)',
            boxShadow: 'var(--shadow-lg)',
          }"
        >
          <!-- Close button -->
          <button
            v-if="closable !== false"
            class="absolute top-4 right-4 p-1 rounded-md text-(--text-muted) hover:text-(--text-primary) hover:bg-(--interactive-hover) transition-colors cursor-pointer"
            @click="close"
          >
            <font-awesome-icon :icon="['fas', 'xmark']" />
          </button>

          <!-- Header -->
          <div v-if="title" class="mb-4">
            <h3
              class="text-lg font-semibold"
              :class="danger ? 'text-(--color-error)' : 'text-(--text-primary)'"
            >
              {{ title }}
            </h3>
            <p v-if="description" class="mt-1 text-sm text-(--text-secondary)">
              {{ description }}
            </p>
          </div>

          <!-- Body -->
          <slot />

          <!-- Footer -->
          <div v-if="$slots.footer" class="mt-6 flex items-center justify-end gap-3">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from > div:last-child,
.modal-leave-to > div:last-child {
  transform: scale(0.95);
}
</style>

<script setup lang="ts">
export interface DropdownItem {
  label: string
  icon?: string[]
  action: () => void
  variant?: 'default' | 'danger'
}

defineProps<{
  items: DropdownItem[]
  position?: 'left' | 'right'
}>()

const isOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)

function toggle(e: MouseEvent) {
  e.stopPropagation()
  isOpen.value = !isOpen.value
}

function handleAction(item: DropdownItem, e: MouseEvent) {
  e.stopPropagation()
  isOpen.value = false
  item.action()
}

function onClickOutside(e: Event) {
  if (menuRef.value && !menuRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div ref="menuRef" class="relative">
    <button
      type="button"
      class="p-2 rounded-md text-(--text-muted) hover:text-(--text-primary) hover:bg-(--interactive-hover) transition-colors cursor-pointer"
      @click="toggle"
    >
      <font-awesome-icon :icon="['fas', 'ellipsis-vertical']" />
    </button>

    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 mt-1 w-44 rounded-md border border-(--border-default) py-1 shadow-lg"
        :class="position === 'left' ? 'left-0' : 'right-0'"
        :style="{ backgroundColor: 'var(--bg-card)' }"
      >
        <button
          v-for="(item, i) in items"
          :key="i"
          type="button"
          class="w-full flex items-center gap-2 px-3 py-2 text-sm transition-colors cursor-pointer"
          :class="item.variant === 'danger'
            ? 'text-(--color-error) hover:bg-(--color-error)/10'
            : 'text-(--text-primary) hover:bg-(--interactive-hover)'"
          @click="handleAction(item, $event)"
        >
          <font-awesome-icon v-if="item.icon" :icon="item.icon" class="text-xs w-4" />
          {{ item.label }}
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import type { DropdownItem } from './ui/UiDropdownMenu.vue'

const props = defineProps<{
  id: string
  name: string
  code: string
  type: 'province' | 'region' | 'commune'
  clickRoute?: string
  showFinancialLinks?: boolean
}>()

const emit = defineEmits<{
  edit: []
  delete: []
}>()

const menuItems = computed<DropdownItem[]>(() => [
  {
    label: 'Éditer',
    icon: ['fas', 'pen'],
    action: () => emit('edit'),
  },
  {
    label: 'Supprimer',
    icon: ['fas', 'trash'],
    variant: 'danger' as const,
    action: () => emit('delete'),
  },
])

function handleCardClick() {
  if (props.clickRoute) {
    navigateTo(props.clickRoute)
  }
}
</script>

<template>
  <div
    class="relative rounded-lg border border-(--border-default) p-4 transition-all"
    :class="clickRoute ? 'cursor-pointer hover:border-(--border-focus) hover:shadow-md' : ''"
    :style="{ backgroundColor: 'var(--bg-card)', boxShadow: 'var(--shadow-sm)' }"
    @click="handleCardClick"
  >
    <!-- Header: name + menu -->
    <div class="flex items-start justify-between gap-2">
      <div class="min-w-0 flex-1">
        <h3 class="text-base font-semibold text-(--text-primary) truncate">
          {{ name }}
        </h3>
        <p class="text-sm text-(--text-muted) mt-0.5">{{ code }}</p>
      </div>
      <UiDropdownMenu :items="menuItems" position="right" />
    </div>

    <!-- Financial links (regions only) -->
    <div v-if="showFinancialLinks" class="mt-3 pt-3 border-t border-(--border-default) flex flex-col gap-1.5">
      <NuxtLink
        :to="`/admin/accounts?collectivite_type=region&collectivite_id=${id}`"
        class="inline-flex items-center gap-1.5 text-xs text-(--color-primary) hover:underline"
        @click.stop
      >
        <font-awesome-icon :icon="['fas', 'coins']" />
        Voir les comptes
      </NuxtLink>
      <NuxtLink
        :to="`/admin/accounts/new?collectivite_type=region&collectivite_id=${id}`"
        class="inline-flex items-center gap-1.5 text-xs text-(--color-primary) hover:underline"
        @click.stop
      >
        <font-awesome-icon :icon="['fas', 'plus-circle']" />
        Soumettre un compte
      </NuxtLink>
    </div>
  </div>
</template>

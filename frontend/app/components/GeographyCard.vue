<script setup lang="ts">
import type { DropdownItem } from './ui/UiDropdownMenu.vue'

const props = defineProps<{
  id: string
  name: string
  code: string
  type: 'province' | 'region' | 'commune'
  clickRoute?: string
  showFinancialLinks?: boolean
  highlighted?: boolean
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
    class="relative rounded-lg border p-4 transition-all"
    :class="[
      clickRoute ? 'cursor-pointer hover:border-(--border-focus) hover:shadow-md' : '',
      highlighted
        ? 'border-emerald-500/50 dark:border-emerald-400/40 ring-1 ring-emerald-500/20 dark:ring-emerald-400/15'
        : 'border-(--border-default)',
    ]"
    :style="{ backgroundColor: 'var(--bg-card)', boxShadow: 'var(--shadow-sm)' }"
    @click="handleCardClick"
  >
    <!-- Header: name + menu -->
    <div class="flex items-start justify-between gap-2">
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <h3 class="text-base font-semibold text-(--text-primary)">
            {{ name }}
          </h3>
          <span
            v-if="highlighted"
            class="inline-flex items-center gap-1 rounded-full bg-emerald-100 dark:bg-emerald-900/40 px-2 py-0.5 text-[10px] font-medium text-emerald-700 dark:text-emerald-300"
          >
            <font-awesome-icon :icon="['fas', 'coins']" class="text-[9px]" />
            Comptes
          </span>
        </div>
        <p class="text-sm text-(--text-muted) mt-0.5">{{ code }}</p>
      </div>
      <UiDropdownMenu :items="menuItems" position="right" />
    </div>

    <!-- Financial shortcuts (region / commune) -->
    <div v-if="showFinancialLinks" class="mt-3 pt-3 border-t border-(--border-default) flex flex-col gap-1.5">
      <NuxtLink
        :to="`/admin/accounts?collectivite_type=${type}&collectivite_id=${id}`"
        class="inline-flex items-center gap-1.5 text-xs text-(--color-primary) hover:underline"
        aria-label="Voir les comptes de cette collectivité"
        @click.stop
      >
        <font-awesome-icon :icon="['fas', 'coins']" />
        Voir les comptes
      </NuxtLink>
      <NuxtLink
        :to="`/admin/accounts/new?collectivite_type=${type}&collectivite_id=${id}`"
        class="inline-flex items-center gap-1.5 text-xs text-(--color-primary) hover:underline"
        aria-label="Soumettre un compte pour cette collectivité"
        @click.stop
      >
        <font-awesome-icon :icon="['fas', 'plus-circle']" />
        Soumettre un compte
      </NuxtLink>
    </div>
  </div>
</template>

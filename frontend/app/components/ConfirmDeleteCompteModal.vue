<script setup lang="ts">
interface Props {
  open: boolean
  loading?: boolean
  compteLabel?: string
  blocked?: boolean
  errorMessage?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  compteLabel: '',
  blocked: false,
  errorMessage: null,
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm'): void
  (e: 'setDraft'): void
}>()

function handleBackdropClick() {
  if (!props.loading) emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-delete-compte-title"
      @click.self="handleBackdropClick"
    >
      <div
        class="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800"
      >
        <h2
          id="confirm-delete-compte-title"
          class="mb-3 text-lg font-semibold text-gray-900 dark:text-white"
        >
          <template v-if="blocked">
            Suppression impossible
          </template>
          <template v-else>
            Supprimer le compte administratif
          </template>
        </h2>

        <p class="mb-4 text-sm text-gray-600 dark:text-gray-300">
          <template v-if="blocked">
            Ce compte est publié et peut être référencé par les pages publiques et les exports.
            Repassez-le en brouillon avant de le supprimer.
          </template>
          <template v-else>
            Cette action est définitive. Le compte
            <span v-if="compteLabel" class="font-medium">« {{ compteLabel }} »</span>
            ainsi que toutes ses recettes, dépenses et journaux seront supprimés.
          </template>
        </p>

        <div
          v-if="errorMessage && !blocked"
          class="mb-3 rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700 dark:border-red-700 dark:bg-red-900/30 dark:text-red-200"
        >
          {{ errorMessage }}
        </div>

        <div class="flex items-center justify-end gap-2">
          <button
            type="button"
            class="rounded border border-gray-300 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
            :disabled="loading"
            @click="emit('close')"
          >
            Fermer
          </button>
          <button
            v-if="blocked"
            type="button"
            class="rounded bg-amber-500 px-3 py-2 text-sm font-medium text-white hover:bg-amber-600 disabled:opacity-50"
            :disabled="loading"
            @click="emit('setDraft')"
          >
            Repasser en brouillon
          </button>
          <button
            v-else
            type="button"
            class="rounded bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
            :disabled="loading"
            @click="emit('confirm')"
          >
            <span v-if="loading">Suppression…</span>
            <span v-else>Supprimer définitivement</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

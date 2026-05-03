<script setup lang="ts">
import type { GeodataVersionDetail, GeodataVersionListItem } from '~/types/geodata'

interface Props {
  version: GeodataVersionListItem | GeodataVersionDetail
}
const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'activated', version: GeodataVersionDetail): void
}>()

const { activateVersion } = useGeodataAdmin()
const loading = ref(false)
const errorMsg = ref<string | null>(null)

async function confirm() {
  loading.value = true
  errorMsg.value = null
  try {
    const v = await activateVersion(props.version.id)
    emit('activated', v)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string }; message?: string }
    errorMsg.value = err?.data?.detail || err?.message || 'Erreur'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="w-full max-w-md rounded-lg bg-white p-6 dark:bg-gray-900">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
        Activer cette version ?
      </h2>
      <p class="mt-3 text-sm text-gray-700 dark:text-gray-300">
        La carte d'accueil sera mise à jour immédiatement avec
        <strong>{{ version.original_filename }}</strong>
        ({{ version.features_count }} régions).
      </p>
      <div v-if="errorMsg" class="mt-3 rounded bg-red-50 p-2 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-300">
        {{ errorMsg }}
      </div>
      <div class="mt-4 flex justify-end gap-2">
        <button
          class="rounded border border-gray-300 px-4 py-2 text-gray-700 dark:border-gray-600 dark:text-gray-300"
          :disabled="loading"
          @click="emit('close')"
        >
          Annuler
        </button>
        <button
          class="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
          :disabled="loading"
          @click="confirm"
        >
          {{ loading ? 'Activation…' : 'Activer' }}
        </button>
      </div>
    </div>
  </div>
</template>

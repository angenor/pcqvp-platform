<script setup lang="ts">
import type { GeodataVersionDetail } from '~/types/geodata'

interface Props {
  versionId: string
}
const props = defineProps<Props>()
const emit = defineEmits<{ (e: 'close'): void }>()

const { getVersion } = useGeodataAdmin()
const detail = ref<GeodataVersionDetail | null>(null)
const errorMsg = ref<string | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    detail.value = await getVersion(props.versionId)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string }; message?: string }
    errorMsg.value = err?.data?.detail || err?.message || 'Erreur'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="w-full max-w-4xl rounded-lg bg-white p-6 dark:bg-gray-900">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Prévisualisation de la version
        </h2>
        <button class="text-gray-500" @click="emit('close')">✕</button>
      </div>
      <div v-if="loading" class="mt-4 text-sm text-gray-600 dark:text-gray-400">
        Chargement…
      </div>
      <div v-else-if="errorMsg" class="mt-4 rounded bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-300">
        {{ errorMsg }}
      </div>
      <div v-else-if="detail" class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div class="md:col-span-2">
          <pre class="max-h-96 overflow-auto rounded bg-gray-100 p-3 text-xs text-gray-800 dark:bg-gray-800 dark:text-gray-200">{{ JSON.stringify(detail.geojson_processed, null, 2).slice(0, 2000) }}…</pre>
        </div>
        <div>
          <h3 class="mb-2 font-medium text-gray-900 dark:text-gray-100">
            {{ detail.region_names.length }} régions
          </h3>
          <ul class="max-h-72 overflow-auto text-sm text-gray-700 dark:text-gray-300">
            <li v-for="n in detail.region_names" :key="n">{{ n }}</li>
          </ul>
          <div v-if="detail.warnings.length" class="mt-3">
            <h4 class="text-sm font-medium text-amber-700 dark:text-amber-300">
              Avertissements ({{ detail.warnings.length }})
            </h4>
            <ul class="mt-1 list-disc pl-5 text-xs text-amber-700 dark:text-amber-300">
              <li v-for="(w, idx) in detail.warnings" :key="idx">
                <strong>{{ w.code }}</strong> — {{ w.message }}
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div class="mt-4 flex justify-end">
        <button
          class="rounded border border-gray-300 px-4 py-2 text-gray-700 dark:border-gray-600 dark:text-gray-300"
          @click="emit('close')"
        >
          Fermer
        </button>
      </div>
    </div>
  </div>
</template>

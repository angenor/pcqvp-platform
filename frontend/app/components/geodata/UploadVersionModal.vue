<script setup lang="ts">
import type {
  GeodataJobAccepted,
  GeodataUploadResponse,
} from '~/types/geodata'

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'uploaded', version: GeodataUploadResponse): void
}>()

const { uploadVersion, isJobAccepted, pollJob, getVersion } = useGeodataAdmin()

const file = ref<File | null>(null)
const notes = ref('')
const dragActive = ref(false)
const uploading = ref(false)
const polling = ref(false)
const result = ref<GeodataUploadResponse | null>(null)
const errorMsg = ref<string | null>(null)

const ALLOWED = ['.geojson', '.json']

function isAllowed(name: string): boolean {
  const n = name.toLowerCase()
  return ALLOWED.some((ext) => n.endsWith(ext))
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  dragActive.value = false
  const f = e.dataTransfer?.files?.[0]
  if (!f) return
  if (!isAllowed(f.name)) {
    errorMsg.value = 'Format non autorisé : utilisez .geojson ou .json'
    return
  }
  file.value = f
  errorMsg.value = null
}

function onPick(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  if (!isAllowed(f.name)) {
    errorMsg.value = 'Format non autorisé : utilisez .geojson ou .json'
    return
  }
  file.value = f
  errorMsg.value = null
}

async function submit() {
  if (!file.value) return
  uploading.value = true
  errorMsg.value = null
  try {
    const res = await uploadVersion(file.value, notes.value || undefined)
    if (isJobAccepted(res)) {
      polling.value = true
      const job = await pollJob((res as GeodataJobAccepted).job_id)
      polling.value = false
      if (job.status === 'failed' || !job.version_id) {
        errorMsg.value = job.error_message || 'Échec du traitement'
        return
      }
      const detail = await getVersion(job.version_id)
      result.value = {
        version_id: detail.id,
        uploaded_at: detail.created_at,
        original_filename: detail.original_filename,
        original_size_bytes: detail.original_size_bytes,
        processed_size_bytes: detail.processed_size_bytes,
        features_count: detail.features_count,
        region_names: detail.region_names,
        warnings: detail.warnings,
        is_active: false,
        notes: detail.notes,
      }
      emit('uploaded', result.value)
    } else {
      result.value = res as GeodataUploadResponse
      emit('uploaded', result.value)
    }
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string }; message?: string }
    errorMsg.value = err?.data?.detail || err?.message || 'Erreur inconnue'
  } finally {
    uploading.value = false
    polling.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="w-full max-w-2xl rounded-lg bg-white p-6 dark:bg-gray-900">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
          Téléverser une nouvelle version
        </h2>
        <button class="text-gray-500 hover:text-gray-700 dark:text-gray-400" @click="emit('close')">
          ✕
        </button>
      </div>

      <div v-if="!result" class="mt-4 space-y-4">
        <div
          class="rounded border-2 border-dashed p-8 text-center"
          :class="[
            dragActive
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : 'border-gray-300 dark:border-gray-600',
          ]"
          @dragover.prevent="dragActive = true"
          @dragleave.prevent="dragActive = false"
          @drop="onDrop"
        >
          <p class="text-gray-700 dark:text-gray-300">
            Glissez-déposez votre fichier .geojson ici, ou
            <label class="cursor-pointer text-blue-600 underline">
              choisissez un fichier
              <input
                type="file"
                accept=".geojson,.json,application/json,application/geo+json"
                class="hidden"
                @change="onPick"
              />
            </label>
          </p>
          <p v-if="file" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Sélectionné : {{ file.name }} ({{ Math.round(file.size / 1024) }} Ko)
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Notes (optionnel)
          </label>
          <textarea
            v-model="notes"
            rows="2"
            class="mt-1 w-full rounded border border-gray-300 bg-white p-2 text-gray-900 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
            placeholder="Source, motif, raison du changement…"
          />
        </div>

        <div v-if="errorMsg" class="rounded bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-300">
          {{ errorMsg }}
        </div>

        <div v-if="uploading" class="text-sm text-gray-600 dark:text-gray-400">
          <progress class="w-full" />
          {{ polling ? 'Traitement en cours…' : 'Téléversement…' }}
        </div>

        <div class="flex justify-end gap-2">
          <button
            class="rounded border border-gray-300 px-4 py-2 text-gray-700 dark:border-gray-600 dark:text-gray-300"
            :disabled="uploading"
            @click="emit('close')"
          >
            Annuler
          </button>
          <button
            class="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
            :disabled="!file || uploading"
            @click="submit"
          >
            Téléverser
          </button>
        </div>
      </div>

      <div v-else class="mt-4 space-y-3">
        <h3 class="font-medium text-gray-900 dark:text-gray-100">
          Version créée (inactive)
        </h3>
        <ul class="text-sm text-gray-700 dark:text-gray-300">
          <li>Régions détectées : {{ result.features_count }}</li>
          <li>Taille traitée : {{ Math.round(result.processed_size_bytes / 1024) }} Ko</li>
          <li v-if="result.warnings.length">
            Avertissements : {{ result.warnings.length }}
          </li>
        </ul>
        <details v-if="result.warnings.length" class="text-sm">
          <summary class="cursor-pointer text-amber-700 dark:text-amber-300">
            Voir les avertissements
          </summary>
          <ul class="mt-2 list-disc pl-5">
            <li v-for="(w, idx) in result.warnings" :key="idx">
              <strong>{{ w.code }}</strong> — {{ w.message }}
            </li>
          </ul>
        </details>
        <div class="flex justify-end gap-2">
          <button
            class="rounded bg-blue-600 px-4 py-2 text-white"
            @click="emit('close')"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

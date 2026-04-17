<script setup lang="ts">
import type {
  CollectivityDocument,
  CollectivityParentType,
} from '../../../packages/shared/types/collectivity'

interface Props {
  parentType: CollectivityParentType
  parentId: string | null | undefined
}

const props = defineProps<Props>()

const {
  listDocuments,
  createDocument,
  updateDocumentTitle,
  replaceDocumentFile,
  reorderDocuments,
  deleteDocument,
  uploadDocumentFile,
} = useCollectivityDocuments()

const documents = ref<CollectivityDocument[]>([])
const loading = ref(false)
const uploading = ref(false)
const errorMessage = ref<string | null>(null)
const editingId = ref<string | null>(null)
const editingTitle = ref('')
const dragIndex = ref<number | null>(null)

const MIME_ICON: Record<string, string> = {
  'application/pdf': 'file-pdf',
  'application/msword': 'file-word',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'file-word',
  'application/vnd.ms-excel': 'file-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'file-excel',
}

const fileInput = ref<HTMLInputElement | null>(null)
const replaceInput = ref<HTMLInputElement | null>(null)
const replaceTargetId = ref<string | null>(null)

async function refresh() {
  if (!props.parentId) return
  loading.value = true
  try {
    documents.value = await listDocuments(props.parentType, props.parentId)
    errorMessage.value = null
  } catch {
    errorMessage.value = 'Impossible de charger les documents officiels.'
  } finally {
    loading.value = false
  }
}

watch(() => props.parentId, () => {
  documents.value = []
  if (props.parentId) refresh()
}, { immediate: true })

function triggerAdd() {
  fileInput.value?.click()
}

async function handleAdd(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !props.parentId) return
  errorMessage.value = null
  uploading.value = true
  try {
    const uploaded = await uploadDocumentFile(file)
    if (!uploaded.file || uploaded.success !== 1) {
      errorMessage.value = uploaded.detail || 'Échec du téléversement.'
      return
    }
    const suggestedTitle = deriveTitleFromFilename(uploaded.file.name)
    await createDocument({
      parent_type: props.parentType,
      parent_id: props.parentId,
      title: suggestedTitle,
      file_path: uploaded.file.url,
      file_mime: uploaded.file.mime,
      file_size_bytes: uploaded.file.size,
    })
    await refresh()
  } catch (err: unknown) {
    errorMessage.value = extractErrorMessage(err)
  } finally {
    uploading.value = false
    input.value = ''
  }
}

function triggerReplace(id: string) {
  replaceTargetId.value = id
  replaceInput.value?.click()
}

async function handleReplace(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  const id = replaceTargetId.value
  replaceTargetId.value = null
  if (!file || !id) {
    input.value = ''
    return
  }
  errorMessage.value = null
  uploading.value = true
  try {
    const uploaded = await uploadDocumentFile(file)
    if (!uploaded.file || uploaded.success !== 1) {
      errorMessage.value = uploaded.detail || 'Échec du téléversement.'
      return
    }
    await replaceDocumentFile(id, {
      file_path: uploaded.file.url,
      file_mime: uploaded.file.mime,
      file_size_bytes: uploaded.file.size,
    })
    await refresh()
  } catch (err: unknown) {
    errorMessage.value = extractErrorMessage(err)
  } finally {
    uploading.value = false
    input.value = ''
  }
}

function startEdit(doc: CollectivityDocument) {
  editingId.value = doc.id
  editingTitle.value = doc.title
}

async function saveEdit() {
  const id = editingId.value
  const title = editingTitle.value.trim()
  if (!id || !title) {
    editingId.value = null
    return
  }
  try {
    await updateDocumentTitle(id, { title })
    await refresh()
    editingId.value = null
  } catch (err: unknown) {
    errorMessage.value = extractErrorMessage(err)
  }
}

function cancelEdit() {
  editingId.value = null
}

async function removeDocument(doc: CollectivityDocument) {
  if (!window.confirm(`Supprimer définitivement le document « ${doc.title} » ?`)) return
  try {
    await deleteDocument(doc.id)
    await refresh()
  } catch (err: unknown) {
    errorMessage.value = extractErrorMessage(err)
  }
}

function onDragStart(index: number) {
  dragIndex.value = index
}

function onDragOver(event: DragEvent) {
  event.preventDefault()
}

async function onDrop(targetIndex: number) {
  const from = dragIndex.value
  dragIndex.value = null
  if (from === null || from === targetIndex || !props.parentId) return
  const reordered = [...documents.value]
  const [moved] = reordered.splice(from, 1)
  reordered.splice(targetIndex, 0, moved)
  const ids = reordered.map(d => d.id)
  documents.value = reordered
  try {
    await reorderDocuments({
      parent_type: props.parentType,
      parent_id: props.parentId,
      ordered_ids: ids,
    })
  } catch (err: unknown) {
    errorMessage.value = extractErrorMessage(err)
    await refresh()
  }
}

function formatBytes(size: number): string {
  if (size < 1024) return `${size} o`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} Ko`
  return `${(size / (1024 * 1024)).toFixed(1)} Mo`
}

function formatDate(iso: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

function iconFor(mime: string): string {
  return MIME_ICON[mime] ?? 'file'
}

function deriveTitleFromFilename(name: string): string {
  const base = name.replace(/\.[^.]+$/, '')
  const cleaned = base.replace(/[_-]+/g, ' ').trim()
  if (!cleaned) return 'Document sans titre'
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1)
}

function extractErrorMessage(err: unknown): string {
  if (typeof err !== 'object' || err === null) {
    return 'Une erreur est survenue.'
  }
  const anyErr = err as { statusCode?: number, data?: { detail?: unknown } }
  const detail = anyErr.data?.detail
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object' && 'detail' in detail) {
    const inner = (detail as { detail?: unknown }).detail
    if (typeof inner === 'string') return inner
  }
  if (anyErr.statusCode === 413) return 'Document trop volumineux (maximum 20 Mo).'
  if (anyErr.statusCode === 415) return 'Type de fichier non autorisé (PDF, DOC, DOCX, XLS, XLSX).'
  if (anyErr.statusCode === 401 || anyErr.statusCode === 403) return 'Action non autorisée.'
  return 'Opération impossible. Réessayez plus tard.'
}
</script>

<template>
  <section
    class="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800"
    aria-labelledby="collectivity-documents-title"
  >
    <header class="mb-4 flex flex-wrap items-center justify-between gap-2">
      <h2
        id="collectivity-documents-title"
        class="text-lg font-semibold text-gray-900 dark:text-white"
      >
        Documents officiels
      </h2>
      <button
        type="button"
        class="inline-flex items-center gap-2 rounded bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        :disabled="!parentId || uploading"
        @click="triggerAdd"
      >
        <font-awesome-icon :icon="['fas', 'plus']" />
        <span>Ajouter un document</span>
      </button>
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        accept=".pdf,.doc,.docx,.xls,.xlsx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        @change="handleAdd"
      >
      <input
        ref="replaceInput"
        type="file"
        class="hidden"
        accept=".pdf,.doc,.docx,.xls,.xlsx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        @change="handleReplace"
      >
    </header>

    <p
      v-if="errorMessage"
      class="mb-3 rounded border border-red-300 bg-red-50 p-2 text-sm text-red-700 dark:border-red-700 dark:bg-red-900/30 dark:text-red-200"
    >
      {{ errorMessage }}
    </p>

    <p
      v-if="!parentId"
      class="text-sm text-gray-500 dark:text-gray-400"
    >
      Enregistrez la fiche avant d'ajouter des documents officiels.
    </p>
    <p
      v-else-if="loading"
      class="text-sm text-gray-500 dark:text-gray-400"
    >
      Chargement…
    </p>
    <p
      v-else-if="documents.length === 0"
      class="text-sm text-gray-500 dark:text-gray-400"
    >
      Aucun document officiel pour cette collectivité.
    </p>

    <ul v-if="documents.length > 0" class="space-y-2">
      <li
        v-for="(doc, index) in documents"
        :key="doc.id"
        class="flex flex-wrap items-center gap-3 rounded border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-900"
        draggable="true"
        @dragstart="onDragStart(index)"
        @dragover="onDragOver"
        @drop="onDrop(index)"
      >
        <font-awesome-icon
          :icon="['fas', 'grip-vertical']"
          class="cursor-grab text-gray-400"
          aria-hidden="true"
        />
        <font-awesome-icon
          :icon="['fas', iconFor(doc.file_mime)]"
          class="text-2xl text-blue-600 dark:text-blue-400"
          aria-hidden="true"
        />
        <div class="flex min-w-0 flex-1 flex-col">
          <template v-if="editingId === doc.id">
            <input
              v-model="editingTitle"
              type="text"
              class="w-full rounded border border-gray-300 px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
              @keydown.enter.prevent="saveEdit"
              @keydown.esc.prevent="cancelEdit"
            >
          </template>
          <template v-else>
            <a
              :href="doc.download_url"
              target="_blank"
              rel="noopener"
              class="truncate font-medium text-blue-700 hover:underline dark:text-blue-300"
            >
              {{ doc.title }}
            </a>
          </template>
          <div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ formatBytes(doc.file_size_bytes) }} · MAJ {{ formatDate(doc.updated_at) }}
          </div>
        </div>
        <div class="flex shrink-0 items-center gap-1">
          <template v-if="editingId === doc.id">
            <button
              type="button"
              class="rounded border border-green-400 px-2 py-1 text-xs text-green-700 hover:bg-green-50 dark:border-green-600 dark:text-green-300 dark:hover:bg-green-900/30"
              @click="saveEdit"
            >
              Enregistrer
            </button>
            <button
              type="button"
              class="rounded border border-gray-300 px-2 py-1 text-xs text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
              @click="cancelEdit"
            >
              Annuler
            </button>
          </template>
          <template v-else>
            <button
              type="button"
              class="rounded border border-gray-300 px-2 py-1 text-xs text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
              @click="startEdit(doc)"
            >
              Renommer
            </button>
            <button
              type="button"
              class="rounded border border-gray-300 px-2 py-1 text-xs text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
              :disabled="uploading"
              @click="triggerReplace(doc.id)"
            >
              Remplacer
            </button>
            <button
              type="button"
              class="rounded border border-red-300 px-2 py-1 text-xs text-red-700 hover:bg-red-50 dark:border-red-700 dark:text-red-300 dark:hover:bg-red-900/30"
              @click="removeDocument(doc)"
            >
              Supprimer
            </button>
          </template>
        </div>
      </li>
    </ul>
  </section>
</template>

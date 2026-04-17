<script setup lang="ts">
import type { CollectivityDocument } from '../../../packages/shared/types/collectivity'

interface Props {
  documents: CollectivityDocument[]
}

defineProps<Props>()

const MIME_ICON: Record<string, string> = {
  'application/pdf': 'file-pdf',
  'application/msword': 'file-word',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'file-word',
  'application/vnd.ms-excel': 'file-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'file-excel',
}

function iconFor(mime: string): string {
  return MIME_ICON[mime] ?? 'file'
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
</script>

<template>
  <section
    v-if="documents && documents.length > 0"
    class="my-6 rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800"
    aria-labelledby="public-documents-title"
  >
    <h2
      id="public-documents-title"
      class="mb-4 text-xl font-semibold text-gray-900 dark:text-white"
    >
      Documents officiels
    </h2>
    <ul class="divide-y divide-gray-200 dark:divide-gray-700">
      <li
        v-for="doc in documents"
        :key="doc.id"
        class="flex items-center gap-3 py-3"
      >
        <font-awesome-icon
          :icon="['fas', iconFor(doc.file_mime)]"
          class="text-2xl text-blue-600 dark:text-blue-400"
          aria-hidden="true"
        />
        <div class="min-w-0 flex-1">
          <a
            :href="doc.download_url"
            target="_blank"
            rel="noopener"
            class="block truncate font-medium text-blue-700 hover:underline dark:text-blue-300"
          >
            {{ doc.title }}
          </a>
          <div class="text-sm text-gray-500 dark:text-gray-400">
            {{ formatBytes(doc.file_size_bytes) }} · Mis à jour le {{ formatDate(doc.updated_at) }}
          </div>
        </div>
        <a
          :href="doc.download_url"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-1 rounded border border-blue-200 px-3 py-1 text-sm text-blue-700 hover:bg-blue-50 dark:border-blue-700 dark:text-blue-300 dark:hover:bg-blue-900/30"
          aria-label="Télécharger le document"
        >
          <font-awesome-icon :icon="['fas', 'download']" />
          <span>Télécharger</span>
        </a>
      </li>
    </ul>
  </section>
</template>

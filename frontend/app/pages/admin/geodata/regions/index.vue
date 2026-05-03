<script setup lang="ts">
import type {
  GeodataVersionDetail,
  GeodataVersionListItem,
} from '~/types/geodata'

definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

const { user } = useAuth()
if (process.client && user.value && user.value.role !== 'admin') {
  throw createError({ statusCode: 403, statusMessage: 'Accès réservé aux admins' })
}

const { listVersions, deleteVersion } = useGeodataAdmin()

const items = ref<GeodataVersionListItem[]>([])
const total = ref(0)
const limit = ref(20)
const offset = ref(0)
const loading = ref(false)

const showUpload = ref(false)
const previewId = ref<string | null>(null)
const toActivate = ref<GeodataVersionListItem | null>(null)

const activeVersion = computed(() => items.value.find((v) => v.is_active))

async function refresh() {
  loading.value = true
  try {
    const res = await listVersions(limit.value, offset.value)
    items.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

onMounted(refresh)

function onPage(o: number) {
  offset.value = o
  refresh()
}

function onUploaded() {
  showUpload.value = false
  refresh()
}

function onActivated(_v: GeodataVersionDetail) {
  toActivate.value = null
  refresh()
}

async function onDelete(v: GeodataVersionListItem) {
  if (!confirm(`Supprimer la version ${v.original_filename} ?`)) return
  try {
    await deleteVersion(v.id)
    await refresh()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    alert(err?.data?.detail || 'Erreur')
  }
}
</script>

<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">
        Géodonnées — régions
      </h1>
      <button
        class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        @click="showUpload = true"
      >
        Téléverser une nouvelle version
      </button>
    </div>

    <section class="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
      <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
        Version active
      </h2>
      <div v-if="activeVersion" class="mt-2 grid grid-cols-1 gap-2 text-sm md:grid-cols-4">
        <div>
          <span class="text-gray-500">Date :</span>
          {{ new Date(activeVersion.created_at).toLocaleString('fr-FR') }}
        </div>
        <div>
          <span class="text-gray-500">Régions :</span>
          {{ activeVersion.features_count }}
        </div>
        <div>
          <span class="text-gray-500">Taille :</span>
          {{ Math.round(activeVersion.processed_size_bytes / 1024) }} Ko
        </div>
        <div>
          <span class="text-gray-500">Auteur :</span>
          {{ activeVersion.created_by.email }}
        </div>
      </div>
      <p v-else class="mt-2 text-sm text-gray-500">Aucune version active.</p>
    </section>

    <section class="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
      <h2 class="mb-3 text-lg font-medium text-gray-900 dark:text-gray-100">
        Historique
      </h2>
      <GeodataVersionTable
        :items="items"
        :total="total"
        :limit="limit"
        :offset="offset"
        :loading="loading"
        @preview="(v) => (previewId = v.id)"
        @activate="(v) => (toActivate = v)"
        @delete="onDelete"
        @page="onPage"
      />
    </section>

    <GeodataUploadVersionModal
      v-if="showUpload"
      @close="showUpload = false"
      @uploaded="onUploaded"
    />
    <GeodataPreviewVersionModal
      v-if="previewId"
      :version-id="previewId"
      @close="previewId = null"
    />
    <GeodataActivateVersionModal
      v-if="toActivate"
      :version="toActivate"
      @close="toActivate = null"
      @activated="onActivated"
    />
  </div>
</template>

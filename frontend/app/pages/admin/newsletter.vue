<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

useHead({ title: 'Admin - Newsletter' })

const { subscribers, loading, listSubscribers, exportCsv, deleteSubscriber } = useAdminNewsletter()

const page = ref(1)
const statusFilter = ref('')
const searchQuery = ref('')
const showDeleteModal = ref(false)
const deletingId = ref<string | null>(null)

const columns = [
  { key: 'email', label: 'Email' },
  { key: 'status', label: 'Statut' },
  { key: 'created_at', label: 'Date' },
]

const statusOptions = [
  { value: '', label: 'Tous les statuts' },
  { value: 'actif', label: 'Actif' },
  { value: 'en_attente', label: 'En attente' },
  { value: 'desinscrit', label: 'Desinscrit' },
]

async function load() {
  await listSubscribers({
    page: page.value,
    per_page: 50,
    status: statusFilter.value || undefined,
    search: searchQuery.value || undefined,
  })
}

function confirmDelete(id: string) {
  deletingId.value = id
  showDeleteModal.value = true
}

async function handleDelete() {
  if (!deletingId.value) return
  await deleteSubscriber(deletingId.value)
  showDeleteModal.value = false
  deletingId.value = null
  await load()
}

async function handleExport() {
  await exportCsv()
}

function handleSearch() {
  page.value = 1
  load()
}

watch([statusFilter], () => {
  page.value = 1
  load()
})

onMounted(load)

function statusVariant(status: string) {
  if (status === 'actif') return 'success'
  if (status === 'en_attente') return 'warning'
  return 'gray'
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-(--text-primary)">Newsletter</h1>
      <UiButton variant="success" :icon="['fas', 'file-csv']" @click="handleExport">
        Exporter CSV
      </UiButton>
    </div>

    <!-- Filters -->
    <div class="flex flex-col sm:flex-row gap-3 mb-4">
      <div class="flex-1">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Rechercher par email..."
          class="w-full px-3 py-2 text-sm border border-(--border-default) rounded-md outline-none transition-colors focus:ring-2 focus:ring-(--color-primary)/20 focus:border-(--border-focus)"
          :style="{ backgroundColor: 'var(--bg-input)', color: 'var(--text-primary)' }"
          @keydown.enter="handleSearch"
        />
      </div>
      <UiFormSelect v-model="statusFilter" :options="statusOptions" class="w-48" />
      <UiButton :icon="['fas', 'magnifying-glass']" @click="handleSearch">Rechercher</UiButton>
    </div>

    <div v-if="loading" class="flex justify-center py-8">
      <UiLoadingSpinner size="lg" />
    </div>

    <template v-else-if="subscribers">
      <UiDataTable
        :columns="columns"
        :data="subscribers.items"
        :searchable="false"
        :pagination="false"
        empty-message="Aucun abonne."
        :empty-icon="['fas', 'envelope']"
      >
        <template #cell-status="{ row }">
          <UiBadge :variant="statusVariant(row.status)" dot>{{ row.status }}</UiBadge>
        </template>
        <template #cell-created_at="{ row }">
          <span class="font-mono text-sm">{{ new Date(row.created_at).toLocaleDateString('fr-FR') }}</span>
        </template>
        <template #actions="{ row }">
          <UiButton variant="ghost" size="sm" class="text-(--color-error)" :icon="['fas', 'trash']" @click="confirmDelete(row.id)">
            Supprimer
          </UiButton>
        </template>
      </UiDataTable>

      <!-- Pagination -->
      <div class="flex items-center justify-between mt-4">
        <span class="text-sm text-(--text-muted)">{{ subscribers.total }} abonne(s) au total</span>
        <div class="flex gap-2">
          <UiButton variant="outline" size="sm" :disabled="page <= 1" @click="page--; load()">Precedent</UiButton>
          <UiButton variant="outline" size="sm" :disabled="!subscribers || page * 50 >= subscribers.total" @click="page++; load()">Suivant</UiButton>
        </div>
      </div>
    </template>

    <UiModal v-model="showDeleteModal" title="Confirmer la suppression" danger>
      <p class="text-sm text-(--text-secondary)">Supprimer cet abonne ?</p>
      <template #footer>
        <UiButton variant="ghost" @click="showDeleteModal = false">Annuler</UiButton>
        <UiButton variant="danger" @click="handleDelete">Supprimer</UiButton>
      </template>
    </UiModal>
  </div>
</template>

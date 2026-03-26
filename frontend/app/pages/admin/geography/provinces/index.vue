<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { fetchAdminProvinces, deleteProvince } = useGeography()

const search = ref('')
const currentPage = ref(1)
const pageSize = 20
const items = ref<any[]>([])
const total = ref(0)
const loading = ref(true)
const deleteError = ref('')
const deletingId = ref<string | null>(null)

const columns = [
  { key: 'name', label: 'Nom' },
  { key: 'code', label: 'Code' },
]

async function loadData() {
  loading.value = true
  try {
    const result = await fetchAdminProvinces({
      search: search.value || undefined,
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    })
    items.value = result.items
    total.value = result.total
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

watch([search], () => {
  currentPage.value = 1
  loadData()
})

watch(currentPage, loadData)

async function handleDelete(id: string) {
  deletingId.value = id
  deleteError.value = ''
}

async function confirmDelete() {
  if (!deletingId.value) return
  try {
    await deleteProvince(deletingId.value)
    deletingId.value = null
    await loadData()
  } catch (e: any) {
    deleteError.value = e?.response?._data?.detail || e?.data?.detail || 'Erreur lors de la suppression'
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-(--text-primary)">Provinces</h1>
      <UiButton to="/admin/geography/provinces/new" :icon="['fas', 'plus']">
        Nouvelle province
      </UiButton>
    </div>

    <UiDataTable
      :columns="columns"
      :data="items"
      :loading="loading"
      search-placeholder="Rechercher une province..."
      :pagination="false"
      @search="(q) => { search = q; currentPage = 1; loadData() }"
    >
      <template #actions="{ row }">
        <div class="flex items-center justify-end gap-2">
          <UiButton variant="ghost" size="sm" :to="`/admin/geography/provinces/${row.id}`" :icon="['fas', 'pen']">
            Modifier
          </UiButton>
          <UiButton variant="ghost" size="sm" class="text-(--color-error)" :icon="['fas', 'trash']" @click="handleDelete(row.id)">
            Supprimer
          </UiButton>
        </div>
      </template>
    </UiDataTable>

    <!-- Pagination externe (server-side) -->
    <div v-if="Math.ceil(total / pageSize) > 1" class="flex items-center justify-between mt-4">
      <p class="text-sm text-(--text-muted)">
        Page {{ currentPage }} sur {{ Math.ceil(total / pageSize) }} ({{ total }} resultats)
      </p>
      <div class="flex gap-2">
        <UiButton variant="outline" size="sm" :disabled="currentPage <= 1" @click="currentPage--">
          Precedent
        </UiButton>
        <UiButton variant="outline" size="sm" :disabled="currentPage >= Math.ceil(total / pageSize)" @click="currentPage++">
          Suivant
        </UiButton>
      </div>
    </div>

    <!-- Delete modal -->
    <UiModal :model-value="!!deletingId" title="Confirmer la suppression" danger @close="deletingId = null">
      <p class="text-sm text-(--text-secondary)">
        Etes-vous sur de vouloir supprimer cette province ? Cette action est irreversible.
      </p>
      <UiAlert v-if="deleteError" variant="error" class="mt-3">{{ deleteError }}</UiAlert>
      <template #footer>
        <UiButton variant="ghost" @click="deletingId = null">Annuler</UiButton>
        <UiButton variant="danger" @click="confirmDelete">Supprimer</UiButton>
      </template>
    </UiModal>
  </div>
</template>

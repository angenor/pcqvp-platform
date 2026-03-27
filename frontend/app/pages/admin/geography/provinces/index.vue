<script setup lang="ts">
import type { ProvinceListItem } from '~/types/geography'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { fetchProvinces, fetchIdsWithComptes, deleteProvince } = useGeography()

const search = ref('')
const items = ref<ProvinceListItem[]>([])
const idsWithComptes = ref<Set<string>>(new Set())
const loading = ref(true)
const deleteError = ref('')
const deletingId = ref<string | null>(null)

const filteredItems = computed(() => {
  let list = items.value
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(p => p.name.toLowerCase().includes(q) || p.code.toLowerCase().includes(q))
  }
  return [...list].sort((a, b) => {
    const aHas = idsWithComptes.value.has(a.id) ? 0 : 1
    const bHas = idsWithComptes.value.has(b.id) ? 0 : 1
    return aHas - bHas || a.name.localeCompare(b.name)
  })
})

async function loadData() {
  loading.value = true
  try {
    const [provinces, ids] = await Promise.all([
      fetchProvinces(),
      fetchIdsWithComptes(),
    ])
    items.value = provinces
    idsWithComptes.value = new Set(ids.province_ids)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

function handleEdit(id: string) {
  navigateTo(`/admin/geography/provinces/${id}`)
}

function handleDelete(id: string) {
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

    <!-- Search -->
    <div class="mb-4 max-w-sm">
      <UiFormInput
        v-model="search"
        placeholder="Rechercher une province..."
        :icon="['fas', 'magnifying-glass']"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UiLoadingSpinner size="lg" />
    </div>

    <!-- Grid -->
    <div v-else-if="filteredItems.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <GeographyCard
        v-for="item in filteredItems"
        :key="item.id"
        :id="item.id"
        :name="item.name"
        :code="item.code"
        type="province"
        :highlighted="idsWithComptes.has(item.id)"
        :click-route="`/admin/geography/provinces/${item.id}/regions`"
        @edit="handleEdit(item.id)"
        @delete="handleDelete(item.id)"
      />
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-12 text-center">
      <font-awesome-icon :icon="['fas', 'map']" class="text-4xl mb-3 text-(--text-muted)" />
      <p class="text-sm text-(--text-muted)">Aucune province</p>
      <UiButton class="mt-4" to="/admin/geography/provinces/new" :icon="['fas', 'plus']">
        Nouvelle province
      </UiButton>
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

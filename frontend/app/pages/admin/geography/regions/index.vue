<script setup lang="ts">
import type { RegionListItem, ProvinceListItem } from '~/types/geography'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { fetchRegions, fetchProvinces, fetchIdsWithComptes, deleteRegion } = useGeography()

const search = ref('')
const selectedProvinceId = ref('')
const provinces = ref<ProvinceListItem[]>([])
const items = ref<RegionListItem[]>([])
const idsWithComptes = ref<Set<string>>(new Set())
const loading = ref(true)
const deleteError = ref('')
const deletingId = ref<string | null>(null)

const filteredItems = computed(() => {
  let list = items.value
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(r => r.name.toLowerCase().includes(q) || r.code.toLowerCase().includes(q))
  }
  return [...list].sort((a, b) => {
    const aHas = idsWithComptes.value.has(a.id) ? 0 : 1
    const bHas = idsWithComptes.value.has(b.id) ? 0 : 1
    return aHas - bHas || a.name.localeCompare(b.name)
  })
})

const provinceOptions = computed(() => [
  { value: '', label: 'Toutes les provinces' },
  ...provinces.value.map(p => ({ value: p.id, label: p.name })),
])

async function loadData() {
  loading.value = true
  try {
    items.value = await fetchRegions(selectedProvinceId.value || undefined)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const [provincesData, ids] = await Promise.all([
      fetchProvinces(),
      fetchIdsWithComptes(),
    ])
    provinces.value = provincesData
    idsWithComptes.value = new Set(ids.region_ids)
  } catch {
    provinces.value = []
  }
  await loadData()
})

watch(selectedProvinceId, () => {
  loadData()
})

function handleEdit(id: string) {
  navigateTo(`/admin/geography/regions/${id}`)
}

function handleDelete(id: string) {
  deletingId.value = id
  deleteError.value = ''
}

async function confirmDelete() {
  if (!deletingId.value) return
  try {
    await deleteRegion(deletingId.value)
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
      <h1 class="text-2xl font-bold text-(--text-primary)">Régions</h1>
      <UiButton to="/admin/geography/regions/new" :icon="['fas', 'plus']">
        Nouvelle région
      </UiButton>
    </div>

    <!-- Filters -->
    <div class="flex flex-col sm:flex-row gap-3 mb-4">
      <div class="max-w-xs">
        <UiFormSelect
          v-model="selectedProvinceId"
          :options="provinceOptions"
        />
      </div>
      <div class="max-w-sm flex-1">
        <UiFormInput
          v-model="search"
          placeholder="Rechercher une région..."
          :icon="['fas', 'magnifying-glass']"
        />
      </div>
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
        type="region"
        :highlighted="idsWithComptes.has(item.id)"
        :show-financial-links="true"
        :click-route="`/admin/geography/regions/${item.id}/communes`"
        @edit="handleEdit(item.id)"
        @delete="handleDelete(item.id)"
      />
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-12 text-center">
      <font-awesome-icon :icon="['fas', 'map-marked']" class="text-4xl mb-3 text-(--text-muted)" />
      <p class="text-sm text-(--text-muted)">Aucune région</p>
      <UiButton class="mt-4" to="/admin/geography/regions/new" :icon="['fas', 'plus']">
        Nouvelle région
      </UiButton>
    </div>

    <!-- Delete modal -->
    <UiModal :model-value="!!deletingId" title="Confirmer la suppression" danger @close="deletingId = null">
      <p class="text-sm text-(--text-secondary)">
        Etes-vous sur de vouloir supprimer cette région ? Cette action est irreversible.
      </p>
      <UiAlert v-if="deleteError" variant="error" class="mt-3">{{ deleteError }}</UiAlert>
      <template #footer>
        <UiButton variant="ghost" @click="deletingId = null">Annuler</UiButton>
        <UiButton variant="danger" @click="confirmDelete">Supprimer</UiButton>
      </template>
    </UiModal>
  </div>
</template>

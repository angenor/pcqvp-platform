<script setup lang="ts">
import type { CommuneListItem, RegionListItem, ProvinceListItem } from '~/types/geography'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { fetchCommunes, fetchRegions, fetchProvinces, fetchIdsWithComptes, deleteCommune } = useGeography()

const search = ref('')
const selectedProvinceId = ref('')
const selectedRegionId = ref('')
const provinces = ref<ProvinceListItem[]>([])
const regions = ref<RegionListItem[]>([])
const items = ref<CommuneListItem[]>([])
const idsWithComptes = ref<Set<string>>(new Set())
const loading = ref(true)
const deleteError = ref('')
const deletingId = ref<string | null>(null)

const filteredItems = computed(() => {
  let list = items.value
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(c => c.name.toLowerCase().includes(q) || c.code.toLowerCase().includes(q))
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

const regionOptions = computed(() => [
  { value: '', label: 'Toutes les régions' },
  ...regions.value.map(r => ({ value: r.id, label: r.name })),
])

async function loadCommunes() {
  loading.value = true
  try {
    items.value = await fetchCommunes(selectedRegionId.value || undefined)
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
    idsWithComptes.value = new Set(ids.commune_ids)
  } catch {
    provinces.value = []
  }
  await loadCommunes()
})

watch(selectedProvinceId, async (provinceId) => {
  selectedRegionId.value = ''
  if (provinceId) {
    regions.value = await fetchRegions(provinceId)
  } else {
    regions.value = []
  }
  await loadCommunes()
})

watch(selectedRegionId, () => {
  loadCommunes()
})

function handleEdit(id: string) {
  navigateTo(`/admin/geography/communes/${id}`)
}

function handleDelete(id: string) {
  deletingId.value = id
  deleteError.value = ''
}

async function confirmDelete() {
  if (!deletingId.value) return
  try {
    await deleteCommune(deletingId.value)
    deletingId.value = null
    await loadCommunes()
  } catch (e: any) {
    deleteError.value = e?.response?._data?.detail || e?.data?.detail || 'Erreur lors de la suppression'
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-(--text-primary)">Communes</h1>
      <UiButton to="/admin/geography/communes/new" :icon="['fas', 'plus']">
        Nouvelle commune
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
      <div class="max-w-xs">
        <UiFormSelect
          v-model="selectedRegionId"
          :options="regionOptions"
          :disabled="regions.length === 0 && !selectedProvinceId"
        />
      </div>
      <div class="max-w-sm flex-1">
        <UiFormInput
          v-model="search"
          placeholder="Rechercher une commune..."
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
        type="commune"
        :highlighted="idsWithComptes.has(item.id)"
        @edit="handleEdit(item.id)"
        @delete="handleDelete(item.id)"
      />
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-12 text-center">
      <font-awesome-icon :icon="['fas', 'city']" class="text-4xl mb-3 text-(--text-muted)" />
      <p class="text-sm text-(--text-muted)">Aucune commune</p>
      <UiButton class="mt-4" to="/admin/geography/communes/new" :icon="['fas', 'plus']">
        Nouvelle commune
      </UiButton>
    </div>

    <!-- Delete modal -->
    <UiModal :model-value="!!deletingId" title="Confirmer la suppression" danger @close="deletingId = null">
      <p class="text-sm text-(--text-secondary)">
        Etes-vous sur de vouloir supprimer cette commune ? Cette action est irreversible.
      </p>
      <UiAlert v-if="deleteError" variant="error" class="mt-3">{{ deleteError }}</UiAlert>
      <template #footer>
        <UiButton variant="ghost" @click="deletingId = null">Annuler</UiButton>
        <UiButton variant="danger" @click="confirmDelete">Supprimer</UiButton>
      </template>
    </UiModal>
  </div>
</template>

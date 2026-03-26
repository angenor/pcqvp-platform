<script setup lang="ts">
import type { ProvinceDetail } from '~/types/geography'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const { fetchProvinceDetail, deleteRegion } = useGeography()

const province = ref<ProvinceDetail | null>(null)
const search = ref('')
const loading = ref(true)
const error = ref('')
const deleteError = ref('')
const deletingId = ref<string | null>(null)

const filteredRegions = computed(() => {
  if (!province.value) return []
  if (!search.value) return province.value.regions
  const q = search.value.toLowerCase()
  return province.value.regions.filter(r => r.name.toLowerCase().includes(q) || r.code.toLowerCase().includes(q))
})

async function loadData() {
  loading.value = true
  try {
    province.value = await fetchProvinceDetail(route.params.id as string)
  } catch {
    error.value = 'Province introuvable'
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

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
    <!-- Breadcrumb -->
    <nav class="flex items-center gap-2 text-sm mb-4 text-(--text-muted)">
      <NuxtLink to="/admin/geography/provinces" class="hover:text-(--text-primary) transition-colors">
        Provinces
      </NuxtLink>
      <font-awesome-icon :icon="['fas', 'chevron-right']" class="text-xs" />
      <span class="text-(--text-primary) font-medium">{{ province?.name ?? '...' }}</span>
      <font-awesome-icon :icon="['fas', 'chevron-right']" class="text-xs" />
      <span>Régions</span>
    </nav>

    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-(--text-primary)">
        Régions de {{ province?.name ?? '...' }}
      </h1>
      <UiButton to="/admin/geography/regions/new" :icon="['fas', 'plus']">
        Nouvelle région
      </UiButton>
    </div>

    <!-- Search -->
    <div class="mb-4 max-w-sm">
      <UiFormInput
        v-model="search"
        placeholder="Rechercher une région..."
        :icon="['fas', 'magnifying-glass']"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UiLoadingSpinner size="lg" />
    </div>

    <!-- Error -->
    <UiAlert v-else-if="error" variant="error">{{ error }}</UiAlert>

    <!-- Grid -->
    <div v-else-if="filteredRegions.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <GeographyCard
        v-for="region in filteredRegions"
        :key="region.id"
        :id="region.id"
        :name="region.name"
        :code="region.code"
        type="region"
        :show-financial-links="true"
        :click-route="`/admin/geography/regions/${region.id}/communes`"
        @edit="handleEdit(region.id)"
        @delete="handleDelete(region.id)"
      />
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-12 text-center">
      <font-awesome-icon :icon="['fas', 'map-marked']" class="text-4xl mb-3 text-(--text-muted)" />
      <p class="text-sm text-(--text-muted)">Aucune région pour cette province</p>
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

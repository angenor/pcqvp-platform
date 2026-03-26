<script setup lang="ts">
import type { RegionDetail, ProvinceDetail } from '~/types/geography'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const { fetchRegionDetail, fetchProvinceDetail, deleteCommune } = useGeography()

const region = ref<RegionDetail | null>(null)
const provinceName = ref('')
const provinceId = ref('')
const search = ref('')
const loading = ref(true)
const error = ref('')
const deleteError = ref('')
const deletingId = ref<string | null>(null)

const filteredCommunes = computed(() => {
  if (!region.value) return []
  if (!search.value) return region.value.communes
  const q = search.value.toLowerCase()
  return region.value.communes.filter(c => c.name.toLowerCase().includes(q) || c.code.toLowerCase().includes(q))
})

async function loadData() {
  loading.value = true
  try {
    region.value = await fetchRegionDetail(route.params.id as string)
    // Load province info for breadcrumb
    if (region.value.province_id) {
      provinceId.value = region.value.province_id
      const province = await fetchProvinceDetail(region.value.province_id)
      provinceName.value = province.name
    }
  } catch {
    error.value = 'Région introuvable'
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

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
    await loadData()
  } catch (e: any) {
    deleteError.value = e?.response?._data?.detail || e?.data?.detail || 'Erreur lors de la suppression'
  }
}
</script>

<template>
  <div>
    <!-- Breadcrumb -->
    <nav class="flex items-center gap-2 text-sm mb-4 text-(--text-muted) flex-wrap">
      <NuxtLink to="/admin/geography/provinces" class="hover:text-(--text-primary) transition-colors">
        Provinces
      </NuxtLink>
      <font-awesome-icon :icon="['fas', 'chevron-right']" class="text-xs" />
      <NuxtLink
        v-if="provinceId"
        :to="`/admin/geography/provinces/${provinceId}/regions`"
        class="hover:text-(--text-primary) transition-colors"
      >
        {{ provinceName || '...' }}
      </NuxtLink>
      <font-awesome-icon :icon="['fas', 'chevron-right']" class="text-xs" />
      <span class="text-(--text-primary) font-medium">{{ region?.name ?? '...' }}</span>
      <font-awesome-icon :icon="['fas', 'chevron-right']" class="text-xs" />
      <span>Communes</span>
    </nav>

    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-(--text-primary)">
        Communes de {{ region?.name ?? '...' }}
      </h1>
      <UiButton to="/admin/geography/communes/new" :icon="['fas', 'plus']">
        Nouvelle commune
      </UiButton>
    </div>

    <!-- Search -->
    <div class="mb-4 max-w-sm">
      <UiFormInput
        v-model="search"
        placeholder="Rechercher une commune..."
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
    <div v-else-if="filteredCommunes.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <GeographyCard
        v-for="commune in filteredCommunes"
        :key="commune.id"
        :id="commune.id"
        :name="commune.name"
        :code="commune.code"
        type="commune"
        @edit="handleEdit(commune.id)"
        @delete="handleDelete(commune.id)"
      />
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-12 text-center">
      <font-awesome-icon :icon="['fas', 'city']" class="text-4xl mb-3 text-(--text-muted)" />
      <p class="text-sm text-(--text-muted)">Aucune commune pour cette région</p>
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

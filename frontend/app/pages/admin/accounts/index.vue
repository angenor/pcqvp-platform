<script setup lang="ts">
import type { ProvinceListItem, RegionListItem, CommuneListItem } from '~/types/geography'
import type { CompteListItem } from '~/types/comptes'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { fetchComptes, updateStatus, deleteCompte } = useComptes()
const { fetchProvinces, fetchRegions, fetchCommunes, fetchRegionDetail, fetchCommuneDetail } = useGeography()
const { user } = useAuth()

const isAdmin = computed(() => user.value?.role === 'admin')

const items = ref<CompteListItem[]>([])
const total = ref(0)
const loading = ref(true)

const filterType = ref('')
const provinces = ref<ProvinceListItem[]>([])
const regions = ref<RegionListItem[]>([])
const communes = ref<CommuneListItem[]>([])
const selectedProvinceId = ref('')
const selectedRegionId = ref('')
const selectedCommuneId = ref('')
const filterAnnee = ref<string>('')
const initializing = ref(true)

const columns = [
  { key: 'collectivite_name', label: 'Collectivite' },
  { key: 'collectivite_type', label: 'Type' },
  { key: 'annee_exercice', label: 'Annee', align: 'center' as const },
  { key: 'status', label: 'Statut', align: 'center' as const },
  { key: 'updated_at', label: 'Modifie le' },
]

const typeOptions = [
  { value: '', label: 'Tous' },
  { value: 'province', label: 'Province' },
  { value: 'region', label: 'Region' },
  { value: 'commune', label: 'Commune' },
]

const provinceOptions = computed(() => [
  { value: '', label: 'Toutes' },
  ...provinces.value.map(p => ({ value: p.id, label: p.name })),
])

const regionOptions = computed(() => [
  { value: '', label: 'Toutes' },
  ...regions.value.map(r => ({ value: r.id, label: r.name })),
])

const route = useRoute()

onMounted(async () => {
  provinces.value = await fetchProvinces()

  // Pre-fill filters from query params (e.g. from "Voir les comptes" link)
  const qType = route.query.collectivite_type as string | undefined
  const qId = route.query.collectivite_id as string | undefined
  if (qType && ['province', 'region', 'commune'].includes(qType)) {
    filterType.value = qType
    if (qType === 'commune' && qId) {
      const communeDetail = await fetchCommuneDetail(qId)
      if (communeDetail?.region_id) {
        const regionDetail = await fetchRegionDetail(communeDetail.region_id)
        if (regionDetail?.province_id) {
          selectedProvinceId.value = regionDetail.province_id
          regions.value = await fetchRegions(regionDetail.province_id)
          selectedRegionId.value = communeDetail.region_id
          communes.value = await fetchCommunes(communeDetail.region_id)
          selectedCommuneId.value = qId
        }
      }
    } else if (qType === 'region' && qId) {
      const regionDetail = await fetchRegionDetail(qId)
      if (regionDetail.province_id) {
        selectedProvinceId.value = regionDetail.province_id
        regions.value = await fetchRegions(regionDetail.province_id)
        selectedRegionId.value = qId
      }
    } else if (qType === 'province' && qId) {
      selectedProvinceId.value = qId
    }
  }

  initializing.value = false
  await loadData()
})

watch(selectedProvinceId, async (id) => {
  if (initializing.value) return
  selectedRegionId.value = ''
  selectedCommuneId.value = ''
  regions.value = []
  communes.value = []
  if (id) {
    regions.value = await fetchRegions(id)
  }
  loadData()
})

watch(selectedRegionId, async (id) => {
  if (initializing.value) return
  selectedCommuneId.value = ''
  communes.value = []
  if (id) {
    communes.value = await fetchCommunes(id)
  }
  loadData()
})

watch([selectedCommuneId, filterType, filterAnnee], () => {
  if (initializing.value) return
  loadData()
})

const selectedCollectiviteId = computed(() => {
  if (filterType.value === 'commune' && selectedCommuneId.value) return selectedCommuneId.value
  if (filterType.value === 'region' && selectedRegionId.value) return selectedRegionId.value
  if (filterType.value === 'province' && selectedProvinceId.value) return selectedProvinceId.value
  return undefined
})

const isFilteredByCollectivite = computed(() => Boolean(filterType.value && selectedCollectiviteId.value))

const emptyMessage = computed(() =>
  isFilteredByCollectivite.value
    ? 'Aucun compte pour cette collectivité pour le moment.'
    : 'Aucun compte trouvé',
)

async function loadData() {
  loading.value = true
  try {
    const result = await fetchComptes({
      collectivite_type: filterType.value || undefined,
      collectivite_id: selectedCollectiviteId.value,
      annee: filterAnnee.value ? Number(filterAnnee.value) : undefined,
    })
    items.value = result.items
    total.value = result.total
  } catch {
    // ignore
  } finally {
    loading.value = false
  }
}

async function toggleStatus(row: CompteListItem) {
  const newStatus = row.status === 'published' ? 'draft' : 'published'
  try {
    await updateStatus(row.id, { status: newStatus })
    await loadData()
  } catch {
    // ignore
  }
}

// --- Delete flow ---

const deleteTarget = ref<CompteListItem | null>(null)
const deleteLoading = ref(false)
const deleteBlocked = ref(false)
const deleteError = ref<string | null>(null)

const deleteModalOpen = computed(() => deleteTarget.value !== null)
const deleteLabel = computed(() => {
  const row = deleteTarget.value
  if (!row) return ''
  return `${row.collectivite_name || row.collectivite_type} ${row.annee_exercice}`
})

function openDeleteModal(row: CompteListItem) {
  deleteError.value = null
  deleteBlocked.value = row.status === 'published'
  deleteTarget.value = row
}

function closeDeleteModal() {
  if (deleteLoading.value) return
  deleteTarget.value = null
  deleteError.value = null
  deleteBlocked.value = false
}

async function confirmDelete() {
  const row = deleteTarget.value
  if (!row) return
  deleteLoading.value = true
  deleteError.value = null
  try {
    await deleteCompte(row.id)
    deleteTarget.value = null
    deleteBlocked.value = false
    await loadData()
  } catch (err: unknown) {
    const anyErr = err as { statusCode?: number, data?: { detail?: { error?: string, message?: string } | string } }
    if (anyErr.statusCode === 409) {
      deleteBlocked.value = true
      const detail = anyErr.data?.detail
      if (detail && typeof detail === 'object' && detail.message) {
        deleteError.value = detail.message
      }
    } else {
      deleteError.value = 'Suppression impossible. Réessayez ou contactez un administrateur.'
    }
  } finally {
    deleteLoading.value = false
  }
}

async function setDraftFromModal() {
  const row = deleteTarget.value
  if (!row) return
  deleteLoading.value = true
  try {
    await updateStatus(row.id, { status: 'draft' })
    deleteBlocked.value = false
    await loadData()
    const refreshed = items.value.find(c => c.id === row.id) ?? null
    deleteTarget.value = refreshed
  } catch {
    deleteError.value = 'Impossible de repasser le compte en brouillon.'
  } finally {
    deleteLoading.value = false
  }
}

function formatDate(d: string | null): string {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('fr-FR')
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-(--text-primary)">Comptes administratifs</h1>
      <UiButton to="/admin/accounts/new" :icon="['fas', 'plus']">
        Nouveau compte
      </UiButton>
    </div>

    <!-- Filters -->
    <div
      class="p-4 mb-6 rounded-lg border border-(--border-default)"
      :style="{ backgroundColor: 'var(--bg-card)' }"
    >
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <UiFormSelect v-model="filterType" label="Type" :options="typeOptions" />
        <UiFormSelect v-model="selectedProvinceId" label="Province" :options="provinceOptions" />
        <UiFormSelect v-model="selectedRegionId" label="Region" :options="regionOptions" :disabled="regions.length === 0" />
        <UiFormInput v-model="filterAnnee" type="number" label="Annee" placeholder="Ex: 2023" />
      </div>
    </div>

    <UiDataTable
      :columns="columns"
      :data="items"
      :loading="loading"
      :searchable="false"
      :empty-message="emptyMessage"
      :empty-icon="['fas', 'calculator']"
      :row-link="(row: any) => `/admin/accounts/${row.id}`"
    >
      <template v-if="isFilteredByCollectivite" #empty-action>
        <NuxtLink
          :to="`/admin/accounts/new?collectivite_type=${filterType}&collectivite_id=${selectedCollectiviteId}`"
          class="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:underline dark:text-blue-400"
        >
          <font-awesome-icon :icon="['fas', 'plus-circle']" />
          Soumettre un compte pour cette collectivité
        </NuxtLink>
      </template>
      <template #cell-collectivite_name="{ row, value }">
        <NuxtLink
          :to="`/admin/accounts/${row.id}`"
          class="font-medium text-(--color-primary) hover:underline"
        >
          {{ value }}
        </NuxtLink>
      </template>
      <template #cell-collectivite_type="{ value }">
        <UiBadge variant="gray">{{ value }}</UiBadge>
      </template>
      <template #cell-annee_exercice="{ value }">
        <span class="font-mono">{{ value }}</span>
      </template>
      <template #cell-status="{ row }">
        <UiBadge :variant="row.status === 'published' ? 'success' : 'warning'" dot>
          {{ row.status === 'published' ? 'Publie' : 'Brouillon' }}
        </UiBadge>
      </template>
      <template #cell-updated_at="{ row }">
        <span class="font-mono text-sm">{{ formatDate(row.updated_at || row.created_at) }}</span>
      </template>
      <template #actions="{ row }">
        <div class="flex items-center justify-end gap-1">
          <UiButton variant="ghost" size="sm" :to="`/admin/accounts/${row.id}`" :icon="['fas', 'eye']">
            Voir
          </UiButton>
          <UiButton variant="ghost" size="sm" :to="`/admin/accounts/${row.id}/recettes`">Recettes</UiButton>
          <UiButton variant="ghost" size="sm" :to="`/admin/accounts/${row.id}/depenses`">Depenses</UiButton>
          <button
            v-if="isAdmin"
            class="text-xs px-2 py-1 rounded border border-(--border-default) text-(--text-secondary) hover:bg-(--interactive-hover) transition-colors"
            :title="row.status === 'published' ? 'Repasser en brouillon' : 'Publier'"
            @click="toggleStatus(row)"
          >
            {{ row.status === 'published' ? 'Depublier' : 'Publier' }}
          </button>
          <button
            v-if="isAdmin"
            class="text-xs px-2 py-1 rounded border border-red-300 text-red-700 hover:bg-red-50 dark:border-red-700 dark:text-red-300 dark:hover:bg-red-900/30 transition-colors"
            title="Supprimer ce compte"
            aria-label="Supprimer ce compte"
            @click="openDeleteModal(row)"
          >
            Supprimer
          </button>
        </div>
      </template>
    </UiDataTable>

    <ConfirmDeleteCompteModal
      :open="deleteModalOpen"
      :loading="deleteLoading"
      :blocked="deleteBlocked"
      :compte-label="deleteLabel"
      :error-message="deleteError"
      @close="closeDeleteModal"
      @confirm="confirmDelete"
      @set-draft="setDraftFromModal"
    />

    <div v-if="items.length > 0" class="mt-3 text-sm text-(--text-muted)">
      {{ total }} compte{{ total > 1 ? 's' : '' }}
    </div>
  </div>
</template>

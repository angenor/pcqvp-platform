<script setup lang="ts">
import type { ProvinceListItem, RegionListItem, CommuneListItem } from '~/types/geography'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { createCompte } = useComptes()
const { fetchProvinces, fetchRegions, fetchCommunes, fetchRegionDetail } = useGeography()

const collectiviteType = ref<'province' | 'region' | 'commune'>('commune')
const provinces = ref<ProvinceListItem[]>([])
const regions = ref<RegionListItem[]>([])
const communes = ref<CommuneListItem[]>([])

const selectedProvinceId = ref('')
const selectedRegionId = ref('')
const selectedCommuneId = ref('')
const anneeExercice = ref<number>(new Date().getFullYear())

const loading = ref(true)
const saving = ref(false)
const error = ref('')

const collectiviteTypeOptions = [
  { value: 'province', label: 'Province' },
  { value: 'region', label: 'Region' },
  { value: 'commune', label: 'Commune' },
]

const provinceOptions = computed(() =>
  provinces.value.map(p => ({ value: p.id, label: p.name }))
)
const regionOptions = computed(() =>
  regions.value.map(r => ({ value: r.id, label: r.name }))
)
const communeOptions = computed(() =>
  communes.value.map(c => ({ value: c.id, label: c.name }))
)

const route = useRoute()

onMounted(async () => {
  try {
    provinces.value = await fetchProvinces()

    // Pre-fill from query params (e.g. from GeographyCard financial links)
    const qType = route.query.collectivite_type as string | undefined
    const qId = route.query.collectivite_id as string | undefined
    if (qType && ['province', 'region', 'commune'].includes(qType)) {
      collectiviteType.value = qType as 'province' | 'region' | 'commune'
      if (qType === 'region' && qId) {
        // Find province for this region, then set region
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
  } finally {
    loading.value = false
  }
})

watch(selectedProvinceId, async (id) => {
  selectedRegionId.value = ''
  selectedCommuneId.value = ''
  regions.value = []
  communes.value = []
  if (id) {
    regions.value = await fetchRegions(id)
  }
})

watch(selectedRegionId, async (id) => {
  selectedCommuneId.value = ''
  communes.value = []
  if (id) {
    communes.value = await fetchCommunes(id)
  }
})

const selectedCollectiviteId = computed(() => {
  if (collectiviteType.value === 'province') return selectedProvinceId.value
  if (collectiviteType.value === 'region') return selectedRegionId.value
  return selectedCommuneId.value
})

const canSubmit = computed(() => {
  return !!selectedCollectiviteId.value && !!anneeExercice.value
})

async function handleSubmit() {
  if (!canSubmit.value) return
  saving.value = true
  error.value = ''
  try {
    const result = await createCompte({
      collectivite_type: collectiviteType.value,
      collectivite_id: selectedCollectiviteId.value,
      annee_exercice: anneeExercice.value,
    })
    navigateTo(`/admin/accounts/${result.id}/recettes`)
  } catch (e: any) {
    const detail = e?.response?._data?.detail || e?.data?.detail || ''
    if (detail.includes('existe deja')) {
      error.value = 'Un compte existe deja pour cette collectivite et cette annee.'
    } else if (detail.includes('non trouvee')) {
      error.value = 'Collectivite non trouvee.'
    } else {
      error.value = detail || 'Erreur lors de la creation du compte.'
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-(--text-primary)">Nouveau compte administratif</h1>
      <UiButton variant="ghost" to="/admin/accounts" :icon="['fas', 'arrow-left']">
        Retour a la liste
      </UiButton>
    </div>

    <UiAlert v-if="error" variant="error" class="mb-4" dismissible @dismiss="error = ''">
      {{ error }}
    </UiAlert>

    <div
      class="p-6 rounded-lg border border-(--border-default)"
      :style="{ backgroundColor: 'var(--bg-card)', boxShadow: 'var(--shadow-sm)' }"
    >
      <div v-if="loading" class="flex items-center justify-center py-8">
        <UiLoadingSpinner size="lg" />
      </div>

      <form v-else class="space-y-6" @submit.prevent="handleSubmit">
        <UiFormSelect
          v-model="collectiviteType"
          label="Type de collectivite"
          :options="collectiviteTypeOptions"
          required
        />

        <UiFormSelect
          v-model="selectedProvinceId"
          label="Province"
          :options="provinceOptions"
          placeholder="-- Choisir une province --"
          required
        />

        <UiFormSelect
          v-if="collectiviteType === 'region' || collectiviteType === 'commune'"
          v-model="selectedRegionId"
          label="Region"
          :options="regionOptions"
          :placeholder="regions.length === 0 ? 'Choisir une province d\'abord' : '-- Choisir une region --'"
          :disabled="regions.length === 0"
          required
        />

        <UiFormSelect
          v-if="collectiviteType === 'commune'"
          v-model="selectedCommuneId"
          label="Commune"
          :options="communeOptions"
          :placeholder="communes.length === 0 ? 'Choisir une region d\'abord' : '-- Choisir une commune --'"
          :disabled="communes.length === 0"
          required
        />

        <UiFormInput
          v-model="anneeExercice"
          type="number"
          label="Annee d'exercice"
          required
        />

        <div class="flex justify-end">
          <UiButton type="submit" :disabled="!canSubmit" :loading="saving" :icon="['fas', 'plus']">
            Creer le compte
          </UiButton>
        </div>
      </form>
    </div>
  </div>
</template>

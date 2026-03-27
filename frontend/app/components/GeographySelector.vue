<script setup lang="ts">
import type { ProvinceListItem, RegionListItem, CommuneListItem } from '~/types/geography'

const props = withDefaults(defineProps<{
  years?: number[]
  onSubmit?: (selection: { type: string; id: string; year?: string }) => void
}>(), {
  years: () => [],
  onSubmit: undefined,
})

const { fetchProvinces, fetchRegions, fetchCommunes } = useGeography()

const provinces = ref<ProvinceListItem[]>([])
const regions = ref<RegionListItem[]>([])
const communes = ref<CommuneListItem[]>([])

const selectedProvinceId = ref('')
const selectedRegionId = ref('')
const selectedCommuneId = ref('')
const selectedYear = ref('')

const loading = ref(true)

const hasComptesFilter = { hasComptes: true }

onMounted(async () => {
  try {
    provinces.value = await fetchProvinces(hasComptesFilter)
  } finally {
    loading.value = false
  }
})

watch(selectedProvinceId, async (id) => {
  selectedRegionId.value = ''
  selectedCommuneId.value = ''
  selectedYear.value = ''
  regions.value = []
  communes.value = []
  if (id) {
    regions.value = await fetchRegions(id, hasComptesFilter)
  }
})

watch(selectedRegionId, async (id) => {
  selectedCommuneId.value = ''
  communes.value = []
  if (id) {
    communes.value = await fetchCommunes(id, hasComptesFilter)
  }
})

const showYears = computed(() => props.years.length > 0)

const canSubmit = computed(() => {
  if (!selectedProvinceId.value || !selectedRegionId.value) return false
  if (showYears.value && !selectedYear.value) return false
  return true
})

const provinceOptions = computed(() =>
  provinces.value.map(p => ({ value: p.id, label: p.name }))
)
const regionOptions = computed(() =>
  regions.value.map(r => ({ value: r.id, label: r.name }))
)
const communeOptions = computed(() =>
  communes.value.map(c => ({ value: c.id, label: c.name }))
)
const yearOptions = computed(() =>
  props.years.map(y => ({ value: String(y), label: String(y) }))
)

function handleSubmit() {
  if (!canSubmit.value) return

  const type = selectedCommuneId.value ? 'commune' : 'region'
  const id = selectedCommuneId.value || selectedRegionId.value

  if (props.onSubmit) {
    props.onSubmit({
      type,
      id,
      year: selectedYear.value || undefined,
    })
    return
  }

  if (selectedCommuneId.value) {
    navigateTo(`/communes/${selectedCommuneId.value}/annee/${selectedYear.value}`)
  } else {
    navigateTo(`/regions/${selectedRegionId.value}/annee/${selectedYear.value}`)
  }
}
</script>

<template>
  <div
    class="p-6 rounded-lg border border-(--border-default)"
    :style="{ backgroundColor: 'var(--bg-card)', boxShadow: 'var(--shadow-sm)' }"
  >
    <div v-if="loading" class="flex items-center justify-center py-8">
      <UiLoadingSpinner />
      <span class="ml-2 text-sm text-(--text-secondary)">Chargement...</span>
    </div>

    <div v-else-if="provinces.length === 0" class="text-center py-8">
      <p class="text-(--text-muted)">Aucune province disponible</p>
    </div>

    <div v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <UiFormSelect
          v-model="selectedProvinceId"
          label="Province"
          :options="provinceOptions"
          placeholder="-- Choisir une province --"
          required
        />

        <UiFormSelect
          v-model="selectedRegionId"
          label="Region"
          :options="regionOptions"
          :placeholder="regions.length === 0 ? 'Aucune region disponible' : '-- Choisir une region --'"
          :disabled="regions.length === 0"
          required
        />

        <UiFormSelect
          v-model="selectedCommuneId"
          label="Commune"
          :options="communeOptions"
          :placeholder="communes.length === 0 ? 'Aucune commune disponible' : '-- Optionnel --'"
          :disabled="communes.length === 0"
        />

        <UiFormSelect
          v-if="showYears"
          v-model="selectedYear"
          label="Annee"
          :options="yearOptions"
          :placeholder="props.years.length === 0 ? 'Aucune annee disponible' : '-- Choisir une annee --'"
          :disabled="props.years.length === 0"
          required
        />
      </div>

      <div class="mt-6 flex justify-end">
        <UiButton :disabled="!canSubmit" @click="handleSubmit">
          OK
        </UiButton>
      </div>
    </div>
  </div>
</template>

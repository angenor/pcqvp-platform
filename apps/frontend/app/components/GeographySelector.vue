<script setup lang="ts">
import type { ProvinceListItem, RegionListItem, CommuneListItem } from '~/types/geography'

const props = withDefaults(defineProps<{
  years?: number[]
}>(), {
  years: () => [],
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

// Load provinces on mount
onMounted(async () => {
  try {
    provinces.value = await fetchProvinces()
  } finally {
    loading.value = false
  }
})

// Watch province change -> load regions, reset downstream
watch(selectedProvinceId, async (id) => {
  selectedRegionId.value = ''
  selectedCommuneId.value = ''
  selectedYear.value = ''
  regions.value = []
  communes.value = []
  if (id) {
    regions.value = await fetchRegions(id)
  }
})

// Watch region change -> load communes, reset commune
watch(selectedRegionId, async (id) => {
  selectedCommuneId.value = ''
  communes.value = []
  if (id) {
    communes.value = await fetchCommunes(id)
  }
})

const canSubmit = computed(() => {
  return !!selectedProvinceId.value && !!selectedRegionId.value && !!selectedYear.value
})

function handleSubmit() {
  if (!canSubmit.value) return
  if (selectedCommuneId.value) {
    navigateTo(`/communes/${selectedCommuneId.value}/annee/${selectedYear.value}`)
  } else {
    navigateTo(`/regions/${selectedRegionId.value}/annee/${selectedYear.value}`)
  }
}
</script>

<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <svg
        class="animate-spin h-6 w-6 text-blue-600 dark:text-blue-400"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span class="ml-2 text-gray-600 dark:text-gray-400">Chargement...</span>
    </div>

    <!-- No provinces available -->
    <div v-else-if="provinces.length === 0" class="text-center py-8">
      <p class="text-gray-500 dark:text-gray-400">Aucune province disponible</p>
    </div>

    <!-- Selector form -->
    <div v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Province (mandatory) -->
        <div>
          <label for="geo-province" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Province <span class="text-red-500">*</span>
          </label>
          <select
            id="geo-province"
            v-model="selectedProvinceId"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="" disabled>-- Choisir une province --</option>
            <option
              v-for="province in provinces"
              :key="province.id"
              :value="province.id"
            >
              {{ province.name }}
            </option>
          </select>
        </div>

        <!-- Region (mandatory) -->
        <div>
          <label for="geo-region" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Region <span class="text-red-500">*</span>
          </label>
          <select
            id="geo-region"
            v-model="selectedRegionId"
            :disabled="regions.length === 0"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="" disabled>
              {{ regions.length === 0 ? 'Aucune region disponible' : '-- Choisir une region --' }}
            </option>
            <option
              v-for="region in regions"
              :key="region.id"
              :value="region.id"
            >
              {{ region.name }}
            </option>
          </select>
        </div>

        <!-- Commune (optional, no asterisk) -->
        <div>
          <label for="geo-commune" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Commune
          </label>
          <select
            id="geo-commune"
            v-model="selectedCommuneId"
            :disabled="communes.length === 0"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="">
              {{ communes.length === 0 ? 'Aucune commune disponible' : '-- Optionnel --' }}
            </option>
            <option
              v-for="commune in communes"
              :key="commune.id"
              :value="commune.id"
            >
              {{ commune.name }}
            </option>
          </select>
        </div>

        <!-- Annee (mandatory) -->
        <div>
          <label for="geo-annee" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Annee <span class="text-red-500">*</span>
          </label>
          <select
            id="geo-annee"
            v-model="selectedYear"
            :disabled="props.years.length === 0"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="" disabled>
              {{ props.years.length === 0 ? 'Aucune annee disponible' : '-- Choisir une annee --' }}
            </option>
            <option
              v-for="year in props.years"
              :key="year"
              :value="String(year)"
            >
              {{ year }}
            </option>
          </select>
        </div>
      </div>

      <!-- Submit button -->
      <div class="mt-6 flex justify-end">
        <button
          type="button"
          :disabled="!canSubmit"
          class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-md transition-colors"
          @click="handleSubmit"
        >
          OK
        </button>
      </div>
    </div>
  </div>
</template>

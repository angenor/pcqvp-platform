<script setup lang="ts">
import type { ProvinceListItem, RegionListItem, CommuneListItem } from '~/types/geography'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { createCompte } = useComptes()
const { fetchProvinces, fetchRegions, fetchCommunes } = useGeography()

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

onMounted(async () => {
  try {
    provinces.value = await fetchProvinces()
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
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Nouveau compte administratif</h1>
      <NuxtLink
        to="/admin/accounts"
        class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
      >
        Retour a la liste
      </NuxtLink>
    </div>

    <div v-if="error" class="mb-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-md text-sm">
      {{ error }}
    </div>

    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <div v-if="loading" class="flex items-center justify-center py-8">
        <span class="text-gray-600 dark:text-gray-400">Chargement...</span>
      </div>

      <form v-else @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Type de collectivite -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Type de collectivite <span class="text-red-500">*</span>
          </label>
          <select
            v-model="collectiviteType"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="province">Province</option>
            <option value="region">Region</option>
            <option value="commune">Commune</option>
          </select>
        </div>

        <!-- Province -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Province <span class="text-red-500">*</span>
          </label>
          <select
            v-model="selectedProvinceId"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="" disabled>-- Choisir une province --</option>
            <option v-for="p in provinces" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>

        <!-- Region -->
        <div v-if="collectiviteType === 'region' || collectiviteType === 'commune'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Region <span class="text-red-500">*</span>
          </label>
          <select
            v-model="selectedRegionId"
            :disabled="regions.length === 0"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
          >
            <option value="" disabled>{{ regions.length === 0 ? 'Choisir une province d\'abord' : '-- Choisir une region --' }}</option>
            <option v-for="r in regions" :key="r.id" :value="r.id">{{ r.name }}</option>
          </select>
        </div>

        <!-- Commune -->
        <div v-if="collectiviteType === 'commune'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Commune <span class="text-red-500">*</span>
          </label>
          <select
            v-model="selectedCommuneId"
            :disabled="communes.length === 0"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
          >
            <option value="" disabled>{{ communes.length === 0 ? 'Choisir une region d\'abord' : '-- Choisir une commune --' }}</option>
            <option v-for="c in communes" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>

        <!-- Annee -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Annee d'exercice <span class="text-red-500">*</span>
          </label>
          <input
            v-model.number="anneeExercice"
            type="number"
            min="1900"
            max="2100"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <!-- Submit -->
        <div class="flex justify-end">
          <button
            type="submit"
            :disabled="!canSubmit || saving"
            class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-md transition-colors"
          >
            {{ saving ? 'Creation...' : 'Creer le compte' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

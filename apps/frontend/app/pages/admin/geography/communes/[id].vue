<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const {
  createCommune,
  updateCommune,
  fetchCommuneDetail,
  fetchProvinces,
  fetchRegions,
} = useGeography()

const isNew = computed(() => route.params.id === 'new')
const loading = ref(!isNew.value)
const saving = ref(false)
const error = ref('')

const provinces = ref<any[]>([])
const regions = ref<any[]>([])
const selectedProvinceId = ref('')

const form = ref({
  name: '',
  code: '',
  region_id: '',
  description_json: null as any,
})

const initialRegionId = ref('')

watch(selectedProvinceId, async (provinceId) => {
  regions.value = []
  form.value.region_id = ''
  if (provinceId) {
    try {
      regions.value = await fetchRegions(provinceId)
      // Restore initial region_id after loading regions in edit mode
      if (initialRegionId.value) {
        form.value.region_id = initialRegionId.value
        initialRegionId.value = ''
      }
    } catch {
      error.value = 'Impossible de charger les regions'
    }
  }
})

onMounted(async () => {
  try {
    provinces.value = await fetchProvinces()
  } catch {
    error.value = 'Impossible de charger les provinces'
  }

  if (!isNew.value) {
    try {
      const data = await fetchCommuneDetail(route.params.id as string)
      form.value = {
        name: data.name,
        code: data.code,
        region_id: data.region_id,
        description_json: data.description_json || [],
      }
      // Fetch parent region to get province_id for province filter
      if (data.region_id) {
        const { fetchRegionDetail } = useGeography()
        const regionData = await fetchRegionDetail(data.region_id)
        if (regionData?.province_id) {
          initialRegionId.value = data.region_id
          selectedProvinceId.value = regionData.province_id
        }
      }
    } catch {
      error.value = 'Commune introuvable'
    } finally {
      loading.value = false
    }
  }
})

async function handleSubmit() {
  saving.value = true
  error.value = ''

  if (!form.value.region_id) {
    error.value = 'Veuillez selectionner une region'
    saving.value = false
    return
  }

  try {
    if (isNew.value) {
      await createCommune(form.value)
    } else {
      await updateCommune(route.params.id as string, form.value)
    }
    navigateTo('/admin/geography/communes')
  } catch (e: any) {
    const detail = e?.response?._data?.detail || e?.data?.detail || ''
    if (detail.includes('already exists')) {
      error.value = detail
    } else {
      error.value = 'Erreur lors de la sauvegarde'
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
      {{ isNew ? 'Nouvelle commune' : 'Modifier la commune' }}
    </h1>

    <div
      v-if="loading"
      class="text-center py-12 text-gray-500 dark:text-gray-400"
    >
      Chargement...
    </div>

    <template v-else>
      <div
        v-if="error"
        class="mb-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-md text-red-700 dark:text-red-300 text-sm"
      >
        {{ error }}
      </div>

      <form
        class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 space-y-5"
        @submit.prevent="handleSubmit"
      >
        <div>
          <label
            for="name"
            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Nom
          </label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label
            for="code"
            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Code
          </label>
          <input
            id="code"
            v-model="form.code"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label
            for="province_filter"
            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Province (filtre)
          </label>
          <select
            id="province_filter"
            v-model="selectedProvinceId"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">
              -- Selectionner une province --
            </option>
            <option
              v-for="province in provinces"
              :key="province.id"
              :value="province.id"
            >
              {{ province.name }}
            </option>
          </select>
        </div>

        <div>
          <label
            for="region_id"
            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Region
          </label>
          <select
            id="region_id"
            v-model="form.region_id"
            required
            :disabled="!selectedProvinceId"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="" disabled>
              -- Selectionner une region --
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

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <ClientOnly>
            <RichContentEditor v-model="form.description_json" />
            <template #fallback>
              <div class="h-50 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center text-gray-400 dark:text-gray-500 text-sm">
                Chargement de l'éditeur...
              </div>
            </template>
          </ClientOnly>
        </div>

        <div class="flex items-center gap-4 pt-2">
          <button
            type="submit"
            :disabled="saving"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
          <NuxtLink
            to="/admin/geography/communes"
            class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          >
            Annuler
          </NuxtLink>
        </div>
      </form>
    </template>
  </div>
</template>

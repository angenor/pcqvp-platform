<script setup lang="ts">
import type { ProvinceListItem, RegionListItem, CommuneListItem } from '~/types/geography'
import type { CompteListItem } from '~/types/comptes'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { fetchComptes } = useComptes()
const { fetchProvinces, fetchRegions, fetchCommunes } = useGeography()

const items = ref<CompteListItem[]>([])
const total = ref(0)
const loading = ref(true)

// Filters
const filterType = ref('')
const provinces = ref<ProvinceListItem[]>([])
const regions = ref<RegionListItem[]>([])
const communes = ref<CommuneListItem[]>([])
const selectedProvinceId = ref('')
const selectedRegionId = ref('')
const selectedCommuneId = ref('')
const filterAnnee = ref<string>('')

onMounted(async () => {
  provinces.value = await fetchProvinces()
  await loadData()
})

watch(selectedProvinceId, async (id) => {
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
  selectedCommuneId.value = ''
  communes.value = []
  if (id) {
    communes.value = await fetchCommunes(id)
  }
  loadData()
})

watch([selectedCommuneId, filterType, filterAnnee], () => loadData())

const selectedCollectiviteId = computed(() => {
  if (filterType.value === 'commune' && selectedCommuneId.value) return selectedCommuneId.value
  if (filterType.value === 'region' && selectedRegionId.value) return selectedRegionId.value
  if (filterType.value === 'province' && selectedProvinceId.value) return selectedProvinceId.value
  return undefined
})

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

function statusBadgeClass(status: string): string {
  return status === 'published'
    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
}

function formatDate(d: string | null): string {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('fr-FR')
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Comptes administratifs</h1>
      <NuxtLink
        to="/admin/accounts/new"
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors"
      >
        Nouveau compte
      </NuxtLink>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Type</label>
          <select
            v-model="filterType"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          >
            <option value="">Tous</option>
            <option value="province">Province</option>
            <option value="region">Region</option>
            <option value="commune">Commune</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Province</label>
          <select
            v-model="selectedProvinceId"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          >
            <option value="">Toutes</option>
            <option v-for="p in provinces" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Region</label>
          <select
            v-model="selectedRegionId"
            :disabled="regions.length === 0"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm disabled:opacity-50"
          >
            <option value="">Toutes</option>
            <option v-for="r in regions" :key="r.id" :value="r.id">{{ r.name }}</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Annee</label>
          <input
            v-model="filterAnnee"
            type="number"
            placeholder="Ex: 2023"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          />
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-16">
        <span class="text-gray-600 dark:text-gray-400">Chargement...</span>
      </div>

      <div v-else-if="items.length === 0" class="text-center py-16">
        <p class="text-gray-500 dark:text-gray-400">Aucun compte trouve</p>
      </div>

      <table v-else class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
            <th class="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Collectivite</th>
            <th class="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Type</th>
            <th class="text-center py-3 px-4 text-gray-700 dark:text-gray-300">Annee</th>
            <th class="text-center py-3 px-4 text-gray-700 dark:text-gray-300">Statut</th>
            <th class="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Modifie le</th>
            <th class="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in items"
            :key="item.id"
            class="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30"
          >
            <td class="py-3 px-4 text-gray-900 dark:text-white font-medium">{{ item.collectivite_name }}</td>
            <td class="py-3 px-4 text-gray-500 dark:text-gray-400 capitalize">{{ item.collectivite_type }}</td>
            <td class="py-3 px-4 text-center text-gray-700 dark:text-gray-300">{{ item.annee_exercice }}</td>
            <td class="py-3 px-4 text-center">
              <span class="px-2 py-0.5 rounded text-xs" :class="statusBadgeClass(item.status)">
                {{ item.status === 'published' ? 'Publie' : 'Brouillon' }}
              </span>
            </td>
            <td class="py-3 px-4 text-gray-500 dark:text-gray-400">{{ formatDate(item.updated_at || item.created_at) }}</td>
            <td class="py-3 px-4 text-right">
              <div class="flex items-center justify-end gap-2">
                <NuxtLink
                  :to="`/admin/accounts/${item.id}/recettes`"
                  class="text-blue-600 dark:text-blue-400 hover:underline text-xs"
                >
                  Recettes
                </NuxtLink>
                <NuxtLink
                  :to="`/admin/accounts/${item.id}/depenses`"
                  class="text-blue-600 dark:text-blue-400 hover:underline text-xs"
                >
                  Depenses
                </NuxtLink>
                <NuxtLink
                  :to="`/admin/accounts/${item.id}/recap`"
                  class="text-blue-600 dark:text-blue-400 hover:underline text-xs"
                >
                  Recap
                </NuxtLink>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="items.length > 0" class="px-4 py-3 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-500 dark:text-gray-400">
        {{ total }} compte{{ total > 1 ? 's' : '' }}
      </div>
    </div>
  </div>
</template>

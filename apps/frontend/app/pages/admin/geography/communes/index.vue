<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { fetchAdminCommunes, deleteCommune, fetchRegions } = useGeography()

const search = ref('')
const currentPage = ref(1)
const pageSize = 20
const items = ref<any[]>([])
const total = ref(0)
const loading = ref(true)
const deleteError = ref('')
const deletingId = ref<string | null>(null)
const selectedRegionId = ref<string>('')
const regions = ref<any[]>([])

async function loadRegions() {
  try {
    const result = await fetchRegions()
    regions.value = result.items ?? result
  } catch {
    regions.value = []
  }
}

async function loadData() {
  loading.value = true
  try {
    const result = await fetchAdminCommunes({
      search: search.value || undefined,
      region_id: selectedRegionId.value || undefined,
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    })
    items.value = result.items
    total.value = result.total
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadRegions()
  await loadData()
})

watch([search, selectedRegionId], () => {
  currentPage.value = 1
  loadData()
})

watch(currentPage, loadData)

const totalPages = computed(() => Math.ceil(total.value / pageSize))

async function handleDelete(id: string) {
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
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Communes</h1>
      <NuxtLink
        to="/admin/geography/communes/new"
        class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors dark:bg-blue-500 dark:hover:bg-blue-600"
      >
        + Nouvelle commune
      </NuxtLink>
    </div>

    <!-- Filters -->
    <div class="flex flex-col sm:flex-row gap-4 mb-4">
      <input
        v-model="search"
        type="text"
        placeholder="Rechercher une commune..."
        class="w-full sm:max-w-md px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      />
      <select
        v-model="selectedRegionId"
        class="w-full sm:w-64 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      >
        <option value="">Toutes les régions</option>
        <option v-for="region in regions" :key="region.id" :value="region.id">
          {{ region.name }}
        </option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12 text-gray-500 dark:text-gray-400">
      Chargement...
    </div>

    <!-- Table -->
    <div v-else class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="bg-gray-50 dark:bg-gray-700">
            <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-300">Nom</th>
            <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-300">Code</th>
            <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-300">Région</th>
            <th class="px-4 py-3 text-right text-sm font-semibold text-gray-600 dark:text-gray-300">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="items.length === 0">
            <td colspan="4" class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
              Aucune commune trouvée.
            </td>
          </tr>
          <tr
            v-for="item in items"
            :key="item.id"
            class="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750"
          >
            <td class="px-4 py-3 text-gray-900 dark:text-gray-100">{{ item.name }}</td>
            <td class="px-4 py-3 text-gray-600 dark:text-gray-400">{{ item.code }}</td>
            <td class="px-4 py-3 text-gray-600 dark:text-gray-400">{{ item.region?.name ?? '-' }}</td>
            <td class="px-4 py-3 text-right">
              <NuxtLink
                :to="`/admin/geography/communes/${item.id}`"
                class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 mr-2"
              >
                Modifier
              </NuxtLink>
              <button
                class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                @click="handleDelete(item.id)"
              >
                Supprimer
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between mt-4">
      <p class="text-sm text-gray-600 dark:text-gray-400">
        Page {{ currentPage }} sur {{ totalPages }} ({{ total }} résultats)
      </p>
      <div class="flex gap-2">
        <button
          :disabled="currentPage <= 1"
          class="px-4 py-2 text-sm font-medium rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          @click="currentPage--"
        >
          Précédent
        </button>
        <button
          :disabled="currentPage >= totalPages"
          class="px-4 py-2 text-sm font-medium rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          @click="currentPage++"
        >
          Suivant
        </button>
      </div>
    </div>

    <!-- Delete confirmation modal -->
    <div v-if="deletingId" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Confirmer la suppression</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          Êtes-vous sûr de vouloir supprimer cette commune ? Cette action est irréversible.
        </p>
        <div v-if="deleteError" class="mb-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
          {{ deleteError }}
        </div>
        <div class="flex justify-end gap-3">
          <button
            class="px-4 py-2 text-sm font-medium rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            @click="deletingId = null"
          >
            Annuler
          </button>
          <button
            class="px-4 py-2 text-sm font-medium rounded-lg bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600 text-white transition-colors"
            @click="confirmDelete"
          >
            Supprimer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

useHead({ title: 'Admin - Newsletter' })

const { subscribers, loading, listSubscribers, exportCsv, deleteSubscriber } = useAdminNewsletter()

const page = ref(1)
const statusFilter = ref('')
const searchQuery = ref('')

async function load() {
  await listSubscribers({
    page: page.value,
    per_page: 50,
    status: statusFilter.value || undefined,
    search: searchQuery.value || undefined,
  })
}

async function handleDelete(id: string) {
  if (!confirm('Supprimer cet abonne ?')) return
  await deleteSubscriber(id)
  await load()
}

async function handleExport() {
  await exportCsv()
}

function handleSearch() {
  page.value = 1
  load()
}

watch([statusFilter], () => {
  page.value = 1
  load()
})

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Newsletter</h1>
      <button
        class="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 rounded-lg transition-colors"
        @click="handleExport"
      >
        Exporter CSV
      </button>
    </div>

    <!-- Filters -->
    <div class="flex gap-4 mb-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Rechercher par email..."
        class="flex-1 px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 transition-colors"
        @keydown.enter="handleSearch"
      />
      <select
        v-model="statusFilter"
        class="px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 transition-colors"
      >
        <option value="">Tous les statuts</option>
        <option value="actif">Actif</option>
        <option value="en_attente">En attente</option>
        <option value="desinscrit">Desinscrit</option>
      </select>
      <button
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
        @click="handleSearch"
      >
        Rechercher
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-8">
      <div class="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>

    <div v-else-if="subscribers" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 dark:bg-gray-900">
          <tr>
            <th class="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Email</th>
            <th class="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Statut</th>
            <th class="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Date</th>
            <th class="px-4 py-3 text-right text-gray-700 dark:text-gray-300">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="sub in subscribers.items" :key="sub.id">
            <td class="px-4 py-3 text-gray-900 dark:text-gray-100">{{ sub.email }}</td>
            <td class="px-4 py-3">
              <span
                class="px-2 py-1 text-xs rounded-full"
                :class="{
                  'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400': sub.status === 'actif',
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400': sub.status === 'en_attente',
                  'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400': sub.status === 'desinscrit',
                }"
              >
                {{ sub.status }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500 dark:text-gray-400">
              {{ new Date(sub.created_at).toLocaleDateString('fr-FR') }}
            </td>
            <td class="px-4 py-3 text-right">
              <button
                class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm transition-colors"
                @click="handleDelete(sub.id)"
              >
                Supprimer
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="px-4 py-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <span class="text-sm text-gray-500 dark:text-gray-400">
          {{ subscribers.total }} abonne(s) au total
        </span>
        <div class="flex gap-2">
          <button
            :disabled="page <= 1"
            class="px-3 py-1 text-sm rounded border border-gray-300 dark:border-gray-600 disabled:opacity-50 text-gray-700 dark:text-gray-300 transition-colors"
            @click="page--; load()"
          >
            Precedent
          </button>
          <button
            :disabled="!subscribers || page * 50 >= subscribers.total"
            class="px-3 py-1 text-sm rounded border border-gray-300 dark:border-gray-600 disabled:opacity-50 text-gray-700 dark:text-gray-300 transition-colors"
            @click="page++; load()"
          >
            Suivant
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

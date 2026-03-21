<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { apiFetch } = useApi()

interface DashboardStats {
  comptes: { total: number; published: number; draft: number }
  collectivites: { provinces: number; regions: number; communes: number }
  users: number
  downloads: number
}

const stats = ref<DashboardStats | null>(null)
const loading = ref(true)
const error = ref('')

async function loadStats() {
  loading.value = true
  try {
    stats.value = await apiFetch<DashboardStats>('/api/admin/analytics/stats')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Erreur lors du chargement des statistiques'
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
      Tableau de bord
    </h1>

    <div v-if="error" class="mb-4 p-3 rounded-md bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm">
      {{ error }}
    </div>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400">
      Chargement des statistiques...
    </div>

    <div v-else-if="stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Comptes administratifs -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          Comptes administratifs
        </h3>
        <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
          {{ stats.comptes.total }}
        </p>
        <div class="mt-2 flex gap-3 text-sm">
          <span class="text-green-600 dark:text-green-400">{{ stats.comptes.published }} publies</span>
          <span class="text-yellow-600 dark:text-yellow-400">{{ stats.comptes.draft }} brouillons</span>
        </div>
      </div>

      <!-- Collectivites -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          Collectivites
        </h3>
        <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
          {{ stats.collectivites.provinces + stats.collectivites.regions + stats.collectivites.communes }}
        </p>
        <div class="mt-2 flex flex-col gap-1 text-sm text-gray-600 dark:text-gray-400">
          <span>{{ stats.collectivites.provinces }} provinces</span>
          <span>{{ stats.collectivites.regions }} regions</span>
          <span>{{ stats.collectivites.communes }} communes</span>
        </div>
      </div>

      <!-- Utilisateurs -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          Utilisateurs
        </h3>
        <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
          {{ stats.users }}
        </p>
        <div class="mt-2 text-sm">
          <NuxtLink to="/admin/users" class="text-blue-600 dark:text-blue-400 hover:underline">
            Gerer les utilisateurs
          </NuxtLink>
        </div>
      </div>

      <!-- Telechargements -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          Telechargements
        </h3>
        <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
          {{ stats.downloads }}
        </p>
        <div class="mt-2 text-sm">
          <NuxtLink to="/admin/analytics" class="text-blue-600 dark:text-blue-400 hover:underline">
            Voir les details
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

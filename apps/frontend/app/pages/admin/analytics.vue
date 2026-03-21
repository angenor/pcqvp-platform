<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

useHead({ title: 'Admin - Analytics' })

const { dashboard, loading, loadDashboard, purge } = useAnalytics()
const period = ref('30d')

async function changePeriod(p: string) {
  period.value = p
  await loadDashboard(p)
}

async function handlePurge() {
  if (!confirm('Supprimer les donnees de plus de 12 mois ? Cette action est irreversible.')) return
  const result = await purge()
  alert(result.message)
  await loadDashboard(period.value)
}

onMounted(() => loadDashboard(period.value))
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
      <div class="flex gap-2">
        <button
          v-for="p in ['7d', '30d', '12m']"
          :key="p"
          class="px-3 py-1 text-sm rounded-lg transition-colors"
          :class="period === p
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'"
          @click="changePeriod(p)"
        >
          {{ p }}
        </button>
      </div>
    </div>

    <!-- Purge alert -->
    <div
      v-if="dashboard?.data_retention.purge_eligible"
      class="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg flex items-center justify-between"
    >
      <p class="text-sm text-yellow-800 dark:text-yellow-200">
        {{ dashboard.data_retention.purge_eligible_count }} enregistrements de plus de 12 mois peuvent etre supprimes.
      </p>
      <button
        class="px-3 py-1 text-sm font-medium text-white bg-yellow-600 hover:bg-yellow-700 rounded-lg transition-colors"
        @click="handlePurge"
      >
        Purger
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>

    <template v-else-if="dashboard">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Visits -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Visites
            <span class="text-2xl ml-2">{{ dashboard.visits.total }}</span>
          </h2>
          <div class="space-y-2">
            <div
              v-for="(count, pageType) in dashboard.visits.by_page_type"
              :key="pageType"
              class="flex justify-between text-sm"
            >
              <span class="text-gray-600 dark:text-gray-400 capitalize">{{ pageType }}</span>
              <span class="font-medium text-gray-900 dark:text-white">{{ count }}</span>
            </div>
          </div>
        </div>

        <!-- Downloads -->
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Telechargements
            <span class="text-2xl ml-2">{{ dashboard.downloads.total }}</span>
          </h2>
          <div class="space-y-2">
            <div
              v-for="(count, format) in dashboard.downloads.by_format"
              :key="format"
              class="flex justify-between text-sm"
            >
              <span class="text-gray-600 dark:text-gray-400 uppercase">{{ format }}</span>
              <span class="font-medium text-gray-900 dark:text-white">{{ count }}</span>
            </div>
          </div>
          <p v-if="Object.keys(dashboard.downloads.by_format).length === 0" class="text-sm text-gray-500 dark:text-gray-400">
            Aucun telechargement sur cette periode.
          </p>
        </div>
      </div>

      <!-- Visit trends -->
      <div class="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Tendance des visites</h2>
        <div v-if="dashboard.visits.trend.length === 0" class="text-sm text-gray-500 dark:text-gray-400">
          Pas de donnees sur cette periode.
        </div>
        <div v-else class="space-y-1">
          <div
            v-for="item in dashboard.visits.trend.slice(-14)"
            :key="item.date"
            class="flex items-center gap-3 text-sm"
          >
            <span class="w-24 text-gray-500 dark:text-gray-400">{{ item.date }}</span>
            <div class="flex-1 bg-gray-100 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
              <div
                class="bg-blue-500 h-full rounded-full transition-all"
                :style="{
                  width: `${Math.min(100, (item.count / Math.max(...dashboard!.visits.trend.map(t => t.count))) * 100)}%`
                }"
              />
            </div>
            <span class="w-12 text-right font-medium text-gray-900 dark:text-white">{{ item.count }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { ProvinceListItem, RegionListItem, CommuneListItem } from '~/types/geography'

const { fetchProvinces, fetchRegions, fetchCommunes } = useGeography()

const isLoading = ref(true)
const provinces = ref<ProvinceListItem[]>([])
const regions = ref<RegionListItem[]>([])
const communes = ref<CommuneListItem[]>([])

onMounted(async () => {
  try {
    const [p, r, c] = await Promise.all([
      fetchProvinces(),
      fetchRegions(),
      fetchCommunes(),
    ])
    provinces.value = p
    regions.value = r
    communes.value = c
  } catch (err) {
    console.error('Erreur lors du chargement des statistiques:', err)
  } finally {
    isLoading.value = false
  }
})

const stats = computed(() => [
  {
    label: 'Provinces',
    value: provinces.value.length,
    icon: 'globe',
    color: 'blue',
  },
  {
    label: 'Regions',
    value: regions.value.length,
    icon: 'landmark',
    color: 'green',
  },
  {
    label: 'Communes',
    value: communes.value.length,
    icon: 'city',
    color: 'purple',
  },
])

const colorClasses: Record<string, { bg: string; icon: string; text: string }> = {
  blue: {
    bg: 'bg-blue-100 dark:bg-blue-900/50',
    icon: 'text-blue-600 dark:text-blue-400',
    text: 'text-blue-600 dark:text-blue-400',
  },
  green: {
    bg: 'bg-green-100 dark:bg-green-900/50',
    icon: 'text-green-600 dark:text-green-400',
    text: 'text-green-600 dark:text-green-400',
  },
  purple: {
    bg: 'bg-purple-100 dark:bg-purple-900/50',
    icon: 'text-purple-600 dark:text-purple-400',
    text: 'text-purple-600 dark:text-purple-400',
  },
}
</script>

<template>
  <section class="py-8">
    <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-8 text-center">
      Madagascar en chiffres
    </h2>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 p-6 hover:shadow-xl transition-shadow duration-300"
      >
        <div class="flex items-center gap-4">
          <div :class="[colorClasses[stat.color].bg, 'p-3 rounded-lg']">
            <svg v-if="stat.icon === 'globe'" class="w-8 h-8" :class="colorClasses[stat.color].icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else-if="stat.icon === 'landmark'" class="w-8 h-8" :class="colorClasses[stat.color].icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <svg v-else class="w-8 h-8" :class="colorClasses[stat.color].icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold" :class="colorClasses[stat.color].text">
              <template v-if="isLoading">
                <span class="inline-block w-12 h-8 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></span>
              </template>
              <template v-else>{{ stat.value }}</template>
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

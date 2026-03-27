<script setup lang="ts">
import type { RegionListItem } from '~/types/geography'

const { fetchRegions } = useGeography()

const regions = ref<RegionListItem[]>([])
const isLoading = ref(true)
const hoveredRegion = ref<RegionListItem | null>(null)

onMounted(async () => {
  try {
    regions.value = await fetchRegions()
  } catch (err) {
    console.error('Erreur lors du chargement des régions:', err)
  } finally {
    isLoading.value = false
  }
})

const handleRegionClick = (region: RegionListItem | null) => {
  if (region) {
    navigateTo(`/collectivite/region-${region.id}`)
  }
}

const handleRegionHover = (region: RegionListItem | null) => {
  hoveredRegion.value = region
}
</script>

<template>
  <section class="py-8">
    <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-8 text-center">
      Carte des Régions de Madagascar
    </h2>

    <div class="grid lg:grid-cols-3 gap-6 items-stretch">
      <!-- Carte (2/3 de largeur sur desktop) -->
      <div class="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 overflow-hidden map-container">
        <ClientOnly>
          <MadagascarMap
            :regions="regions"
            :is-loading="isLoading"
            class="h-full w-full"
            @region-click="handleRegionClick"
            @region-hover="handleRegionHover"
          />
          <template #fallback>
            <div class="h-full flex items-center justify-center">
              <UiLoadingSpinner />
            </div>
          </template>
        </ClientOnly>
      </div>

      <!-- Panneau latéral : liste des régions -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 p-5 overflow-y-auto panel-container">
        <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-4">
          Régions
        </h3>

        <div v-if="isLoading" class="space-y-3">
          <div v-for="i in 6" :key="i" class="h-10 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"></div>
        </div>

        <div v-else class="space-y-2">
          <button
            v-for="region in regions"
            :key="region.id"
            class="w-full text-left px-4 py-3 rounded-lg transition-colors cursor-pointer"
            :class="[
              hoveredRegion?.id === region.id
                ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-700'
                : 'bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700',
              'border border-transparent'
            ]"
            @click="handleRegionClick(region)"
            @mouseenter="hoveredRegion = region"
            @mouseleave="hoveredRegion = null"
          >
            <span class="text-sm font-medium text-gray-800 dark:text-gray-200">
              {{ region.name }}
            </span>
          </button>
        </div>

        <div v-if="!isLoading" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 text-center">
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ regions.length }} régions
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.map-container {
  min-height: 500px;
  height: 600px;
}

.panel-container {
  max-height: 600px;
}

@media (min-width: 1024px) {
  .map-container {
    height: 650px;
  }
  .panel-container {
    max-height: 650px;
  }
}

@media (max-width: 1023px) {
  .map-container {
    height: 500px;
    min-height: 400px;
  }
  .panel-container {
    max-height: 400px;
  }
}
</style>

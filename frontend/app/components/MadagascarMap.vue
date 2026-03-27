<script setup lang="ts">
import type { RegionListItem } from '~/types/geography'

const props = defineProps<{
  regions: RegionListItem[]
  isLoading?: boolean
}>()

const emit = defineEmits<{
  regionClick: [region: RegionListItem | null]
  regionHover: [region: RegionListItem | null]
}>()

const { $am5 } = useNuxtApp()
const colorMode = useColorMode()
const isDark = computed(() => colorMode.value === 'dark')

const legendOpen = ref(false)
const chartRef = ref<HTMLDivElement | null>(null)
let root: any = null
let polygonSeries: any = null

// Mapping des IDs amCharts vers les noms de régions
const amchartsToRegionName: Record<string, string> = {
  'MG-TIT': 'Itasy',
  'MG-TAT': 'Analamanga',
  'MG-TVA': 'Vakinankaratra',
  'MG-TBO': 'Bongolava',
  'MG-FAM': "Amoron'i Mania",
  'MG-FHM': 'Haute Matsiatra',
  'MG-FVF': 'Vatovavy-Fitovinany',
  'MG-FVH': 'Vatovavy',
  'MG-FFT': 'Fitovinany',
  'MG-FHO': 'Ihorombe',
  'MG-FAT': 'Atsimo-Atsinanana',
  'MG-MAL': 'Alaotra-Mangoro',
  'MG-AAO': 'Alaotra-Mangoro',
  'MG-MAT': 'Atsinanana',
  'MG-MAA': 'Analanjirofo',
  'MG-MSF': 'Sofia',
  'MG-MBO': 'Boeny',
  'MG-MBT': 'Betsiboka',
  'MG-MME': 'Melaky',
  'MG-AAM': 'Atsimo-Andrefana',
  'MG-TAD': 'Androy',
  'MG-TAN': 'Anosy',
  'MG-MAM': 'Menabe',
  'MG-DSN': 'Diana',
  'MG-DSV': 'Sava',
}

const findRegionByName = (name: string): RegionListItem | undefined => {
  return props.regions.find(r =>
    r.name.toLowerCase() === name.toLowerCase() ||
    r.name.toLowerCase().includes(name.toLowerCase()) ||
    name.toLowerCase().includes(r.name.toLowerCase())
  )
}

const findRegionByAmchartsId = (amchartsId: string): RegionListItem | undefined => {
  const regionName = amchartsToRegionName[amchartsId]
  if (!regionName) return undefined
  return findRegionByName(regionName)
}

const getRegionColor = (region: RegionListItem | undefined): string => {
  if (!region) return isDark.value ? '#374151' : '#e5e7eb'
  // Couleur uniforme pour les régions avec données
  return isDark.value ? '#2563eb' : '#3b82f6'
}

const initChart = async () => {
  if (!chartRef.value || !$am5) return

  const madagascarRegionHigh = await import('@amcharts/amcharts5-geodata/madagascarRegionHigh').then(m => m.default)

  root = $am5.core.Root.new(chartRef.value)
  root.setThemes([$am5.themes.Animated.new(root)])

  const chart = root.container.children.push(
    $am5.map.MapChart.new(root, {
      panX: 'translateX',
      panY: 'translateY',
      wheelX: 'none',
      wheelY: 'none',
      maxZoomLevel: 1,
      projection: $am5.map.geoMercator(),
      homeGeoPoint: { latitude: -18.8792, longitude: 47.5079 },
      homeZoomLevel: 1,
    })
  )

  polygonSeries = chart.series.push(
    $am5.map.MapPolygonSeries.new(root, {
      geoJSON: madagascarRegionHigh,
      valueField: 'value',
      calculateAggregates: true,
    })
  )

  polygonSeries.mapPolygons.template.setAll({
    tooltipText: '{name}',
    interactive: true,
    fill: $am5.core.color(isDark.value ? '#374151' : '#e5e7eb'),
    strokeWidth: 1,
    stroke: $am5.core.color(isDark.value ? '#1f2937' : '#ffffff'),
    cursorOverStyle: 'pointer',
  })

  polygonSeries.mapPolygons.template.states.create('hover', {
    fill: $am5.core.color(isDark.value ? '#4f46e5' : '#818cf8'),
  })

  polygonSeries.mapPolygons.template.events.on('click', (ev: any) => {
    const dataItem = ev.target.dataItem
    if (dataItem) {
      const amchartsId = dataItem.get('id')
      const region = findRegionByAmchartsId(amchartsId)
      emit('regionClick', region || null)
    }
  })

  polygonSeries.mapPolygons.template.events.on('pointerover', (ev: any) => {
    const dataItem = ev.target.dataItem
    if (dataItem) {
      const amchartsId = dataItem.get('id')
      const region = findRegionByAmchartsId(amchartsId)
      emit('regionHover', region || null)
    }
  })

  polygonSeries.mapPolygons.template.events.on('pointerout', () => {
    emit('regionHover', null)
  })

  polygonSeries.mapPolygons.template.adapters.add('tooltipText', (_text: string, target: any) => {
    const dataItem = target.dataItem
    if (dataItem) {
      const amchartsId = dataItem.get('id')
      const region = findRegionByAmchartsId(amchartsId)
      if (region) {
        return `[bold]${region.name}[/]`
      }
    }
    return '{name}'
  })

  updateColors()
}

const updateColors = () => {
  if (!polygonSeries) return
  polygonSeries.mapPolygons.each((polygon: any) => {
    const dataItem = polygon.dataItem
    if (dataItem) {
      const amchartsId = dataItem.get('id')
      const region = findRegionByAmchartsId(amchartsId)
      const color = getRegionColor(region)
      polygon.set('fill', $am5.core.color(color))
    }
  })
}

watch(() => props.regions, () => updateColors(), { deep: true })

watch(isDark, () => {
  if (polygonSeries) {
    polygonSeries.mapPolygons.template.setAll({
      stroke: $am5.core.color(isDark.value ? '#1f2937' : '#ffffff'),
    })
    polygonSeries.mapPolygons.template.states.create('hover', {
      fill: $am5.core.color(isDark.value ? '#4f46e5' : '#818cf8'),
    })
    updateColors()
  }
})

onMounted(() => initChart())
onUnmounted(() => { if (root) root.dispose() })
</script>

<template>
  <div class="relative w-full h-full min-h-100">
    <!-- Loading overlay -->
    <div
      v-if="isLoading"
      class="absolute inset-0 bg-white/80 dark:bg-gray-900/80 flex items-center justify-center z-10 rounded-xl"
    >
      <div class="flex flex-col items-center gap-3">
        <UiLoadingSpinner />
        <span class="text-sm text-gray-600 dark:text-gray-400">Chargement de la carte...</span>
      </div>
    </div>

    <!-- Chart container -->
    <div ref="chartRef" class="w-full h-full min-h-100 rounded-xl" />

    <!-- Légende repliable -->
    <div class="absolute bottom-4 left-4 z-20">
      <button
        v-if="!legendOpen"
        @click="legendOpen = true"
        class="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-2.5 shadow-lg border border-gray-200 dark:border-gray-700 cursor-pointer hover:bg-white dark:hover:bg-gray-800 transition-colors"
        title="Afficher la légende"
      >
        <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
      </button>

      <Transition name="legend">
        <div
          v-if="legendOpen"
          class="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-3 shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-xs font-semibold text-gray-700 dark:text-gray-300">Régions</h4>
            <button
              @click="legendOpen = false"
              class="ml-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 cursor-pointer transition-colors"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="flex flex-col gap-1.5">
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 rounded" :class="isDark ? 'bg-[#374151]' : 'bg-[#e5e7eb]'"></div>
              <span class="text-xs text-gray-600 dark:text-gray-400">Sans données</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 rounded" :class="isDark ? 'bg-[#2563eb]' : 'bg-[#3b82f6]'"></div>
              <span class="text-xs text-gray-600 dark:text-gray-400">Avec données</span>
            </div>
          </div>
          <div class="border-t border-gray-200 dark:border-gray-600 mt-3 pt-2">
            <span class="text-xs text-gray-500 dark:text-gray-400 italic">Cliquez sur une région</span>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.legend-enter-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.legend-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.legend-enter-from,
.legend-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(8px);
}
</style>

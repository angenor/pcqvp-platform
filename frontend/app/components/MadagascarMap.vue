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

const fetchState = ref<'loading' | 'success' | 'error'>('loading')
const errorMessage = ref('')

function normalize(name: string): string {
  return name
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .trim()
}

const regionsByNorm = computed<Map<string, RegionListItem>>(() => {
  const m = new Map<string, RegionListItem>()
  for (const r of props.regions) m.set(normalize(r.name), r)
  return m
})

function findRegionForFeature(props_: any): RegionListItem | undefined {
  const name = props_?.name
  if (!name) return undefined
  return regionsByNorm.value.get(normalize(String(name)))
}

function getRegionColor(region: RegionListItem | undefined): string {
  if (!region) return isDark.value ? '#374151' : '#e5e7eb'
  return isDark.value ? '#2563eb' : '#3b82f6'
}

async function fetchGeoJson(): Promise<any> {
  try {
    fetchState.value = 'loading'
    const data = await $fetch<any>('/api/geography/regions/geojson')
    fetchState.value = 'success'
    return data
  } catch (e: unknown) {
    fetchState.value = 'error'
    errorMessage.value = 'Carte temporairement indisponible'
    throw e
  }
}

function computeBounds(geojson: any): { north: number; south: number; east: number; west: number } | null {
  let north = -Infinity, south = Infinity, east = -Infinity, west = Infinity
  const visit = (c: any) => {
    if (typeof c[0] === 'number') {
      const [lon, lat] = c
      if (lon < west) west = lon
      if (lon > east) east = lon
      if (lat < south) south = lat
      if (lat > north) north = lat
    } else if (Array.isArray(c)) {
      for (const x of c) visit(x)
    }
  }
  for (const f of geojson?.features || []) visit(f.geometry?.coordinates || [])
  if (!isFinite(north)) return null
  return { north, south, east, west }
}

function fitChart(chart: any, geojson: any) {
  const b = computeBounds(geojson)
  if (!b) return
  const lat = (b.north + b.south) / 2
  const lon = (b.east + b.west) / 2
  const dLat = Math.max(0.5, b.north - b.south)
  const dLon = Math.max(0.5, b.east - b.west)
  // Niveau de zoom Mercator approximatif pour caser le bbox dans le viewport,
  // avec marge 1.4× pour laisser respirer la carte.
  // Marge 0.85× pour garantir que toute l'emprise (y compris pointe nord/sud) reste visible.
  const zoom = Math.max(1.2, Math.min(15, Math.min(40 / dLon, 22 / dLat) * 0.85))
  try { chart.zoomToGeoPoint({ latitude: lat, longitude: lon }, zoom, false) } catch { /* noop */ }
}

async function initChart() {
  if (!chartRef.value || !$am5) return
  let geojson: any
  try {
    geojson = await fetchGeoJson()
  } catch {
    return
  }

  root = $am5.core.Root.new(chartRef.value)
  root.setThemes([$am5.themes.Animated.new(root)])

  const chart = root.container.children.push(
    $am5.map.MapChart.new(root, {
      panX: 'translateX',
      panY: 'translateY',
      wheelX: 'none',
      wheelY: 'none',
      projection: $am5.map.geoMercator(),
      homeGeoPoint: { latitude: -18.8792, longitude: 47.5079 },
      homeZoomLevel: 7,
    })
  )

  polygonSeries = chart.series.push(
    $am5.map.MapPolygonSeries.new(root, {
      geoJSON: geojson,
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
    const di = ev.target.dataItem
    if (!di) return
    const dataContext = di.dataContext as any
    const region = findRegionForFeature(dataContext)
    if (!region) return
    emit('regionClick', region)
  })

  polygonSeries.mapPolygons.template.events.on('pointerover', (ev: any) => {
    const di = ev.target.dataItem
    if (!di) return
    const region = findRegionForFeature(di.dataContext as any)
    emit('regionHover', region || null)
  })

  polygonSeries.mapPolygons.template.events.on('pointerout', () => {
    emit('regionHover', null)
  })

  polygonSeries.mapPolygons.template.adapters.add(
    'tooltipText',
    (_text: string, target: any) => {
      const di = target.dataItem
      if (!di) return '{name}'
      const ctx = di.dataContext as any
      const region = findRegionForFeature(ctx)
      if (region) return `[bold]${region.name}[/]`
      const fallback = ctx?.name ? `${ctx.name} — Données non disponibles` : 'Données non disponibles'
      return fallback
    }
  )

  polygonSeries.mapPolygons.template.adapters.add(
    'cursorOverStyle',
    (_v: any, target: any) => {
      const di = target.dataItem
      if (!di) return 'pointer'
      return findRegionForFeature(di.dataContext as any) ? 'pointer' : 'default'
    }
  )

  polygonSeries.events.on('datavalidated', () => {
    applyColors()
    requestAnimationFrame(() => fitChart(chart, geojson))
  })

  // Filet de sécurité : si `datavalidated` n'a pas encore positionné la carte
  // après 500 ms (cas observé avec certains GeoJSON), on force le recadrage.
  setTimeout(() => {
    if (chart.get('zoomLevel') == null || (chart.get('zoomLevel') as number) < 1.4) {
      fitChart(chart, geojson)
    }
  }, 500)
}

function applyColors() {
  if (!polygonSeries || !$am5) return
  polygonSeries.mapPolygons.each((polygon: any) => {
    const di = polygon.dataItem
    if (!di) return
    const region = findRegionForFeature(di.dataContext as any)
    polygon.set('fill', $am5.core.color(getRegionColor(region)))
  })
}

watch(() => props.regions, () => nextTick(() => applyColors()), { deep: true })

watch(isDark, () => {
  if (!polygonSeries) return
  polygonSeries.mapPolygons.template.setAll({
    stroke: $am5.core.color(isDark.value ? '#1f2937' : '#ffffff'),
  })
  polygonSeries.mapPolygons.template.states.create('hover', {
    fill: $am5.core.color(isDark.value ? '#4f46e5' : '#818cf8'),
  })
  applyColors()
})

onMounted(() => initChart())
onUnmounted(() => { if (root) root.dispose() })
</script>

<template>
  <div class="relative w-full h-full min-h-100">
    <div
      v-if="isLoading || fetchState === 'loading'"
      class="absolute inset-0 bg-white/80 dark:bg-gray-900/80 flex items-center justify-center z-10 rounded-xl"
    >
      <div class="flex flex-col items-center gap-3">
        <UiLoadingSpinner />
        <span class="text-sm text-gray-600 dark:text-gray-400">Chargement de la carte...</span>
      </div>
    </div>

    <div
      v-if="fetchState === 'error'"
      class="absolute inset-0 flex items-center justify-center rounded-xl bg-gray-50 dark:bg-gray-900"
    >
      <div class="text-center">
        <p class="text-sm text-gray-600 dark:text-gray-400">{{ errorMessage }}</p>
      </div>
    </div>

    <div ref="chartRef" class="w-full h-full min-h-100 rounded-xl" />

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

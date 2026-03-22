<script setup lang="ts">
import type { TemplateLine } from '~/types/templates'

interface ColumnDef {
  code: string
  name: string
  editable: boolean
  computed?: boolean
}

const props = defineProps<{
  templateLines: TemplateLine[]
  columns: ColumnDef[]
  values: Record<string, Record<string, number>>
  computedValues?: Record<string, Record<string, number | null>>
  hierarchicalSums?: Record<string, Record<string, number>>
  templateType: 'recette' | 'depense'
}>()

const emit = defineEmits<{
  'save-line': [templateLineId: string, values: Record<string, number>]
}>()

// Track sync status per line
const lineStatus = ref<Record<string, 'idle' | 'pending' | 'success' | 'error'>>({})

// Local editable values
const localValues = ref<Record<string, Record<string, number>>>({})

// Initialize local values from props
watch(() => props.values, (newVals) => {
  for (const [tlId, vals] of Object.entries(newVals)) {
    if (!localValues.value[tlId]) {
      localValues.value[tlId] = { ...vals }
    }
  }
}, { immediate: true, deep: true })

function getLineValue(templateLineId: string, colCode: string): number | string {
  const tl = props.templateLines.find(t => t.id === templateLineId)
  if (!tl) return ''

  // For Niv1/Niv2, show hierarchical sums
  if (tl.level < 3 && props.hierarchicalSums?.[tl.compte_code]) {
    const sums = props.hierarchicalSums[tl.compte_code]
    return sums[colCode] ?? ''
  }

  // Check computed values first
  if (props.computedValues?.[templateLineId]?.[colCode] !== undefined) {
    return props.computedValues[templateLineId][colCode] ?? ''
  }

  // Local editable values
  return localValues.value[templateLineId]?.[colCode] ?? props.values[templateLineId]?.[colCode] ?? ''
}

function isEditable(templateLineId: string, col: ColumnDef): boolean {
  if (!col.editable) return false
  const tl = props.templateLines.find(t => t.id === templateLineId)
  return tl?.level === 3
}

function onCellBlur(templateLineId: string) {
  const vals = localValues.value[templateLineId] || {}
  // Clean values - convert empties to 0
  const cleanVals: Record<string, number> = {}
  for (const col of props.columns) {
    if (col.editable) {
      cleanVals[col.code] = Number(vals[col.code]) || 0
    }
  }
  localValues.value[templateLineId] = { ...vals, ...cleanVals }

  lineStatus.value[templateLineId] = 'pending'
  emit('save-line', templateLineId, cleanVals)
}

function setLineStatus(templateLineId: string, status: 'idle' | 'pending' | 'success' | 'error') {
  lineStatus.value[templateLineId] = status
}

// Expose for parent component
defineExpose({ setLineStatus })

function onCellInput(templateLineId: string, colCode: string, event: Event) {
  const val = Number((event.target as HTMLInputElement).value) || 0
  if (!localValues.value[templateLineId]) {
    localValues.value[templateLineId] = {}
  }
  localValues.value[templateLineId][colCode] = val
}

// Group lines by section
const sections = computed(() => {
  const grouped: Record<string, TemplateLine[]> = {}
  for (const tl of props.templateLines) {
    const sec = tl.section
    if (!grouped[sec]) grouped[sec] = []
    grouped[sec].push(tl)
  }
  return Object.entries(grouped).map(([name, lines]) => ({
    name: name === 'fonctionnement' ? 'Fonctionnement' : 'Investissement',
    key: name,
    lines: lines.sort((a, b) => a.sort_order - b.sort_order),
  }))
})

function formatNumber(val: number | string | null): string {
  if (val === null || val === '' || val === undefined) return ''
  const n = Number(val)
  if (isNaN(n)) return String(val)
  return n.toLocaleString('fr-FR')
}

function levelClass(level: number): string {
  if (level === 1) return 'font-bold bg-gray-50 dark:bg-gray-800/50'
  if (level === 2) return 'font-semibold pl-4'
  return 'pl-8'
}
</script>

<template>
  <div class="overflow-x-auto">
    <div v-for="section in sections" :key="section.key" class="mb-8">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3 border-b border-gray-200 dark:border-gray-700 pb-2">
        {{ section.name }}
      </h3>

      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-300 dark:border-gray-600">
            <th class="text-left py-2 px-2 text-gray-700 dark:text-gray-300 w-12">Code</th>
            <th class="text-left py-2 px-2 text-gray-700 dark:text-gray-300 min-w-[200px]">Intitule</th>
            <th
              v-for="col in columns"
              :key="col.code"
              class="text-right py-2 px-2 text-gray-700 dark:text-gray-300 min-w-[120px]"
            >
              {{ col.name }}
              <span v-if="col.computed" class="text-xs text-blue-500 dark:text-blue-400 ml-1">(calc)</span>
            </th>
            <th class="w-8"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="line in section.lines"
            :key="line.id"
            class="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30"
            :class="levelClass(line.level)"
          >
            <td class="py-1.5 px-2 text-gray-500 dark:text-gray-400 font-mono text-xs">
              {{ line.compte_code }}
            </td>
            <td class="py-1.5 px-2 text-gray-900 dark:text-white">
              {{ line.intitule }}
            </td>
            <td
              v-for="col in columns"
              :key="col.code"
              class="py-1.5 px-2 text-right"
            >
              <input
                v-if="isEditable(line.id, col)"
                type="number"
                :value="localValues[line.id]?.[col.code] ?? values[line.id]?.[col.code] ?? ''"
                class="w-full text-right px-1 py-0.5 border border-gray-200 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                @input="onCellInput(line.id, col.code, $event)"
                @blur="onCellBlur(line.id)"
              />
              <span v-else class="text-gray-700 dark:text-gray-300">
                {{ formatNumber(getLineValue(line.id, col.code)) }}
              </span>
            </td>
            <td class="py-1.5 px-1">
              <span
                v-if="lineStatus[line.id] === 'pending'"
                class="inline-block w-2 h-2 rounded-full bg-yellow-400 animate-pulse"
                title="Sauvegarde en cours..."
              />
              <span
                v-else-if="lineStatus[line.id] === 'success'"
                class="inline-block w-2 h-2 rounded-full bg-green-500"
                title="Sauvegarde"
              />
              <span
                v-else-if="lineStatus[line.id] === 'error'"
                class="inline-block w-2 h-2 rounded-full bg-red-500 cursor-pointer"
                title="Erreur - cliquer pour reessayer"
                @click="onCellBlur(line.id)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

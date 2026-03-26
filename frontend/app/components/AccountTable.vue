<script setup lang="ts">
import type { PublicLineData, PublicTemplateColumn, PublicSection } from '../../../../packages/shared/types/public'

const props = defineProps<{
  sections: PublicSection[]
  columns: PublicTemplateColumn[]
}>()

const expandedRows = ref<Set<string>>(new Set())

function toggleRow(code: string) {
  if (expandedRows.value.has(code)) {
    expandedRows.value.delete(code)
  } else {
    expandedRows.value.add(code)
  }
}

function isExpanded(code: string): boolean {
  return expandedRows.value.has(code)
}

function formatNumber(val: number | null | undefined): string {
  if (val === null || val === undefined) return '-'
  if (typeof val !== 'number') return '-'
  return new Intl.NumberFormat('fr-FR').format(val)
}

function formatPercent(val: number | null | undefined): string {
  if (val === null || val === undefined) return '-'
  return (val * 100).toFixed(1) + ' %'
}

function getDisplayValue(line: PublicLineData, col: PublicTemplateColumn): string {
  if (col.code === 'taux_execution') {
    return formatPercent(line.computed?.taux_execution ?? line.values?.taux_execution)
  }
  const computed = line.computed?.[col.code]
  if (computed !== undefined && computed !== null) return formatNumber(computed)
  const raw = line.values?.[col.code]
  if (raw !== undefined && raw !== null) return formatNumber(raw)
  return '-'
}

function sectionLabel(section: string): string {
  return section === 'fonctionnement' ? 'FONCTIONNEMENT' : 'INVESTISSEMENT'
}
</script>

<template>
  <div class="overflow-x-auto relative">
    <!-- Scroll indicator on mobile -->
    <div class="md:hidden text-xs text-(--text-muted) text-right mb-1 flex items-center justify-end gap-1">
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>
      Faire defiler
    </div>

    <table class="w-full text-sm border-collapse min-w-[700px]">
      <thead>
        <tr class="bg-(--interactive-hover)">
          <th class="text-left px-3 py-2 border border-(--border-default) text-(--text-secondary) font-semibold sticky left-0 bg-(--interactive-hover) z-10 min-w-[200px]">
            Intitule
          </th>
          <th
            v-for="col in columns"
            :key="col.code"
            class="text-right px-3 py-2 border border-(--border-default) text-(--text-secondary) font-semibold whitespace-nowrap"
          >
            {{ col.name }}
          </th>
        </tr>
      </thead>
      <tbody>
        <template v-for="section in sections" :key="section.section">
          <!-- Section header -->
          <tr class="bg-(--interactive-selected)">
            <td
              :colspan="columns.length + 1"
              class="px-3 py-2 border border-(--border-default) font-bold text-(--color-primary) text-sm uppercase tracking-wide"
            >
              {{ sectionLabel(section.section) }}
            </td>
          </tr>

          <!-- Level 1 lines -->
          <template v-for="line in section.lines" :key="line.compte_code">
            <!-- Niv1 row -->
            <tr
              class="bg-(--interactive-hover) hover:bg-(--interactive-active) cursor-pointer transition-colors"
              @click="toggleRow(line.compte_code)"
            >
              <td class="px-3 py-2 border border-(--border-default) font-semibold text-(--text-primary) sticky left-0 bg-(--bg-card) z-10">
                <div class="flex items-center gap-2">
                  <svg
                    class="w-4 h-4 text-(--text-muted) transition-transform flex-shrink-0"
                    :class="{ 'rotate-90': isExpanded(line.compte_code) }"
                    fill="none" viewBox="0 0 24 24" stroke="currentColor"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                  <span>{{ line.compte_code }} - {{ line.intitule }}</span>
                </div>
              </td>
              <td
                v-for="col in columns"
                :key="col.code"
                class="text-right px-3 py-2 border border-(--border-default) font-semibold text-(--text-primary) whitespace-nowrap"
              >
                {{ getDisplayValue(line, col) }}
              </td>
            </tr>

            <!-- Niv2 children (shown when niv1 expanded) -->
            <template v-if="isExpanded(line.compte_code)">
              <template v-for="child2 in line.children" :key="child2.compte_code">
                <tr
                  class="hover:bg-(--interactive-hover) cursor-pointer transition-colors"
                  @click="toggleRow(child2.compte_code)"
                >
                  <td class="px-3 py-1.5 border border-(--border-default) text-(--text-primary) sticky left-0 bg-(--bg-card) z-10">
                    <div class="flex items-center gap-2 pl-6">
                      <svg
                        v-if="child2.children && child2.children.length > 0"
                        class="w-3 h-3 text-(--text-muted) transition-transform flex-shrink-0"
                        :class="{ 'rotate-90': isExpanded(child2.compte_code) }"
                        fill="none" viewBox="0 0 24 24" stroke="currentColor"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                      <span class="font-medium">{{ child2.compte_code }} - {{ child2.intitule }}</span>
                    </div>
                  </td>
                  <td
                    v-for="col in columns"
                    :key="col.code"
                    class="text-right px-3 py-1.5 border border-(--border-default) text-(--text-secondary) whitespace-nowrap"
                  >
                    {{ getDisplayValue(child2, col) }}
                  </td>
                </tr>

                <!-- Niv3 children (shown when niv2 expanded) -->
                <template v-if="isExpanded(child2.compte_code) && child2.children">
                  <tr
                    v-for="child3 in child2.children"
                    :key="child3.compte_code"
                    class="hover:bg-(--interactive-hover) transition-colors"
                  >
                    <td class="px-3 py-1 border border-(--border-default) text-(--text-muted) sticky left-0 bg-(--bg-card) z-10">
                      <div class="pl-12">
                        {{ child3.compte_code }} - {{ child3.intitule }}
                      </div>
                    </td>
                    <td
                      v-for="col in columns"
                      :key="col.code"
                      class="text-right px-3 py-1 border border-(--border-default) text-(--text-muted) whitespace-nowrap"
                    >
                      {{ getDisplayValue(child3, col) }}
                    </td>
                  </tr>
                </template>
              </template>
            </template>
          </template>
        </template>
      </tbody>
    </table>
  </div>
</template>

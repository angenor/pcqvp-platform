<script setup lang="ts">
import type { PublicCompteResponse } from '../../../../packages/shared/types/public'

const props = defineProps<{
  recapRecettes: PublicCompteResponse['recapitulatifs']['recettes']
  recapDepenses: PublicCompteResponse['recapitulatifs']['depenses']
}>()

function formatNumber(val: number | null | undefined): string {
  if (val === null || val === undefined) return '-'
  return new Intl.NumberFormat('fr-FR').format(val)
}

function sectionLabel(section: string): string {
  return section === 'fonctionnement' ? 'FONCTIONNEMENT' : 'INVESTISSEMENT'
}
</script>

<template>
  <div class="space-y-8">
    <!-- Recap Recettes -->
    <div>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Recapitulatif des recettes</h3>
      <div class="overflow-x-auto">
        <div class="md:hidden text-xs text-gray-400 dark:text-gray-500 text-right mb-1 flex items-center justify-end gap-1">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          Faire defiler
        </div>
        <table class="w-full text-sm border-collapse min-w-[600px]">
          <thead>
            <tr class="bg-gray-100 dark:bg-gray-700">
              <th class="text-left px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold min-w-[200px]">Categorie</th>
              <th class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold">Previsions definitives</th>
              <th class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold">OR admis</th>
              <th class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold">Recouvrement</th>
              <th class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold">Reste a recouvrer</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="section in recapRecettes.sections" :key="section.section">
              <!-- Section header -->
              <tr class="bg-blue-50 dark:bg-blue-900/20">
                <td colspan="5" class="px-3 py-2 border border-gray-200 dark:border-gray-600 font-bold text-blue-800 dark:text-blue-300 text-sm uppercase tracking-wide">
                  {{ sectionLabel(section.section) }}
                </td>
              </tr>
              <!-- Categories -->
              <tr v-for="cat in section.categories" :key="cat.compte_code" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <td class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-800 dark:text-gray-200">
                  {{ cat.compte_code }} - {{ cat.intitule }}
                </td>
                <td class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300">{{ formatNumber(cat.previsions_definitives) }}</td>
                <td class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300">{{ formatNumber(cat.or_admis) }}</td>
                <td class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300">{{ formatNumber(cat.recouvrement) }}</td>
                <td class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300">{{ formatNumber(cat.reste_a_recouvrer) }}</td>
              </tr>
              <!-- Total section -->
              <tr class="bg-gray-50 dark:bg-gray-750 font-semibold">
                <td class="px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">
                  Total {{ section.section }}
                </td>
                <td class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">{{ formatNumber(section.total_section?.previsions_definitives) }}</td>
                <td class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">{{ formatNumber(section.total_section?.or_admis) }}</td>
                <td class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">{{ formatNumber(section.total_section?.recouvrement) }}</td>
                <td class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">{{ formatNumber(section.total_section?.reste_a_recouvrer) }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Recap Depenses -->
    <div>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Recapitulatif des depenses</h3>
      <div class="overflow-x-auto">
        <div class="md:hidden text-xs text-gray-400 dark:text-gray-500 text-right mb-1 flex items-center justify-end gap-1">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          Faire defiler
        </div>
        <table class="w-full text-sm border-collapse min-w-[600px]">
          <thead>
            <tr class="bg-gray-100 dark:bg-gray-700">
              <th class="text-left px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold min-w-[200px]">Categorie</th>
              <th
                v-for="prog in recapDepenses.programmes"
                :key="prog.id"
                class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold whitespace-nowrap"
              >
                Prog. {{ prog.numero }}
              </th>
              <th class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold">Total</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="section in recapDepenses.sections" :key="section.section">
              <tr class="bg-blue-50 dark:bg-blue-900/20">
                <td :colspan="(recapDepenses.programmes?.length || 0) + 2" class="px-3 py-2 border border-gray-200 dark:border-gray-600 font-bold text-blue-800 dark:text-blue-300 text-sm uppercase tracking-wide">
                  {{ sectionLabel(section.section) }}
                </td>
              </tr>

              <!-- Mandat admis row per category -->
              <template v-for="cat in section.categories" :key="cat.compte_code">
                <tr class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-800 dark:text-gray-200">
                    {{ cat.compte_code }} - {{ cat.intitule }}
                  </td>
                  <td
                    v-for="prog in cat.programmes"
                    :key="prog.programme_id"
                    class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300"
                  >
                    {{ formatNumber(prog.mandat_admis) }}
                  </td>
                  <td class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 font-semibold text-gray-900 dark:text-white">
                    {{ formatNumber(cat.total?.mandat_admis) }}
                  </td>
                </tr>
              </template>

              <!-- Total section -->
              <tr class="bg-gray-50 dark:bg-gray-750 font-semibold">
                <td class="px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">
                  Total {{ section.section }}
                </td>
                <td
                  v-for="(_prog, idx) in recapDepenses.programmes"
                  :key="idx"
                  class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white"
                >
                  -
                </td>
                <td class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">
                  {{ formatNumber(section.total_section?.mandat_admis) }}
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

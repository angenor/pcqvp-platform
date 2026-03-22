<script setup lang="ts">
import type { PublicCompteResponse } from '../../../../packages/shared/types/public'

const props = defineProps<{
  equilibre: PublicCompteResponse['equilibre']
}>()

function formatNumber(val: number | null | undefined): string {
  if (val === null || val === undefined) return '-'
  return new Intl.NumberFormat('fr-FR').format(val)
}

function sectionLabel(section: string): string {
  return section === 'fonctionnement' ? 'Fonctionnement' : 'Investissement'
}

const sections = computed(() => [
  { key: 'fonctionnement', data: props.equilibre.fonctionnement },
  { key: 'investissement', data: props.equilibre.investissement },
])
</script>

<template>
  <div class="space-y-8">
    <template v-for="section in sections" :key="section.key">
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          {{ sectionLabel(section.key) }}
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Depenses -->
          <div>
            <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase">Depenses</h4>
            <div class="overflow-x-auto">
              <table class="w-full text-sm border-collapse">
                <thead>
                  <tr class="bg-red-50 dark:bg-red-900/20">
                    <th class="text-left px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold">Categorie</th>
                    <th class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold">Montant</th>
                  </tr>
                </thead>
                <tbody>
                  <!-- Operations reelles -->
                  <tr class="bg-gray-50 dark:bg-gray-800/50">
                    <td colspan="2" class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                      Operations reelles
                    </td>
                  </tr>
                  <tr v-for="item in section.data.depenses.reelles" :key="item.compte_code" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-800 dark:text-gray-200">{{ item.intitule }}</td>
                    <td class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300">{{ formatNumber(item.montant) }}</td>
                  </tr>
                  <tr class="font-semibold bg-gray-50 dark:bg-gray-800/50">
                    <td class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">Sous-total reelles</td>
                    <td class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">{{ formatNumber(section.data.depenses.total_reelles) }}</td>
                  </tr>

                  <!-- Operations d'ordre -->
                  <tr v-if="section.data.depenses.ordre.length > 0" class="bg-gray-50 dark:bg-gray-800/50">
                    <td colspan="2" class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                      Operations d'ordre
                    </td>
                  </tr>
                  <tr v-for="item in section.data.depenses.ordre" :key="item.compte_code" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-800 dark:text-gray-200">{{ item.intitule }}</td>
                    <td class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300">{{ formatNumber(item.montant) }}</td>
                  </tr>

                  <!-- Total -->
                  <tr class="font-bold bg-red-50 dark:bg-red-900/20">
                    <td class="px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">Total depenses</td>
                    <td class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">{{ formatNumber(section.data.depenses.total) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Recettes -->
          <div>
            <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase">Recettes</h4>
            <div class="overflow-x-auto">
              <table class="w-full text-sm border-collapse">
                <thead>
                  <tr class="bg-green-50 dark:bg-green-900/20">
                    <th class="text-left px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold">Categorie</th>
                    <th class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold">Montant</th>
                  </tr>
                </thead>
                <tbody>
                  <!-- Operations reelles -->
                  <tr class="bg-gray-50 dark:bg-gray-800/50">
                    <td colspan="2" class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                      Operations reelles
                    </td>
                  </tr>
                  <tr v-for="item in section.data.recettes.reelles" :key="item.compte_code" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-800 dark:text-gray-200">{{ item.intitule }}</td>
                    <td class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300">{{ formatNumber(item.montant) }}</td>
                  </tr>
                  <tr class="font-semibold bg-gray-50 dark:bg-gray-800/50">
                    <td class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">Sous-total reelles</td>
                    <td class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">{{ formatNumber(section.data.recettes.total_reelles) }}</td>
                  </tr>

                  <!-- Operations d'ordre -->
                  <tr v-if="section.data.recettes.ordre.length > 0" class="bg-gray-50 dark:bg-gray-800/50">
                    <td colspan="2" class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                      Operations d'ordre
                    </td>
                  </tr>
                  <tr v-for="item in section.data.recettes.ordre" :key="item.compte_code" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td class="px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-800 dark:text-gray-200">{{ item.intitule }}</td>
                    <td class="text-right px-3 py-1.5 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300">{{ formatNumber(item.montant) }}</td>
                  </tr>

                  <!-- Total -->
                  <tr class="font-bold bg-green-50 dark:bg-green-900/20">
                    <td class="px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">Total recettes</td>
                    <td class="text-right px-3 py-2 border border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white">{{ formatNumber(section.data.recettes.total) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Excedent/Deficit -->
        <div class="mt-4 p-4 rounded-lg" :class="section.data.excedent >= 0 ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-gray-900 dark:text-white">
              {{ section.data.excedent >= 0 ? 'Excedent' : 'Deficit' }} de {{ sectionLabel(section.key) }}
            </span>
            <span class="font-bold text-lg" :class="section.data.excedent >= 0 ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'">
              {{ formatNumber(Math.abs(section.data.excedent)) }}
            </span>
          </div>
        </div>
      </div>
    </template>

    <!-- Resultat definitif -->
    <div class="p-6 rounded-lg border-2" :class="equilibre.resultat_definitif >= 0 ? 'border-green-500 bg-green-50 dark:bg-green-900/20' : 'border-red-500 bg-red-50 dark:bg-red-900/20'">
      <div class="flex items-center justify-between">
        <span class="text-lg font-bold text-gray-900 dark:text-white">
          Resultat definitif
        </span>
        <span class="text-2xl font-bold" :class="equilibre.resultat_definitif >= 0 ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'">
          {{ equilibre.resultat_definitif >= 0 ? '+' : '' }}{{ formatNumber(equilibre.resultat_definitif) }}
        </span>
      </div>
    </div>
  </div>
</template>

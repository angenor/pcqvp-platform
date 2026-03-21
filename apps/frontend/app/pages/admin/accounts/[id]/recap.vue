<script setup lang="ts">
import type { CompteDetail, RecapRecettesResponse, RecapDepensesResponse, EquilibreResponse } from '~/types/comptes'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const compteId = route.params.id as string

const { fetchCompte, fetchRecapRecettes, fetchRecapDepenses, fetchEquilibre } = useComptes()

const compte = ref<CompteDetail | null>(null)
const recapRecettes = ref<RecapRecettesResponse | null>(null)
const recapDepenses = ref<RecapDepensesResponse | null>(null)
const equilibre = ref<EquilibreResponse | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const [compteData, recR, recD, eq] = await Promise.all([
      fetchCompte(compteId),
      fetchRecapRecettes(compteId),
      fetchRecapDepenses(compteId),
      fetchEquilibre(compteId),
    ])
    compte.value = compteData
    recapRecettes.value = recR
    recapDepenses.value = recD
    equilibre.value = eq
  } catch {
    error.value = 'Erreur lors du chargement'
  } finally {
    loading.value = false
  }
})

function fmt(val: number | null | undefined): string {
  if (val === null || val === undefined) return '-'
  return Number(val).toLocaleString('fr-FR')
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Recapitulatifs</h1>
        <p v-if="compte" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ compte.collectivite_name }} - {{ compte.annee_exercice }}
        </p>
      </div>
      <div class="flex items-center gap-3">
        <NuxtLink
          :to="`/admin/accounts/${compteId}/recettes`"
          class="text-sm px-3 py-1.5 rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          Recettes
        </NuxtLink>
        <NuxtLink
          :to="`/admin/accounts/${compteId}/depenses`"
          class="text-sm px-3 py-1.5 rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          Depenses
        </NuxtLink>
        <NuxtLink
          to="/admin/accounts"
          class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
        >
          Liste
        </NuxtLink>
      </div>
    </div>

    <div v-if="error" class="mb-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-md text-sm">
      {{ error }}
    </div>

    <div v-if="loading" class="flex items-center justify-center py-16">
      <span class="text-gray-600 dark:text-gray-400">Chargement...</span>
    </div>

    <div v-else class="space-y-8">
      <!-- Recap Recettes -->
      <div v-if="recapRecettes" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recapitulatif des recettes</h2>
        <div v-for="section in recapRecettes.sections" :key="section.section" class="mb-6">
          <h3 class="text-md font-medium text-gray-700 dark:text-gray-300 mb-2 capitalize">{{ section.section }}</h3>
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-300 dark:border-gray-600">
                <th class="text-left py-2 px-2 text-gray-700 dark:text-gray-300">Compte</th>
                <th class="text-left py-2 px-2 text-gray-700 dark:text-gray-300">Intitule</th>
                <th class="text-right py-2 px-2 text-gray-700 dark:text-gray-300">Prev. definitives</th>
                <th class="text-right py-2 px-2 text-gray-700 dark:text-gray-300">OR admis</th>
                <th class="text-right py-2 px-2 text-gray-700 dark:text-gray-300">Recouvrement</th>
                <th class="text-right py-2 px-2 text-gray-700 dark:text-gray-300">Reste a recouvrer</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="cat in section.categories"
                :key="cat.compte_code"
                class="border-b border-gray-100 dark:border-gray-700/50"
              >
                <td class="py-1.5 px-2 font-mono text-xs text-gray-500 dark:text-gray-400">{{ cat.compte_code }}</td>
                <td class="py-1.5 px-2 text-gray-900 dark:text-white">{{ cat.intitule }}</td>
                <td class="py-1.5 px-2 text-right text-gray-700 dark:text-gray-300">{{ fmt(cat.previsions_definitives) }}</td>
                <td class="py-1.5 px-2 text-right text-gray-700 dark:text-gray-300">{{ fmt(cat.or_admis) }}</td>
                <td class="py-1.5 px-2 text-right text-gray-700 dark:text-gray-300">{{ fmt(cat.recouvrement) }}</td>
                <td class="py-1.5 px-2 text-right text-gray-700 dark:text-gray-300">{{ fmt(cat.reste_a_recouvrer) }}</td>
              </tr>
              <tr class="font-bold border-t border-gray-300 dark:border-gray-600">
                <td colspan="2" class="py-2 px-2 text-gray-900 dark:text-white">Total {{ section.section }}</td>
                <td class="py-2 px-2 text-right text-gray-900 dark:text-white">{{ fmt(section.total_section?.previsions_definitives) }}</td>
                <td class="py-2 px-2 text-right text-gray-900 dark:text-white">{{ fmt(section.total_section?.or_admis) }}</td>
                <td class="py-2 px-2 text-right text-gray-900 dark:text-white">{{ fmt(section.total_section?.recouvrement) }}</td>
                <td class="py-2 px-2 text-right text-gray-900 dark:text-white">{{ fmt(section.total_section?.reste_a_recouvrer) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Recap Depenses -->
      <div v-if="recapDepenses" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recapitulatif des depenses</h2>
        <div v-for="section in recapDepenses.sections" :key="section.section" class="mb-6">
          <h3 class="text-md font-medium text-gray-700 dark:text-gray-300 mb-2 capitalize">{{ section.section }}</h3>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-300 dark:border-gray-600">
                  <th class="text-left py-2 px-2 text-gray-700 dark:text-gray-300">Compte</th>
                  <th class="text-left py-2 px-2 text-gray-700 dark:text-gray-300">Intitule</th>
                  <th
                    v-for="prog in recapDepenses.programmes"
                    :key="prog.id"
                    class="text-right py-2 px-2 text-gray-700 dark:text-gray-300"
                  >
                    P{{ prog.numero }}
                  </th>
                  <th class="text-right py-2 px-2 text-gray-700 dark:text-gray-300 font-bold">Total</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="cat in section.categories"
                  :key="cat.compte_code"
                  class="border-b border-gray-100 dark:border-gray-700/50"
                >
                  <td class="py-1.5 px-2 font-mono text-xs text-gray-500 dark:text-gray-400">{{ cat.compte_code }}</td>
                  <td class="py-1.5 px-2 text-gray-900 dark:text-white">{{ cat.intitule }}</td>
                  <td
                    v-for="prog in cat.programmes"
                    :key="prog.programme_id"
                    class="py-1.5 px-2 text-right text-gray-700 dark:text-gray-300"
                  >
                    {{ fmt(prog.mandat_admis) }}
                  </td>
                  <td class="py-1.5 px-2 text-right font-semibold text-gray-900 dark:text-white">
                    {{ fmt(cat.total?.mandat_admis) }}
                  </td>
                </tr>
                <tr class="font-bold border-t border-gray-300 dark:border-gray-600">
                  <td colspan="2" class="py-2 px-2 text-gray-900 dark:text-white">Total {{ section.section }}</td>
                  <td
                    v-for="(_p, idx) in recapDepenses.programmes"
                    :key="idx"
                    class="py-2 px-2 text-right text-gray-900 dark:text-white"
                  >
                    -
                  </td>
                  <td class="py-2 px-2 text-right text-gray-900 dark:text-white">
                    {{ fmt(section.total_section?.mandat_admis) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Equilibre -->
      <div v-if="equilibre" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Equilibre</h2>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Fonctionnement -->
          <div>
            <h3 class="text-md font-medium text-gray-700 dark:text-gray-300 mb-3">Fonctionnement</h3>
            <div class="space-y-4">
              <div>
                <h4 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1">Depenses</h4>
                <div v-for="item in equilibre.fonctionnement.depenses.reelles" :key="item.compte_code" class="flex justify-between text-sm py-0.5">
                  <span class="text-gray-700 dark:text-gray-300">{{ item.intitule }}</span>
                  <span class="text-gray-900 dark:text-white">{{ fmt(item.montant) }}</span>
                </div>
                <div class="flex justify-between font-semibold text-sm border-t border-gray-200 dark:border-gray-700 pt-1 mt-1">
                  <span class="text-gray-900 dark:text-white">Total depenses</span>
                  <span class="text-gray-900 dark:text-white">{{ fmt(equilibre.fonctionnement.depenses.total) }}</span>
                </div>
              </div>
              <div>
                <h4 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1">Recettes</h4>
                <div v-for="item in equilibre.fonctionnement.recettes.reelles" :key="item.compte_code" class="flex justify-between text-sm py-0.5">
                  <span class="text-gray-700 dark:text-gray-300">{{ item.intitule }}</span>
                  <span class="text-gray-900 dark:text-white">{{ fmt(item.montant) }}</span>
                </div>
                <div class="flex justify-between font-semibold text-sm border-t border-gray-200 dark:border-gray-700 pt-1 mt-1">
                  <span class="text-gray-900 dark:text-white">Total recettes</span>
                  <span class="text-gray-900 dark:text-white">{{ fmt(equilibre.fonctionnement.recettes.total) }}</span>
                </div>
              </div>
              <div class="flex justify-between font-bold text-sm border-t-2 border-gray-300 dark:border-gray-600 pt-2">
                <span :class="equilibre.fonctionnement.excedent >= 0 ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'">
                  {{ equilibre.fonctionnement.excedent >= 0 ? 'Excedent' : 'Deficit' }}
                </span>
                <span :class="equilibre.fonctionnement.excedent >= 0 ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'">
                  {{ fmt(Math.abs(equilibre.fonctionnement.excedent)) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Investissement -->
          <div>
            <h3 class="text-md font-medium text-gray-700 dark:text-gray-300 mb-3">Investissement</h3>
            <div class="space-y-4">
              <div>
                <h4 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1">Depenses</h4>
                <div v-for="item in equilibre.investissement.depenses.reelles" :key="item.compte_code" class="flex justify-between text-sm py-0.5">
                  <span class="text-gray-700 dark:text-gray-300">{{ item.intitule }}</span>
                  <span class="text-gray-900 dark:text-white">{{ fmt(item.montant) }}</span>
                </div>
                <div class="flex justify-between font-semibold text-sm border-t border-gray-200 dark:border-gray-700 pt-1 mt-1">
                  <span class="text-gray-900 dark:text-white">Total depenses</span>
                  <span class="text-gray-900 dark:text-white">{{ fmt(equilibre.investissement.depenses.total) }}</span>
                </div>
              </div>
              <div>
                <h4 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1">Recettes</h4>
                <div v-for="item in equilibre.investissement.recettes.reelles" :key="item.compte_code" class="flex justify-between text-sm py-0.5">
                  <span class="text-gray-700 dark:text-gray-300">{{ item.intitule }}</span>
                  <span class="text-gray-900 dark:text-white">{{ fmt(item.montant) }}</span>
                </div>
                <div class="flex justify-between font-semibold text-sm border-t border-gray-200 dark:border-gray-700 pt-1 mt-1">
                  <span class="text-gray-900 dark:text-white">Total recettes</span>
                  <span class="text-gray-900 dark:text-white">{{ fmt(equilibre.investissement.recettes.total) }}</span>
                </div>
              </div>
              <div class="flex justify-between font-bold text-sm border-t-2 border-gray-300 dark:border-gray-600 pt-2">
                <span :class="equilibre.investissement.excedent >= 0 ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'">
                  {{ equilibre.investissement.excedent >= 0 ? 'Excedent' : 'Deficit' }}
                </span>
                <span :class="equilibre.investissement.excedent >= 0 ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'">
                  {{ fmt(Math.abs(equilibre.investissement.excedent)) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Resultat definitif -->
        <div class="mt-6 p-4 rounded-lg border-2" :class="equilibre.resultat_definitif >= 0
          ? 'border-green-300 dark:border-green-700 bg-green-50 dark:bg-green-900/20'
          : 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20'"
        >
          <div class="flex justify-between items-center">
            <span class="text-lg font-bold text-gray-900 dark:text-white">Resultat definitif</span>
            <span class="text-lg font-bold" :class="equilibre.resultat_definitif >= 0
              ? 'text-green-700 dark:text-green-400'
              : 'text-red-700 dark:text-red-400'"
            >
              {{ fmt(equilibre.resultat_definitif) }} Ar
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

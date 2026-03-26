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
      <h3 class="text-lg font-semibold text-(--text-primary) mb-3">Recapitulatif des recettes</h3>
      <div class="overflow-x-auto">
        <div class="md:hidden text-xs text-(--text-muted) text-right mb-1 flex items-center justify-end gap-1">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          Faire defiler
        </div>
        <table class="w-full text-sm border-collapse min-w-[600px]">
          <thead>
            <tr class="bg-(--interactive-hover)">
              <th class="text-left px-3 py-2 border border-(--border-default) text-(--text-secondary) font-semibold min-w-[200px]">Categorie</th>
              <th class="text-right px-3 py-2 border border-(--border-default) text-(--text-secondary) font-semibold">Previsions definitives</th>
              <th class="text-right px-3 py-2 border border-(--border-default) text-(--text-secondary) font-semibold">OR admis</th>
              <th class="text-right px-3 py-2 border border-(--border-default) text-(--text-secondary) font-semibold">Recouvrement</th>
              <th class="text-right px-3 py-2 border border-(--border-default) text-(--text-secondary) font-semibold">Reste a recouvrer</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="section in recapRecettes.sections" :key="section.section">
              <!-- Section header -->
              <tr class="bg-(--interactive-selected)">
                <td colspan="5" class="px-3 py-2 border border-(--border-default) font-bold text-(--color-primary) text-sm uppercase tracking-wide">
                  {{ sectionLabel(section.section) }}
                </td>
              </tr>
              <!-- Categories -->
              <tr v-for="cat in section.categories" :key="cat.compte_code" class="hover:bg-(--interactive-hover)">
                <td class="px-3 py-1.5 border border-(--border-default) text-(--text-primary)">
                  {{ cat.compte_code }} - {{ cat.intitule }}
                </td>
                <td class="text-right px-3 py-1.5 border border-(--border-default) text-(--text-secondary)">{{ formatNumber(cat.previsions_definitives) }}</td>
                <td class="text-right px-3 py-1.5 border border-(--border-default) text-(--text-secondary)">{{ formatNumber(cat.or_admis) }}</td>
                <td class="text-right px-3 py-1.5 border border-(--border-default) text-(--text-secondary)">{{ formatNumber(cat.recouvrement) }}</td>
                <td class="text-right px-3 py-1.5 border border-(--border-default) text-(--text-secondary)">{{ formatNumber(cat.reste_a_recouvrer) }}</td>
              </tr>
              <!-- Total section -->
              <tr class="bg-(--interactive-hover) font-semibold">
                <td class="px-3 py-2 border border-(--border-default) text-(--text-primary)">
                  Total {{ section.section }}
                </td>
                <td class="text-right px-3 py-2 border border-(--border-default) text-(--text-primary)">{{ formatNumber(section.total_section?.previsions_definitives) }}</td>
                <td class="text-right px-3 py-2 border border-(--border-default) text-(--text-primary)">{{ formatNumber(section.total_section?.or_admis) }}</td>
                <td class="text-right px-3 py-2 border border-(--border-default) text-(--text-primary)">{{ formatNumber(section.total_section?.recouvrement) }}</td>
                <td class="text-right px-3 py-2 border border-(--border-default) text-(--text-primary)">{{ formatNumber(section.total_section?.reste_a_recouvrer) }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Recap Depenses -->
    <div>
      <h3 class="text-lg font-semibold text-(--text-primary) mb-3">Recapitulatif des depenses</h3>
      <div class="overflow-x-auto">
        <div class="md:hidden text-xs text-(--text-muted) text-right mb-1 flex items-center justify-end gap-1">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          Faire defiler
        </div>
        <table class="w-full text-sm border-collapse min-w-[600px]">
          <thead>
            <tr class="bg-(--interactive-hover)">
              <th class="text-left px-3 py-2 border border-(--border-default) text-(--text-secondary) font-semibold min-w-[200px]">Categorie</th>
              <th
                v-for="prog in recapDepenses.programmes"
                :key="prog.id"
                class="text-right px-3 py-2 border border-(--border-default) text-(--text-secondary) font-semibold whitespace-nowrap"
              >
                Prog. {{ prog.numero }}
              </th>
              <th class="text-right px-3 py-2 border border-(--border-default) text-(--text-secondary) font-semibold">Total</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="section in recapDepenses.sections" :key="section.section">
              <tr class="bg-(--interactive-selected)">
                <td :colspan="(recapDepenses.programmes?.length || 0) + 2" class="px-3 py-2 border border-(--border-default) font-bold text-(--color-primary) text-sm uppercase tracking-wide">
                  {{ sectionLabel(section.section) }}
                </td>
              </tr>

              <!-- Mandat admis row per category -->
              <template v-for="cat in section.categories" :key="cat.compte_code">
                <tr class="hover:bg-(--interactive-hover)">
                  <td class="px-3 py-1.5 border border-(--border-default) text-(--text-primary)">
                    {{ cat.compte_code }} - {{ cat.intitule }}
                  </td>
                  <td
                    v-for="prog in cat.programmes"
                    :key="prog.programme_id"
                    class="text-right px-3 py-1.5 border border-(--border-default) text-(--text-secondary)"
                  >
                    {{ formatNumber(prog.mandat_admis) }}
                  </td>
                  <td class="text-right px-3 py-1.5 border border-(--border-default) font-semibold text-(--text-primary)">
                    {{ formatNumber(cat.total?.mandat_admis) }}
                  </td>
                </tr>
              </template>

              <!-- Total section -->
              <tr class="bg-(--interactive-hover) font-semibold">
                <td class="px-3 py-2 border border-(--border-default) text-(--text-primary)">
                  Total {{ section.section }}
                </td>
                <td
                  v-for="(_prog, idx) in recapDepenses.programmes"
                  :key="idx"
                  class="text-right px-3 py-2 border border-(--border-default) text-(--text-primary)"
                >
                  -
                </td>
                <td class="text-right px-3 py-2 border border-(--border-default) text-(--text-primary)">
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

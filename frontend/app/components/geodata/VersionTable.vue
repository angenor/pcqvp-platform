<script setup lang="ts">
import type { GeodataVersionListItem } from '~/types/geodata'

interface Props {
  items: GeodataVersionListItem[]
  total: number
  limit: number
  offset: number
  loading?: boolean
}
const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'preview', v: GeodataVersionListItem): void
  (e: 'activate', v: GeodataVersionListItem): void
  (e: 'delete', v: GeodataVersionListItem): void
  (e: 'page', offset: number): void
}>()

const fmtDate = (s: string) => new Date(s).toLocaleString('fr-FR')
const fmtKb = (n: number) => `${Math.round(n / 1024)} Ko`

const hasNext = computed(() => props.offset + props.limit < props.total)
const hasPrev = computed(() => props.offset > 0)
</script>

<template>
  <div class="overflow-x-auto">
    <table class="min-w-full text-sm">
      <thead class="bg-gray-100 text-left dark:bg-gray-800">
        <tr>
          <th class="px-3 py-2">Date</th>
          <th class="px-3 py-2">Auteur</th>
          <th class="px-3 py-2">Fichier</th>
          <th class="px-3 py-2">Taille</th>
          <th class="px-3 py-2">Régions</th>
          <th class="px-3 py-2">Statut</th>
          <th class="px-3 py-2">Avert.</th>
          <th class="px-3 py-2 text-right">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="v in items"
          :key="v.id"
          class="border-t border-gray-200 dark:border-gray-700"
        >
          <td class="px-3 py-2 text-gray-700 dark:text-gray-300">
            {{ fmtDate(v.created_at) }}
          </td>
          <td class="px-3 py-2 text-gray-700 dark:text-gray-300">
            {{ v.created_by.email }}
          </td>
          <td class="px-3 py-2 text-gray-700 dark:text-gray-300">
            {{ v.original_filename }}
          </td>
          <td class="px-3 py-2 text-gray-700 dark:text-gray-300">
            {{ fmtKb(v.processed_size_bytes) }}
          </td>
          <td class="px-3 py-2 text-gray-700 dark:text-gray-300">
            {{ v.features_count }}
          </td>
          <td class="px-3 py-2">
            <span
              v-if="v.is_active"
              class="rounded bg-green-100 px-2 py-1 text-xs font-medium text-green-800 dark:bg-green-900/30 dark:text-green-300"
            >
              Active
            </span>
            <span
              v-else
              class="rounded bg-gray-100 px-2 py-1 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300"
            >
              Inactive
            </span>
          </td>
          <td class="px-3 py-2">
            <span
              v-if="v.has_warnings"
              class="rounded bg-amber-100 px-2 py-1 text-xs text-amber-800 dark:bg-amber-900/30 dark:text-amber-300"
            >
              ⚠
            </span>
            <span v-else class="text-gray-400">—</span>
          </td>
          <td class="px-3 py-2 text-right">
            <div class="inline-flex gap-2">
              <button
                class="text-blue-600 hover:underline"
                @click="emit('preview', v)"
              >
                Prévisualiser
              </button>
              <button
                v-if="!v.is_active"
                class="text-emerald-600 hover:underline"
                @click="emit('activate', v)"
              >
                Activer
              </button>
              <button
                class="text-red-600 hover:underline disabled:cursor-not-allowed disabled:text-gray-400"
                :disabled="v.is_active"
                @click="emit('delete', v)"
              >
                Supprimer
              </button>
            </div>
          </td>
        </tr>
        <tr v-if="!items.length">
          <td colspan="8" class="px-3 py-6 text-center text-gray-500">
            {{ loading ? 'Chargement…' : 'Aucune version' }}
          </td>
        </tr>
      </tbody>
    </table>
    <div class="mt-3 flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
      <span>Total : {{ total }}</span>
      <div class="flex gap-2">
        <button
          class="rounded border px-3 py-1 disabled:opacity-50"
          :disabled="!hasPrev"
          @click="emit('page', Math.max(0, offset - limit))"
        >
          ← Précédent
        </button>
        <button
          class="rounded border px-3 py-1 disabled:opacity-50"
          :disabled="!hasNext"
          @click="emit('page', offset + limit)"
        >
          Suivant →
        </button>
      </div>
    </div>
  </div>
</template>

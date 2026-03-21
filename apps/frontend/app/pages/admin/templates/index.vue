<script setup lang="ts">
import type { TemplateListItem } from '~/types/templates'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { fetchTemplates } = useTemplates()

const templates = ref<TemplateListItem[]>([])
const loading = ref(true)

async function loadTemplates() {
  loading.value = true
  try {
    const data = await fetchTemplates()
    templates.value = data.items
  } catch (e) {
    console.error('Failed to load templates', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadTemplates)

function typeBadgeClass(type: string) {
  return type === 'recette'
    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
    : 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
}

function statusBadgeClass(isActive: boolean) {
  return isActive
    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
    : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Templates de comptes</h1>
    </div>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400">Chargement...</div>

    <div v-else-if="templates.length === 0" class="text-gray-500 dark:text-gray-400">
      Aucun template. Executez le seed pour importer la structure de reference.
    </div>

    <div v-else class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Nom</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Type</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Version</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Statut</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Lignes</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Colonnes</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Date</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="t in templates"
            :key="t.id"
            class="hover:bg-gray-50 dark:hover:bg-gray-700/30 cursor-pointer transition-colors"
            @click="navigateTo(`/admin/templates/${t.id}`)"
          >
            <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">{{ t.name }}</td>
            <td class="px-6 py-4">
              <span class="px-2 py-1 text-xs font-medium rounded-full" :class="typeBadgeClass(t.type)">
                {{ t.type === 'recette' ? 'Recette' : 'Depense' }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">v{{ t.version }}</td>
            <td class="px-6 py-4">
              <span class="px-2 py-1 text-xs font-medium rounded-full" :class="statusBadgeClass(t.is_active)">
                {{ t.is_active ? 'Actif' : 'Inactif' }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ t.lines_count }}</td>
            <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ t.columns_count }}</td>
            <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
              {{ new Date(t.created_at).toLocaleDateString('fr-FR') }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

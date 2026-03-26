<script setup lang="ts">
import type { TemplateListItem } from '~/types/templates'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { fetchTemplates } = useTemplates()

const templates = ref<TemplateListItem[]>([])
const loading = ref(true)

const columns = [
  { key: 'name', label: 'Nom' },
  { key: 'type', label: 'Type' },
  { key: 'version', label: 'Version' },
  { key: 'is_active', label: 'Statut' },
  { key: 'lines_count', label: 'Lignes', align: 'center' as const },
  { key: 'columns_count', label: 'Colonnes', align: 'center' as const },
  { key: 'created_at', label: 'Date' },
]

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
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-(--text-primary)">Templates de comptes</h1>
    </div>

    <UiDataTable
      :columns="columns"
      :data="templates"
      :loading="loading"
      :searchable="false"
      empty-message="Aucun template. Executez le seed pour importer la structure de reference."
      :empty-icon="['fas', 'file-alt']"
    >
      <template #cell-type="{ value }">
        <UiBadge :variant="value === 'recette' ? 'success' : 'warning'">
          {{ value === 'recette' ? 'Recette' : 'Depense' }}
        </UiBadge>
      </template>
      <template #cell-version="{ value }">
        <span class="font-mono text-sm">v{{ value }}</span>
      </template>
      <template #cell-is_active="{ value }">
        <UiBadge :variant="value ? 'info' : 'gray'" dot>
          {{ value ? 'Actif' : 'Inactif' }}
        </UiBadge>
      </template>
      <template #cell-lines_count="{ value }">
        <span class="font-mono">{{ value }}</span>
      </template>
      <template #cell-columns_count="{ value }">
        <span class="font-mono">{{ value }}</span>
      </template>
      <template #cell-created_at="{ value }">
        <span class="font-mono text-sm">{{ new Date(value).toLocaleDateString('fr-FR') }}</span>
      </template>
      <template #actions="{ row }">
        <UiButton variant="ghost" size="sm" :to="`/admin/templates/${row.id}`" :icon="['fas', 'eye']">
          Voir
        </UiButton>
      </template>
    </UiDataTable>
  </div>
</template>

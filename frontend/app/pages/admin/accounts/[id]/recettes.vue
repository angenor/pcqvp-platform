<script setup lang="ts">
import type { TemplateDetail } from '~/types/templates'
import type { CompteDetail } from '~/types/comptes'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const compteId = route.params.id as string

const { fetchCompte, upsertRecetteLine, updateStatus } = useComptes()
const { fetchTemplates, fetchTemplate } = useTemplates()
const { user } = useAuth()

const compte = ref<CompteDetail | null>(null)
const template = ref<TemplateDetail | null>(null)
const loading = ref(true)
const error = ref('')

const dataTable = ref<InstanceType<typeof AccountDataTable> | null>(null)

// Build values map from compte recettes
const valuesMap = computed(() => {
  const map: Record<string, Record<string, number>> = {}
  if (compte.value?.recettes?.lines) {
    for (const line of compte.value.recettes.lines) {
      map[line.template_line_id] = line.values as Record<string, number>
    }
  }
  return map
})

const computedMap = computed(() => {
  const map: Record<string, Record<string, number | null>> = {}
  if (compte.value?.recettes?.lines) {
    for (const line of compte.value.recettes.lines) {
      map[line.template_line_id] = line.computed as Record<string, number | null>
    }
  }
  return map
})

const hierarchicalSums = computed(() => {
  return (compte.value?.recettes?.hierarchical_sums || {}) as Record<string, Record<string, number>>
})

// Column definitions for recettes
const columns = computed(() => {
  if (!template.value) return []
  return template.value.columns
    .sort((a, b) => a.sort_order - b.sort_order)
    .map(col => ({
      code: col.code,
      name: col.name,
      editable: !col.is_computed,
      computed: col.is_computed,
    }))
})

onMounted(async () => {
  try {
    // Load compte and find recette template
    const [compteData, templatesData] = await Promise.all([
      fetchCompte(compteId),
      fetchTemplates(),
    ])
    compte.value = compteData

    const recetteTemplate = templatesData.items.find(t => t.type === 'recette' && t.is_active)
    if (recetteTemplate) {
      template.value = await fetchTemplate(recetteTemplate.id)
    }
  } catch {
    error.value = 'Erreur lors du chargement'
  } finally {
    loading.value = false
  }
})

async function handleSaveLine(templateLineId: string, values: Record<string, number>) {
  dataTable.value?.setLineStatus(templateLineId, 'pending')
  try {
    await upsertRecetteLine(compteId, {
      template_line_id: templateLineId,
      values,
    })
    // Reload to get updated computed values and sums
    compte.value = await fetchCompte(compteId)
    dataTable.value?.setLineStatus(templateLineId, 'success')
    setTimeout(() => dataTable.value?.setLineStatus(templateLineId, 'idle'), 2000)
  } catch {
    dataTable.value?.setLineStatus(templateLineId, 'error')
  }
}

const isAdmin = computed(() => user.value?.role === 'admin')
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-(--text-primary)">
          Recettes
        </h1>
        <p v-if="compte" class="text-sm text-(--text-muted) mt-1">
          {{ compte.collectivite_name }} - {{ compte.annee_exercice }}
          <span
            class="ml-2 px-2 py-0.5 rounded text-xs"
            :class="compte.status === 'published'
              ? 'bg-(--color-success-light) text-(--color-success)'
              : 'bg-(--color-warning-light) text-(--color-warning)'"
          >
            {{ compte.status === 'published' ? 'Publie' : 'Brouillon' }}
          </span>
        </p>
      </div>
      <div class="flex items-center gap-3">
        <NuxtLink
          :to="`/admin/accounts/${compteId}/depenses`"
          class="text-sm px-3 py-1.5 rounded-md border border-(--border-default) text-(--text-secondary) hover:bg-(--interactive-hover)"
        >
          Depenses
        </NuxtLink>
        <NuxtLink
          :to="`/admin/accounts/${compteId}/recap`"
          class="text-sm px-3 py-1.5 rounded-md border border-(--border-default) text-(--text-secondary) hover:bg-(--interactive-hover)"
        >
          Recapitulatifs
        </NuxtLink>
        <NuxtLink
          to="/admin/accounts"
          class="text-sm text-(--text-secondary) hover:text-(--text-primary)"
        >
          Liste
        </NuxtLink>
      </div>
    </div>

    <div v-if="error" class="mb-4 p-3 bg-(--color-error-light) text-(--color-error) rounded-md text-sm">
      {{ error }}
    </div>

    <div v-if="loading" class="flex items-center justify-center py-16">
      <span class="text-(--text-secondary)">Chargement...</span>
    </div>

    <div v-else-if="template" class="bg-(--bg-card) shadow rounded-lg p-6">
      <AccountDataTable
        ref="dataTable"
        :template-lines="template.lines"
        :columns="columns"
        :values="valuesMap"
        :computed-values="computedMap"
        :hierarchical-sums="hierarchicalSums"
        template-type="recette"
        @save-line="handleSaveLine"
      />
    </div>

    <div v-else class="text-center py-16 text-(--text-muted)">
      Aucun template de recettes actif. Veuillez configurer un template dans la section Templates.
    </div>
  </div>
</template>

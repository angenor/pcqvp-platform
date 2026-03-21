<script setup lang="ts">
import type { TemplateDetail } from '~/types/templates'
import type { CompteDetail, DepenseProgramResponse } from '~/types/comptes'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const compteId = route.params.id as string

const {
  fetchCompte,
  upsertDepenseLine,
  createProgramme,
  updateProgramme,
  deleteProgramme,
} = useComptes()
const { fetchTemplates, fetchTemplate } = useTemplates()

const compte = ref<CompteDetail | null>(null)
const template = ref<TemplateDetail | null>(null)
const depensesProgrammes = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const activeTab = ref(0)

const showAddProgramme = ref(false)
const newProgrammeIntitule = ref('')
const showDeleteConfirm = ref<string | null>(null)
const editingProgramme = ref<string | null>(null)
const editIntitule = ref('')

const dataTableRefs = ref<Record<number, any>>({})

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

async function loadData() {
  try {
    const [compteData, templatesData] = await Promise.all([
      fetchCompte(compteId),
      fetchTemplates(),
    ])
    compte.value = compteData

    const depTemplate = templatesData.items.find(t => t.type === 'depense' && t.is_active)
    if (depTemplate) {
      template.value = await fetchTemplate(depTemplate.id)
    }

    // Load depenses via a separate fetch (programmes with computed values)
    const { apiFetch } = useApi()
    depensesProgrammes.value = await apiFetch<any[]>(`/api/admin/comptes/${compteId}/depenses-computed`) as any[]
  } catch {
    // Fallback: build from compte data
    depensesProgrammes.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

function getValuesMap(progIndex: number): Record<string, Record<string, number>> {
  const map: Record<string, Record<string, number>> = {}
  const prog = depensesProgrammes.value[progIndex]
  if (prog?.lines) {
    for (const line of prog.lines) {
      map[line.template_line_id] = line.values
    }
  }
  return map
}

function getComputedMap(progIndex: number): Record<string, Record<string, number | null>> {
  const map: Record<string, Record<string, number | null>> = {}
  const prog = depensesProgrammes.value[progIndex]
  if (prog?.lines) {
    for (const line of prog.lines) {
      map[line.template_line_id] = line.computed
    }
  }
  return map
}

function getHierarchicalSums(progIndex: number): Record<string, Record<string, number>> {
  return depensesProgrammes.value[progIndex]?.hierarchical_sums || {}
}

async function handleSaveLine(templateLineId: string, values: Record<string, number>) {
  const prog = compte.value?.programmes[activeTab.value]
  if (!prog) return
  const dtRef = dataTableRefs.value[activeTab.value]
  dtRef?.setLineStatus(templateLineId, 'pending')
  try {
    await upsertDepenseLine(compteId, prog.id, {
      template_line_id: templateLineId,
      values,
    })
    // Reload
    const { apiFetch } = useApi()
    try {
      depensesProgrammes.value = await apiFetch<any[]>(`/api/admin/comptes/${compteId}/depenses-computed`) as any[]
    } catch { /* ignore */ }
    dtRef?.setLineStatus(templateLineId, 'success')
    setTimeout(() => dtRef?.setLineStatus(templateLineId, 'idle'), 2000)
  } catch {
    dtRef?.setLineStatus(templateLineId, 'error')
  }
}

async function handleAddProgramme() {
  if (!newProgrammeIntitule.value.trim()) return
  try {
    await createProgramme(compteId, { intitule: newProgrammeIntitule.value.trim() })
    newProgrammeIntitule.value = ''
    showAddProgramme.value = false
    compte.value = await fetchCompte(compteId)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Erreur lors de l\'ajout'
  }
}

async function handleDeleteProgramme(progId: string) {
  try {
    await deleteProgramme(compteId, progId)
    showDeleteConfirm.value = null
    activeTab.value = 0
    compte.value = await fetchCompte(compteId)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Erreur lors de la suppression'
  }
}

async function handleUpdateProgramme(progId: string) {
  if (!editIntitule.value.trim()) return
  try {
    await updateProgramme(compteId, progId, { intitule: editIntitule.value.trim() })
    editingProgramme.value = null
    compte.value = await fetchCompte(compteId)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Erreur lors de la modification'
  }
}

function startEdit(prog: DepenseProgramResponse) {
  editingProgramme.value = prog.id
  editIntitule.value = prog.intitule
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Depenses</h1>
        <p v-if="compte" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ compte.collectivite_name }} - {{ compte.annee_exercice }}
          <span
            class="ml-2 px-2 py-0.5 rounded text-xs"
            :class="compte.status === 'published'
              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'"
          >
            {{ compte.status === 'published' ? 'Publie' : 'Brouillon' }}
          </span>
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
          :to="`/admin/accounts/${compteId}/recap`"
          class="text-sm px-3 py-1.5 rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          Recapitulatifs
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

    <div v-else-if="template && compte" class="bg-white dark:bg-gray-800 shadow rounded-lg">
      <!-- Programme tabs -->
      <div class="border-b border-gray-200 dark:border-gray-700 px-4 flex items-center gap-2">
        <button
          v-for="(prog, idx) in compte.programmes"
          :key="prog.id"
          class="px-4 py-3 text-sm font-medium border-b-2 transition-colors"
          :class="activeTab === idx
            ? 'border-blue-500 text-blue-600 dark:text-blue-400'
            : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
          @click="activeTab = idx"
        >
          <span v-if="editingProgramme === prog.id">
            <input
              v-model="editIntitule"
              class="px-2 py-0.5 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              @keyup.enter="handleUpdateProgramme(prog.id)"
              @keyup.escape="editingProgramme = null"
              @click.stop
            />
            <button class="ml-1 text-green-600 text-xs" @click.stop="handleUpdateProgramme(prog.id)">OK</button>
          </span>
          <span v-else @dblclick="startEdit(prog)">
            Programme {{ prog.numero }} - {{ prog.intitule }}
          </span>
        </button>

        <button
          class="px-3 py-3 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
          @click="showAddProgramme = true"
        >
          + Ajouter
        </button>
      </div>

      <!-- Programme management -->
      <div v-if="showAddProgramme" class="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750 flex items-center gap-3">
        <input
          v-model="newProgrammeIntitule"
          placeholder="Intitule du programme"
          class="flex-1 px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          @keyup.enter="handleAddProgramme"
        />
        <button
          class="px-3 py-1.5 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
          @click="handleAddProgramme"
        >
          Ajouter
        </button>
        <button
          class="px-3 py-1.5 text-gray-500 text-sm"
          @click="showAddProgramme = false"
        >
          Annuler
        </button>
      </div>

      <!-- Delete confirmation -->
      <div
        v-if="showDeleteConfirm"
        class="p-4 border-b border-gray-200 dark:border-gray-700 bg-red-50 dark:bg-red-900/20 flex items-center justify-between"
      >
        <span class="text-sm text-red-700 dark:text-red-300">
          Supprimer ce programme et toutes ses lignes de depenses ?
        </span>
        <div class="flex gap-2">
          <button
            class="px-3 py-1.5 bg-red-600 text-white rounded-md text-sm hover:bg-red-700"
            @click="handleDeleteProgramme(showDeleteConfirm)"
          >
            Supprimer
          </button>
          <button
            class="px-3 py-1.5 text-gray-500 text-sm"
            @click="showDeleteConfirm = null"
          >
            Annuler
          </button>
        </div>
      </div>

      <!-- Current programme actions -->
      <div v-if="compte.programmes[activeTab]" class="px-4 py-2 border-b border-gray-100 dark:border-gray-700/50 flex justify-end gap-2">
        <button
          class="text-xs text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
          @click="showDeleteConfirm = compte.programmes[activeTab].id"
        >
          Supprimer ce programme
        </button>
      </div>

      <!-- Data table for active programme -->
      <div class="p-6">
        <AccountDataTable
          v-if="compte.programmes[activeTab]"
          :ref="(el: any) => { dataTableRefs[activeTab] = el }"
          :template-lines="template.lines"
          :columns="columns"
          :values="getValuesMap(activeTab)"
          :computed-values="getComputedMap(activeTab)"
          :hierarchical-sums="getHierarchicalSums(activeTab)"
          template-type="depense"
          @save-line="handleSaveLine"
        />
      </div>
    </div>
  </div>
</template>

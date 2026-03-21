<script setup lang="ts">
import type { TemplateDetail, TemplateLine, TemplateColumn } from '~/types/templates'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const { fetchTemplate, addLine, deleteLine, updateLines, updateColumns } = useTemplates()

const template = ref<TemplateDetail | null>(null)
const loading = ref(true)
const error = ref('')
const search = ref('')
const allExpanded = ref(true)
const collapsedCodes = ref<Set<string>>(new Set())

// Add line form
const showAddForm = ref(false)
const newLine = ref({
  compte_code: '',
  intitule: '',
  level: 3,
  parent_code: '',
  section: 'fonctionnement',
  sort_order: 0,
})
const addLineError = ref('')
const addLineLoading = ref(false)

// Delete
const deletingLineId = ref<string | null>(null)
const deleteError = ref('')

async function loadTemplate() {
  loading.value = true
  error.value = ''
  try {
    template.value = await fetchTemplate(route.params.id as string)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Erreur de chargement'
  } finally {
    loading.value = false
  }
}

onMounted(loadTemplate)

// Filtering
const filteredLines = computed(() => {
  if (!template.value) return []
  const lines = template.value.lines
  if (!search.value.trim()) return lines

  const q = search.value.trim().toLowerCase()
  const matchingCodes = new Set<string>()

  // Find matching lines
  for (const line of lines) {
    if (line.compte_code.toLowerCase().includes(q) || line.intitule.toLowerCase().includes(q)) {
      matchingCodes.add(line.compte_code)
      // Include parents
      if (line.parent_code) {
        matchingCodes.add(line.parent_code)
        const parent = lines.find(l => l.compte_code === line.parent_code)
        if (parent?.parent_code) matchingCodes.add(parent.parent_code)
      }
    }
  }

  return lines.filter(l => matchingCodes.has(l.compte_code))
})

// Collapsing
function isLineVisible(line: TemplateLine): boolean {
  if (line.level === 1) return true
  if (!line.parent_code) return true

  // Check if parent is collapsed
  if (collapsedCodes.value.has(line.parent_code)) return false

  // Check grandparent
  const parent = template.value?.lines.find(l => l.compte_code === line.parent_code)
  if (parent?.parent_code && collapsedCodes.value.has(parent.parent_code)) return false

  return true
}

function toggleCollapse(code: string) {
  if (collapsedCodes.value.has(code)) {
    collapsedCodes.value.delete(code)
  } else {
    collapsedCodes.value.add(code)
  }
}

function toggleAll() {
  if (allExpanded.value) {
    // Collapse all Niv1 and Niv2
    template.value?.lines.forEach(l => {
      if (l.level < 3) collapsedCodes.value.add(l.compte_code)
    })
    allExpanded.value = false
  } else {
    collapsedCodes.value.clear()
    allExpanded.value = true
  }
}

function hasChildren(code: string): boolean {
  return template.value?.lines.some(l => l.parent_code === code) ?? false
}

// Section grouping
function getSectionLabel(section: string): string {
  return section === 'fonctionnement' ? 'FONCTIONNEMENT' : 'INVESTISSEMENT'
}

const groupedLines = computed(() => {
  const lines = filteredLines.value
  const groups: { section: string; lines: TemplateLine[] }[] = []
  let currentSection = ''

  for (const line of lines) {
    const s = line.section
    if (s !== currentSection) {
      currentSection = s
      groups.push({ section: s, lines: [] })
    }
    groups[groups.length - 1].lines.push(line)
  }
  return groups
})

// Indent classes
function indentClass(level: number): string {
  if (level === 1) return ''
  if (level === 2) return 'pl-6'
  return 'pl-12'
}

function lineClass(level: number): string {
  if (level === 1) return 'font-bold text-gray-900 dark:text-white'
  if (level === 2) return 'font-semibold text-gray-800 dark:text-gray-200'
  return 'text-gray-700 dark:text-gray-300'
}

// Add line
async function submitAddLine() {
  addLineLoading.value = true
  addLineError.value = ''
  try {
    const sortOrder = template.value ? template.value.lines.length + 1 : 1
    await addLine(route.params.id as string, {
      ...newLine.value,
      parent_code: newLine.value.parent_code || null,
      sort_order: sortOrder,
    } as any)
    showAddForm.value = false
    newLine.value = { compte_code: '', intitule: '', level: 3, parent_code: '', section: 'fonctionnement', sort_order: 0 }
    await loadTemplate()
  } catch (e: any) {
    addLineError.value = e?.data?.detail || 'Erreur lors de l\'ajout'
  } finally {
    addLineLoading.value = false
  }
}

// Delete line
async function confirmDeleteLine(lineId: string) {
  deletingLineId.value = lineId
}

async function executeDelete() {
  if (!deletingLineId.value) return
  deleteError.value = ''
  try {
    await deleteLine(route.params.id as string, deletingLineId.value)
    deletingLineId.value = null
    await loadTemplate()
  } catch (e: any) {
    deleteError.value = e?.data?.detail || 'Erreur lors de la suppression'
  }
}

// Available parents for add form
const availableParents = computed(() => {
  if (!template.value) return []
  const targetLevel = newLine.value.level - 1
  return template.value.lines.filter(l => l.level === targetLevel)
})
</script>

<template>
  <div>
    <!-- Back + title -->
    <div class="mb-6">
      <NuxtLink
        to="/admin/templates"
        class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
      >
        &larr; Retour a la liste
      </NuxtLink>
    </div>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400">Chargement...</div>
    <div v-else-if="error" class="text-red-600 dark:text-red-400">{{ error }}</div>

    <template v-else-if="template">
      <!-- Template header -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ template.name }}</h1>
            <div class="flex items-center gap-3 mt-2">
              <span
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="template.type === 'recette'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                  : 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'"
              >
                {{ template.type === 'recette' ? 'Recette' : 'Depense' }}
              </span>
              <span class="text-sm text-gray-500 dark:text-gray-400">v{{ template.version }}</span>
              <span
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="template.is_active
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'"
              >
                {{ template.is_active ? 'Actif' : 'Inactif' }}
              </span>
            </div>
          </div>
          <div class="text-right text-sm text-gray-500 dark:text-gray-400">
            <p>{{ template.lines.length }} lignes</p>
            <p>{{ template.columns.length }} colonnes</p>
          </div>
        </div>
      </div>

      <!-- Columns -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Colonnes</h2>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="col in template.columns"
            :key="col.id"
            class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
          >
            {{ col.name }}
            <span
              v-if="col.is_computed"
              class="px-1.5 py-0.5 text-xs rounded bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300"
            >
              Calcule
            </span>
          </span>
        </div>
      </div>

      <!-- Lines -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Structure des comptes</h2>
          <div class="flex items-center gap-3">
            <input
              v-model="search"
              type="text"
              placeholder="Rechercher par code ou intitule..."
              class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              class="px-3 py-1.5 text-sm rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              @click="toggleAll"
            >
              {{ allExpanded ? 'Tout replier' : 'Tout deplier' }}
            </button>
            <button
              class="px-3 py-1.5 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors"
              @click="showAddForm = !showAddForm"
            >
              Ajouter une ligne
            </button>
          </div>
        </div>

        <!-- Add line form -->
        <div v-if="showAddForm" class="mb-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Nouvelle ligne</h3>
          <div v-if="addLineError" class="mb-3 text-sm text-red-600 dark:text-red-400">{{ addLineError }}</div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Code compte</label>
              <input v-model="newLine.compte_code" type="text" class="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Intitule</label>
              <input v-model="newLine.intitule" type="text" class="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Niveau</label>
              <select v-model.number="newLine.level" class="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option :value="1">Niveau 1</option>
                <option :value="2">Niveau 2</option>
                <option :value="3">Niveau 3</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Code parent</label>
              <select v-model="newLine.parent_code" class="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="">Aucun (Niveau 1)</option>
                <option v-for="p in availableParents" :key="p.compte_code" :value="p.compte_code">
                  {{ p.compte_code }} - {{ p.intitule }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Section</label>
              <select v-model="newLine.section" class="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="fonctionnement">Fonctionnement</option>
                <option value="investissement">Investissement</option>
              </select>
            </div>
          </div>
          <div class="flex gap-2 mt-3">
            <button
              class="px-3 py-1.5 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
              :disabled="addLineLoading || !newLine.compte_code || !newLine.intitule"
              @click="submitAddLine"
            >
              {{ addLineLoading ? 'Ajout...' : 'Ajouter' }}
            </button>
            <button
              class="px-3 py-1.5 text-sm rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              @click="showAddForm = false"
            >
              Annuler
            </button>
          </div>
        </div>

        <!-- Lines table -->
        <div class="overflow-x-auto">
          <table class="min-w-full">
            <thead>
              <tr class="border-b border-gray-200 dark:border-gray-700">
                <th class="py-2 px-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-24">Code</th>
                <th class="py-2 px-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Intitule</th>
                <th class="py-2 px-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-16">Niv</th>
                <th class="py-2 px-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase w-20">Actions</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="group in groupedLines" :key="group.section">
                <tr>
                  <td colspan="4" class="py-2 px-3 bg-gray-50 dark:bg-gray-700/50">
                    <span class="text-xs font-bold uppercase text-gray-500 dark:text-gray-400">
                      {{ getSectionLabel(group.section) }}
                    </span>
                  </td>
                </tr>
                <template v-for="line in group.lines" :key="line.id">
                  <tr
                    v-if="isLineVisible(line)"
                    class="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/20 transition-colors"
                  >
                    <td class="py-1.5 px-3 text-sm font-mono text-gray-600 dark:text-gray-400">
                      {{ line.compte_code }}
                    </td>
                    <td class="py-1.5 px-3 text-sm" :class="[indentClass(line.level), lineClass(line.level)]">
                      <button
                        v-if="hasChildren(line.compte_code)"
                        class="mr-1 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
                        @click="toggleCollapse(line.compte_code)"
                      >
                        {{ collapsedCodes.has(line.compte_code) ? '&#9654;' : '&#9660;' }}
                      </button>
                      {{ line.intitule }}
                    </td>
                    <td class="py-1.5 px-3 text-xs text-gray-500 dark:text-gray-400">{{ line.level }}</td>
                    <td class="py-1.5 px-3 text-right">
                      <button
                        v-if="line.level === 3"
                        class="text-xs text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 transition-colors"
                        @click="confirmDeleteLine(line.id)"
                      >
                        Supprimer
                      </button>
                    </td>
                  </tr>
                </template>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Delete confirmation modal -->
    <div
      v-if="deletingLineId"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="deletingLineId = null"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-sm w-full mx-4 border border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Confirmer la suppression</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Voulez-vous vraiment supprimer cette ligne ?
        </p>
        <div v-if="deleteError" class="mb-3 text-sm text-red-600 dark:text-red-400">{{ deleteError }}</div>
        <div class="flex justify-end gap-2">
          <button
            class="px-3 py-1.5 text-sm rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            @click="deletingLineId = null; deleteError = ''"
          >
            Annuler
          </button>
          <button
            class="px-3 py-1.5 text-sm rounded-md bg-red-600 text-white hover:bg-red-700 transition-colors"
            @click="executeDelete"
          >
            Supprimer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PublicCompteResponse } from '../../../../packages/shared/types/public'

const props = defineProps<{
  modelValue: boolean
  type: string
  id: string
  annee: number | null
  name: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const { fetchCompte, downloadExport } = usePublicComptes()

const compteData = ref<PublicCompteResponse | null>(null)
const loading = ref(false)
const error = ref('')
const activeTab = ref<'recettes' | 'depenses' | 'recapitulatifs' | 'equilibre'>('recettes')
const activeProgIdx = ref(0)
const downloadingExcel = ref(false)
const downloadingWord = ref(false)
const downloadError = ref('')

watch(
  () => [props.modelValue, props.type, props.id, props.annee],
  async ([open, type, id, annee]) => {
    if (!open || !annee) return
    loading.value = true
    error.value = ''
    compteData.value = null
    activeTab.value = 'recettes'
    activeProgIdx.value = 0
    try {
      compteData.value = await fetchCompte(type as string, id as string, annee as number)
    } catch {
      error.value = 'Impossible de charger le compte.'
    } finally {
      loading.value = false
    }
  },
  { immediate: true },
)

async function handleExport(format: 'xlsx' | 'docx') {
  if (!props.annee) return
  downloadError.value = ''
  const isExcel = format === 'xlsx'
  if (isExcel) downloadingExcel.value = true
  else downloadingWord.value = true

  try {
    const result = await downloadExport(props.type, props.id, props.annee, format)
    if (!result.success) {
      downloadError.value = `Erreur lors du telechargement du fichier ${isExcel ? 'Excel' : 'Word'}.`
    }
  } catch {
    downloadError.value = `Erreur lors du telechargement du fichier ${isExcel ? 'Excel' : 'Word'}.`
  } finally {
    if (isExcel) downloadingExcel.value = false
    else downloadingWord.value = false
  }
}

function close() {
  emit('update:modelValue', false)
}
</script>

<template>
  <UiModal :model-value="modelValue" size="full" @update:model-value="close">
    <div class="max-h-[85vh] overflow-y-auto">
      <div class="mb-4 pr-8">
        <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
          Aperçu du compte administratif
        </p>
        <h3 class="text-lg md:text-xl font-semibold text-gray-900 dark:text-white">
          {{ name }} — Exercice {{ annee }}
        </h3>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-20">
        <svg class="animate-spin h-8 w-8 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>

      <div v-else-if="error" class="text-center py-12 text-red-600 dark:text-red-400">
        {{ error }}
      </div>

      <div v-else-if="compteData">
        <div class="flex flex-wrap items-center gap-2 mb-4">
          <button
            class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors inline-flex items-center gap-1.5"
            :class="{ 'opacity-50 cursor-not-allowed': downloadingExcel }"
            :disabled="downloadingExcel"
            @click="handleExport('xlsx')"
          >
            <svg v-if="downloadingExcel" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {{ downloadingExcel ? 'Chargement...' : 'Télécharger Excel' }}
          </button>
          <button
            class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors inline-flex items-center gap-1.5"
            :class="{ 'opacity-50 cursor-not-allowed': downloadingWord }"
            :disabled="downloadingWord"
            @click="handleExport('docx')"
          >
            <svg v-if="downloadingWord" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {{ downloadingWord ? 'Chargement...' : 'Télécharger Word' }}
          </button>
          <p v-if="downloadError" class="text-sm text-red-600 dark:text-red-400">
            {{ downloadError }}
          </p>
        </div>

        <div class="border-b border-gray-200 dark:border-gray-700 mb-4">
          <nav class="flex gap-1 -mb-px overflow-x-auto">
            <button
              v-for="tab in [
                { key: 'recettes', label: 'Recettes' },
                { key: 'depenses', label: 'Depenses' },
                { key: 'recapitulatifs', label: 'Recapitulatifs' },
                { key: 'equilibre', label: 'Equilibre' },
              ]"
              :key="tab.key"
              class="px-4 py-2 text-sm font-medium whitespace-nowrap transition-colors border-b-2"
              :class="activeTab === tab.key
                ? 'border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'"
              @click="activeTab = tab.key as typeof activeTab"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>

        <div v-if="activeTab === 'recettes'">
          <AccountTable
            :sections="compteData.recettes.sections"
            :columns="compteData.recettes.template_columns"
          />
        </div>

        <div v-else-if="activeTab === 'depenses'">
          <div v-if="compteData.depenses.programmes.length > 0">
            <div class="flex gap-2 mb-4 overflow-x-auto">
              <button
                v-for="(prog, idx) in compteData.depenses.programmes"
                :key="prog.id"
                class="px-3 py-1.5 text-sm rounded-full whitespace-nowrap transition-colors"
                :class="activeProgIdx === idx
                  ? 'bg-blue-600 dark:bg-blue-500 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'"
                @click="activeProgIdx = idx"
              >
                Prog. {{ prog.numero }} - {{ prog.intitule }}
              </button>
            </div>
            <AccountTable
              :sections="compteData.depenses.programmes[activeProgIdx].sections"
              :columns="compteData.depenses.template_columns"
            />
          </div>
          <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
            Aucun programme de depenses.
          </div>
        </div>

        <div v-else-if="activeTab === 'recapitulatifs'">
          <RecapTable
            :recap-recettes="compteData.recapitulatifs.recettes"
            :recap-depenses="compteData.recapitulatifs.depenses"
          />
        </div>

        <div v-else-if="activeTab === 'equilibre'">
          <EquilibreTable :equilibre="compteData.equilibre" />
        </div>
      </div>
    </div>
  </UiModal>
</template>

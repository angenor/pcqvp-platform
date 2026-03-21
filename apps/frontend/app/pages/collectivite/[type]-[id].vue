<script setup lang="ts">
import type { PublicCompteResponse, PublicDescriptionResponse } from '../../../../../packages/shared/types/public'

const route = useRoute()
const rawParam = route.params['type-id'] as string || `${route.params.type}-${route.params.id}`
const parts = rawParam.match(/^(province|region|commune)-(.+)$/)
const collectiviteType = parts?.[1] || ''
const collectiviteId = parts?.[2] || ''

const { fetchAnnees, fetchDescription, fetchCompte, downloadExport } = usePublicComptes()

const description = ref<PublicDescriptionResponse | null>(null)
const annees = ref<number[]>([])
const selectedAnnee = ref<number | null>(null)
const compteData = ref<PublicCompteResponse | null>(null)
const activeTab = ref<'recettes' | 'depenses' | 'recapitulatifs' | 'equilibre'>('recettes')
const activeProgIdx = ref(0)
const loading = ref(true)
const loadingCompte = ref(false)
const error = ref('')
const downloadingExcel = ref(false)
const downloadingWord = ref(false)
const downloadError = ref('')

onMounted(async () => {
  if (!collectiviteType || !collectiviteId) {
    error.value = 'URL invalide'
    loading.value = false
    return
  }

  try {
    const [desc, years] = await Promise.all([
      fetchDescription(collectiviteType, collectiviteId),
      fetchAnnees(collectiviteType, collectiviteId),
    ])
    description.value = desc
    annees.value = years

    if (years.length > 0) {
      selectedAnnee.value = years[0]
    }
  } catch {
    error.value = 'Collectivite non trouvee'
  } finally {
    loading.value = false
  }
})

watch(selectedAnnee, async (annee) => {
  if (!annee) return
  loadingCompte.value = true
  try {
    compteData.value = await fetchCompte(collectiviteType, collectiviteId, annee)
  } catch {
    compteData.value = null
  } finally {
    loadingCompte.value = false
  }
})

function handlePrint() {
  window.print()
}

async function handleExport(format: 'xlsx' | 'docx') {
  if (!selectedAnnee.value) return
  downloadError.value = ''
  const isExcel = format === 'xlsx'
  if (isExcel) downloadingExcel.value = true
  else downloadingWord.value = true

  try {
    const result = await downloadExport(collectiviteType, collectiviteId, selectedAnnee.value, format)
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

const typeLabel = computed(() => {
  const labels: Record<string, string> = { province: 'Province', region: 'Region', commune: 'Commune' }
  return labels[collectiviteType] || collectiviteType
})

const seoTitle = computed(() => {
  const name = description.value?.name || ''
  const annee = selectedAnnee.value || ''
  if (name && annee) return `${name} - Compte administratif ${annee} | PCQVP Madagascar`
  if (name) return `${name} | PCQVP Madagascar`
  return 'Consultation | PCQVP Madagascar'
})

const seoDescription = computed(() => {
  const name = description.value?.name || 'la collectivite'
  const annee = selectedAnnee.value
  if (annee) return `Consultez les recettes et depenses de ${name} pour l'exercice ${annee}.`
  return `Consultez les comptes administratifs de ${name}.`
})

useSeoMeta({
  title: seoTitle,
  description: seoDescription,
  ogTitle: seoTitle,
  ogDescription: seoDescription,
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <header class="bg-white dark:bg-gray-800 shadow-sm print:shadow-none">
      <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div class="w-8 h-8 bg-blue-600 dark:bg-blue-500 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-sm">TI</span>
          </div>
          <span class="text-sm text-gray-500 dark:text-gray-400 hidden sm:inline">PCQVP Madagascar</span>
        </NuxtLink>
        <button
          class="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors print:hidden"
          @click="useColorMode().preference = useColorMode().value === 'dark' ? 'light' : 'dark'"
        >
          <svg v-if="useColorMode().value === 'dark'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        </button>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <svg class="animate-spin h-8 w-8 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="max-w-6xl mx-auto px-4 py-20 text-center">
      <p class="text-red-600 dark:text-red-400 text-lg">{{ error }}</p>
      <NuxtLink to="/" class="mt-4 inline-block text-blue-600 dark:text-blue-400 hover:underline">
        Retour a l'accueil
      </NuxtLink>
    </div>

    <!-- Content -->
    <main v-else class="max-w-6xl mx-auto px-4 py-6">
      <!-- Title and description -->
      <div class="mb-6">
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ typeLabel }}</p>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
          {{ description?.name }}
        </h1>

        <!-- Rich content description -->
        <div v-if="description?.description_json?.length" class="mt-4">
          <RichContentRenderer :description-json="description.description_json" />
        </div>
      </div>

      <!-- Year selector + action buttons -->
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 print:hidden">
        <div class="flex items-center gap-3">
          <label for="annee-select" class="text-sm font-medium text-gray-700 dark:text-gray-300">
            Exercice :
          </label>
          <select
            id="annee-select"
            v-model="selectedAnnee"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option v-for="annee in annees" :key="annee" :value="annee">{{ annee }}</option>
          </select>
          <span v-if="annees.length === 0" class="text-sm text-gray-500 dark:text-gray-400">
            Aucun compte publie
          </span>
        </div>

        <!-- Action buttons -->
        <div v-if="compteData" class="flex items-center gap-2">
          <button
            class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            @click="handlePrint"
          >
            Imprimer
          </button>
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
            {{ downloadingExcel ? 'Chargement...' : 'Excel' }}
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
            {{ downloadingWord ? 'Chargement...' : 'Word' }}
          </button>
        </div>
        <p v-if="downloadError" class="mt-2 text-sm text-red-600 dark:text-red-400">
          {{ downloadError }}
        </p>
      </div>

      <!-- Loading compte -->
      <div v-if="loadingCompte" class="flex items-center justify-center py-12">
        <svg class="animate-spin h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>

      <!-- No data -->
      <div v-else-if="!compteData && annees.length > 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        Aucune donnee disponible pour cette annee.
      </div>

      <!-- Tabs + content -->
      <div v-else-if="compteData">
        <!-- Tab navigation -->
        <div class="border-b border-gray-200 dark:border-gray-700 mb-6 print:hidden">
          <nav class="flex gap-1 -mb-px overflow-x-auto">
            <button
              v-for="tab in [
                { key: 'recettes', label: 'Recettes' },
                { key: 'depenses', label: 'Depenses' },
                { key: 'recapitulatifs', label: 'Recapitulatifs' },
                { key: 'equilibre', label: 'Equilibre' },
              ]"
              :key="tab.key"
              class="px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2"
              :class="activeTab === tab.key
                ? 'border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'"
              @click="activeTab = tab.key as typeof activeTab"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>

        <!-- Recettes tab -->
        <div v-if="activeTab === 'recettes'">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 hidden print:block">Recettes</h2>
          <AccountTable
            :sections="compteData.recettes.sections"
            :columns="compteData.recettes.template_columns"
          />
        </div>

        <!-- Depenses tab -->
        <div v-else-if="activeTab === 'depenses'">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 hidden print:block">Depenses</h2>
          <!-- Sub-tabs for programmes -->
          <div v-if="compteData.depenses.programmes.length > 0">
            <div class="flex gap-2 mb-4 overflow-x-auto print:hidden">
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

        <!-- Recapitulatifs tab -->
        <div v-else-if="activeTab === 'recapitulatifs'">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 hidden print:block">Recapitulatifs</h2>
          <RecapTable
            :recap-recettes="compteData.recapitulatifs.recettes"
            :recap-depenses="compteData.recapitulatifs.depenses"
          />
        </div>

        <!-- Equilibre tab -->
        <div v-else-if="activeTab === 'equilibre'">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 hidden print:block">Equilibre</h2>
          <EquilibreTable :equilibre="compteData.equilibre" />
        </div>
      </div>
    </main>
  </div>
</template>

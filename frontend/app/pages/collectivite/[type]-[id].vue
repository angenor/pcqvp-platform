<script setup lang="ts">
import type {
  PublicCompteResponse,
  PublicDescriptionResponse,
  PublicParentDocument,
} from '../../../../packages/shared/types/public'

const route = useRoute()
const rawParam = route.params['type-id'] as string || `${route.params.type}-${route.params.id}`
const parts = rawParam.match(/^(province|region|commune)-(.+)$/)
const collectiviteType = parts?.[1] || ''
const collectiviteId = parts?.[2] || ''

const { fetchAnnees, fetchDescription, fetchCompte, fetchDocumentsLies, downloadExport } = usePublicComptes()
const { fetchEditorial } = useEditorial()

const description = ref<PublicDescriptionResponse | null>(null)
const defaultHeroImage = ref<string | null>(null)
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
const parentDocuments = ref<PublicParentDocument[]>([])
const previewOpen = ref(false)
const previewType = ref('')
const previewId = ref('')
const previewAnnee = ref<number | null>(null)
const previewName = ref('')
const parentDownloading = ref<Record<string, boolean>>({})

function openPreview(parent: PublicParentDocument, annee: number) {
  previewType.value = parent.type
  previewId.value = parent.id
  previewAnnee.value = annee
  previewName.value = parent.name
  previewOpen.value = true
}

async function downloadParent(parent: PublicParentDocument, annee: number, format: 'xlsx' | 'docx') {
  const key = `${parent.type}-${parent.id}-${annee}-${format}`
  parentDownloading.value = { ...parentDownloading.value, [key]: true }
  try {
    await downloadExport(parent.type, parent.id, annee, format)
  } finally {
    parentDownloading.value = { ...parentDownloading.value, [key]: false }
  }
}

function parentTypeLabel(t: string) {
  const labels: Record<string, string> = { province: 'Province', region: 'Region', commune: 'Commune' }
  return labels[t] || t
}

onMounted(async () => {
  if (!collectiviteType || !collectiviteId) {
    error.value = 'URL invalide'
    loading.value = false
    return
  }

  try {
    const [desc, years, editorial, docsLies] = await Promise.all([
      fetchDescription(collectiviteType, collectiviteId),
      fetchAnnees(collectiviteType, collectiviteId),
      fetchEditorial().catch(() => null),
      fetchDocumentsLies(collectiviteType, collectiviteId).catch(() => ({ parents: [] })),
    ])
    description.value = desc
    annees.value = years
    parentDocuments.value = docsLies.parents
    if (editorial?.hero?.image) {
      defaultHeroImage.value = editorial.hero.image
    }

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

const heroImage = computed(() => description.value?.banner_image || defaultHeroImage.value)

const hasDescription = computed(() => {
  const dj = description.value?.description_json
  if (!dj) return false
  if (Array.isArray(dj)) return dj.length > 0
  if (typeof dj === 'object' && 'blocks' in dj) return (dj as any).blocks?.length > 0
  return false
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
  <div>
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
    <div v-else>
      <!-- Hero section -->
      <CollectiviteHero
        v-if="heroImage"
        :name="description!.name"
        :type="collectiviteType"
        :banner-image="heroImage"
      />

      <main class="max-w-6xl mx-auto px-4 py-6">
      <!-- Title (fallback when no hero image at all) -->
      <div v-if="!heroImage" class="mb-6">
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ typeLabel }}</p>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
          {{ description?.name }}
        </h1>
      </div>

      <!-- Rich content description -->
      <div v-if="hasDescription" class="mb-6">
        <RichContentRenderer :description-json="description!.description_json" />
      </div>

      <!-- Documents officiels (niveau courant) -->
      <CollectivityDocumentsList
        v-if="description?.documents?.length"
        :documents="description.documents"
      />

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

      <!-- Documents liés (niveaux parents) -->
      <section v-if="parentDocuments.length > 0" class="mt-10 print:hidden">
        <h2 class="text-lg md:text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Documents liés
        </h2>
        <div class="space-y-4">
          <div
            v-for="parent in parentDocuments"
            :key="`${parent.type}-${parent.id}`"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="mb-3">
              <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
                {{ parentTypeLabel(parent.type) }}
              </p>
              <p class="text-base font-semibold text-gray-900 dark:text-white">
                {{ parent.name }}
              </p>
            </div>
            <ul class="divide-y divide-gray-200 dark:divide-gray-700">
              <li
                v-for="annee in parent.annees"
                :key="annee"
                class="py-2 flex flex-wrap items-center justify-between gap-2"
              >
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  Compte administratif — Exercice {{ annee }}
                </span>
                <div class="flex flex-wrap items-center gap-2">
                  <button
                    class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    @click="openPreview(parent, annee)"
                  >
                    Aperçu
                  </button>
                  <button
                    class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                    :disabled="parentDownloading[`${parent.type}-${parent.id}-${annee}-xlsx`]"
                    @click="downloadParent(parent, annee, 'xlsx')"
                  >
                    {{ parentDownloading[`${parent.type}-${parent.id}-${annee}-xlsx`] ? 'Chargement...' : 'Excel' }}
                  </button>
                  <button
                    class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                    :disabled="parentDownloading[`${parent.type}-${parent.id}-${annee}-docx`]"
                    @click="downloadParent(parent, annee, 'docx')"
                  >
                    {{ parentDownloading[`${parent.type}-${parent.id}-${annee}-docx`] ? 'Chargement...' : 'Word' }}
                  </button>
                </div>
              </li>
              <li
                v-for="doc in parent.documents"
                :key="doc.id"
                class="py-2 flex flex-wrap items-center justify-between gap-2"
              >
                <span class="text-sm text-gray-700 dark:text-gray-300 truncate">
                  {{ doc.title }}
                </span>
                <a
                  :href="doc.download_url"
                  target="_blank"
                  rel="noopener"
                  class="inline-flex items-center gap-1 px-3 py-1.5 text-sm border border-blue-200 dark:border-blue-700 rounded-md text-blue-700 dark:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors"
                >
                  <font-awesome-icon :icon="['fas', 'download']" />
                  <span>Télécharger</span>
                </a>
              </li>
            </ul>
          </div>
        </div>
      </section>
    </main>
    </div>

    <CompteDocumentPreview
      v-model="previewOpen"
      :type="previewType"
      :id="previewId"
      :annee="previewAnnee"
      :name="previewName"
    />
  </div>
</template>

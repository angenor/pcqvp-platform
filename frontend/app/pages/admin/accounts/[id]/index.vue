<script setup lang="ts">
import type { ProvinceListItem, RegionListItem, CommuneListItem } from '~/types/geography'
import type { CompteDetail } from '~/types/comptes'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const compteId = route.params.id as string

const { fetchCompte, updateCompte, updateStatus } = useComptes()
const { fetchProvinces, fetchRegions, fetchCommunes, fetchRegionDetail } = useGeography()
const { user } = useAuth()

const compte = ref<CompteDetail | null>(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')

// Edit mode
const editing = ref(false)
const collectiviteType = ref<'province' | 'region' | 'commune'>('commune')
const provinces = ref<ProvinceListItem[]>([])
const regions = ref<RegionListItem[]>([])
const communes = ref<CommuneListItem[]>([])
const selectedProvinceId = ref('')
const selectedRegionId = ref('')
const selectedCommuneId = ref('')
const anneeExercice = ref<number>(new Date().getFullYear())

const collectiviteTypeOptions = [
  { value: 'province', label: 'Province' },
  { value: 'region', label: 'Region' },
  { value: 'commune', label: 'Commune' },
]

const provinceOptions = computed(() =>
  provinces.value.map(p => ({ value: p.id, label: p.name }))
)
const regionOptions = computed(() =>
  regions.value.map(r => ({ value: r.id, label: r.name }))
)
const communeOptions = computed(() =>
  communes.value.map(c => ({ value: c.id, label: c.name }))
)

const selectedCollectiviteId = computed(() => {
  if (collectiviteType.value === 'province') return selectedProvinceId.value
  if (collectiviteType.value === 'region') return selectedRegionId.value
  return selectedCommuneId.value
})

const canSubmit = computed(() => {
  return !!selectedCollectiviteId.value && !!anneeExercice.value
})

const isAdmin = computed(() => user.value?.role === 'admin')

onMounted(async () => {
  try {
    const [compteData, provs] = await Promise.all([
      fetchCompte(compteId),
      fetchProvinces(),
    ])
    compte.value = compteData
    provinces.value = provs
  } catch {
    error.value = 'Erreur lors du chargement'
  } finally {
    loading.value = false
  }
})

watch(selectedProvinceId, async (id) => {
  if (!editing.value) return
  selectedRegionId.value = ''
  selectedCommuneId.value = ''
  regions.value = []
  communes.value = []
  if (id) {
    regions.value = await fetchRegions(id)
  }
})

watch(selectedRegionId, async (id) => {
  if (!editing.value) return
  selectedCommuneId.value = ''
  communes.value = []
  if (id) {
    communes.value = await fetchCommunes(id)
  }
})

async function startEditing() {
  if (!compte.value) return
  editing.value = true
  error.value = ''
  success.value = ''

  collectiviteType.value = compte.value.collectivite_type as 'province' | 'region' | 'commune'
  anneeExercice.value = compte.value.annee_exercice

  // Pre-fill geography selectors
  if (collectiviteType.value === 'province') {
    selectedProvinceId.value = compte.value.collectivite_id
  } else if (collectiviteType.value === 'region') {
    const regionDetail = await fetchRegionDetail(compte.value.collectivite_id)
    if (regionDetail.province_id) {
      selectedProvinceId.value = regionDetail.province_id
      regions.value = await fetchRegions(regionDetail.province_id)
      selectedRegionId.value = compte.value.collectivite_id
    }
  } else if (collectiviteType.value === 'commune') {
    // For commune, we need to resolve the chain
    // Load all regions for each province until we find the right commune
    const { apiFetch } = useApi()
    try {
      const communeDetail = await apiFetch<any>(`/api/geography/communes/${compte.value.collectivite_id}`)
      if (communeDetail.region_id) {
        const regionDetail = await fetchRegionDetail(communeDetail.region_id)
        if (regionDetail.province_id) {
          selectedProvinceId.value = regionDetail.province_id
          regions.value = await fetchRegions(regionDetail.province_id)
          selectedRegionId.value = communeDetail.region_id
          communes.value = await fetchCommunes(communeDetail.region_id)
          selectedCommuneId.value = compte.value.collectivite_id
        }
      }
    } catch {
      // Fallback: just set the type
    }
  }
}

function cancelEditing() {
  editing.value = false
  error.value = ''
}

async function handleSave() {
  if (!canSubmit.value) return
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    const result = await updateCompte(compteId, {
      collectivite_type: collectiviteType.value,
      collectivite_id: selectedCollectiviteId.value,
      annee_exercice: anneeExercice.value,
    })
    compte.value = result
    editing.value = false
    success.value = 'Compte mis a jour avec succes.'
    setTimeout(() => success.value = '', 3000)
  } catch (e: any) {
    const detail = e?.response?._data?.detail || e?.data?.detail || ''
    if (detail.includes('existe deja')) {
      error.value = 'Un compte existe deja pour cette collectivite et cette annee.'
    } else if (detail.includes('non trouvee')) {
      error.value = 'Collectivite non trouvee.'
    } else {
      error.value = detail || 'Erreur lors de la mise a jour.'
    }
  } finally {
    saving.value = false
  }
}

async function toggleStatus() {
  if (!compte.value) return
  const newStatus = compte.value.status === 'published' ? 'draft' : 'published'
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await updateStatus(compteId, { status: newStatus })
    compte.value = await fetchCompte(compteId)
    success.value = `Statut change en "${newStatus === 'published' ? 'Publie' : 'Brouillon'}".`
    setTimeout(() => success.value = '', 3000)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Erreur lors du changement de statut.'
  } finally {
    saving.value = false
  }
}

function formatDate(d: string | null): string {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-(--text-primary)">Detail du compte</h1>
      <UiButton variant="ghost" to="/admin/accounts" :icon="['fas', 'arrow-left']">
        Retour a la liste
      </UiButton>
    </div>

    <UiAlert v-if="error" variant="error" class="mb-4" dismissible @dismiss="error = ''">
      {{ error }}
    </UiAlert>
    <UiAlert v-if="success" variant="success" class="mb-4" dismissible @dismiss="success = ''">
      {{ success }}
    </UiAlert>

    <div v-if="loading" class="flex items-center justify-center py-16">
      <UiLoadingSpinner size="lg" />
    </div>

    <div v-else-if="compte" class="space-y-6">
      <!-- Info card -->
      <div
        class="p-6 rounded-lg border border-(--border-default)"
        :style="{ backgroundColor: 'var(--bg-card)', boxShadow: 'var(--shadow-sm)' }"
      >
        <div class="flex items-start justify-between mb-4">
          <h2 class="text-lg font-semibold text-(--text-primary)">Informations</h2>
          <div class="flex items-center gap-2">
            <UiButton v-if="!editing" variant="outline" size="sm" :icon="['fas', 'pen']" @click="startEditing">
              Modifier
            </UiButton>
          </div>
        </div>

        <!-- View mode -->
        <div v-if="!editing" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span class="text-sm text-(--text-muted)">Collectivite</span>
              <p class="text-(--text-primary) font-medium">{{ compte.collectivite_name }}</p>
            </div>
            <div>
              <span class="text-sm text-(--text-muted)">Type</span>
              <p>
                <UiBadge variant="gray">{{ compte.collectivite_type }}</UiBadge>
              </p>
            </div>
            <div>
              <span class="text-sm text-(--text-muted)">Annee d'exercice</span>
              <p class="text-(--text-primary) font-mono font-medium">{{ compte.annee_exercice }}</p>
            </div>
            <div>
              <span class="text-sm text-(--text-muted)">Statut</span>
              <div class="flex items-center gap-2 mt-1">
                <UiBadge :variant="compte.status === 'published' ? 'success' : 'warning'" dot>
                  {{ compte.status === 'published' ? 'Publie' : 'Brouillon' }}
                </UiBadge>
                <button
                  v-if="isAdmin"
                  class="text-xs px-2 py-0.5 rounded border border-(--border-default) text-(--text-secondary) hover:bg-(--interactive-hover) transition-colors"
                  :disabled="saving"
                  @click="toggleStatus"
                >
                  {{ compte.status === 'published' ? 'Repasser en brouillon' : 'Publier' }}
                </button>
              </div>
            </div>
            <div>
              <span class="text-sm text-(--text-muted)">Cree le</span>
              <p class="text-(--text-secondary) text-sm font-mono">{{ formatDate(compte.created_at) }}</p>
            </div>
            <div>
              <span class="text-sm text-(--text-muted)">Modifie le</span>
              <p class="text-(--text-secondary) text-sm font-mono">{{ formatDate(compte.updated_at) }}</p>
            </div>
          </div>
        </div>

        <!-- Edit mode -->
        <form v-else class="space-y-4" @submit.prevent="handleSave">
          <UiFormSelect
            v-model="collectiviteType"
            label="Type de collectivite"
            :options="collectiviteTypeOptions"
            required
          />
          <UiFormSelect
            v-model="selectedProvinceId"
            label="Province"
            :options="provinceOptions"
            placeholder="-- Choisir une province --"
            required
          />
          <UiFormSelect
            v-if="collectiviteType === 'region' || collectiviteType === 'commune'"
            v-model="selectedRegionId"
            label="Region"
            :options="regionOptions"
            :placeholder="regions.length === 0 ? 'Choisir une province d\'abord' : '-- Choisir une region --'"
            :disabled="regions.length === 0"
            required
          />
          <UiFormSelect
            v-if="collectiviteType === 'commune'"
            v-model="selectedCommuneId"
            label="Commune"
            :options="communeOptions"
            :placeholder="communes.length === 0 ? 'Choisir une region d\'abord' : '-- Choisir une commune --'"
            :disabled="communes.length === 0"
            required
          />
          <UiFormInput
            v-model="anneeExercice"
            type="number"
            label="Annee d'exercice"
            required
          />
          <div class="flex justify-end gap-2">
            <UiButton variant="ghost" type="button" @click="cancelEditing">
              Annuler
            </UiButton>
            <UiButton type="submit" :disabled="!canSubmit" :loading="saving" :icon="['fas', 'check']">
              Enregistrer
            </UiButton>
          </div>
        </form>
      </div>

      <!-- Actions rapides -->
      <div
        class="p-6 rounded-lg border border-(--border-default)"
        :style="{ backgroundColor: 'var(--bg-card)', boxShadow: 'var(--shadow-sm)' }"
      >
        <h2 class="text-lg font-semibold text-(--text-primary) mb-4">Donnees financieres</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <NuxtLink
            :to="`/admin/accounts/${compteId}/recettes`"
            class="flex items-center gap-3 p-4 rounded-lg border border-(--border-default) hover:border-(--color-primary) hover:bg-(--interactive-hover) transition-colors group"
          >
            <div class="w-10 h-10 rounded-lg flex items-center justify-center bg-(--color-success-light)">
              <font-awesome-icon :icon="['fas', 'arrow-trend-up']" class="text-(--color-success)" />
            </div>
            <div>
              <p class="font-medium text-(--text-primary) group-hover:text-(--color-primary)">Recettes</p>
              <p class="text-xs text-(--text-muted)">Consulter et saisir les recettes</p>
            </div>
          </NuxtLink>

          <NuxtLink
            :to="`/admin/accounts/${compteId}/depenses`"
            class="flex items-center gap-3 p-4 rounded-lg border border-(--border-default) hover:border-(--color-primary) hover:bg-(--interactive-hover) transition-colors group"
          >
            <div class="w-10 h-10 rounded-lg flex items-center justify-center bg-(--color-error-light)">
              <font-awesome-icon :icon="['fas', 'arrow-trend-down']" class="text-(--color-error)" />
            </div>
            <div>
              <p class="font-medium text-(--text-primary) group-hover:text-(--color-primary)">Depenses</p>
              <p class="text-xs text-(--text-muted)">Consulter et saisir les depenses</p>
            </div>
          </NuxtLink>

          <NuxtLink
            :to="`/admin/accounts/${compteId}/recap`"
            class="flex items-center gap-3 p-4 rounded-lg border border-(--border-default) hover:border-(--color-primary) hover:bg-(--interactive-hover) transition-colors group"
          >
            <div class="w-10 h-10 rounded-lg flex items-center justify-center bg-(--color-primary-light)">
              <font-awesome-icon :icon="['fas', 'scale-balanced']" class="text-(--color-primary)" />
            </div>
            <div>
              <p class="font-medium text-(--text-primary) group-hover:text-(--color-primary)">Recapitulatifs</p>
              <p class="text-xs text-(--text-muted)">Synthese et equilibre</p>
            </div>
          </NuxtLink>
        </div>
      </div>

      <!-- Programmes -->
      <div
        class="p-6 rounded-lg border border-(--border-default)"
        :style="{ backgroundColor: 'var(--bg-card)', boxShadow: 'var(--shadow-sm)' }"
      >
        <h2 class="text-lg font-semibold text-(--text-primary) mb-4">Programmes de depenses</h2>
        <div v-if="compte.programmes.length === 0" class="text-sm text-(--text-muted)">
          Aucun programme.
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="prog in compte.programmes"
            :key="prog.id"
            class="flex items-center justify-between p-3 rounded-md border border-(--border-light)"
          >
            <div>
              <span class="text-sm font-medium text-(--text-primary)">Programme {{ prog.numero }}</span>
              <span class="text-sm text-(--text-secondary) ml-2">{{ prog.intitule }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

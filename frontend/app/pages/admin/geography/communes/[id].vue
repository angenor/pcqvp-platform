<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const { createCommune, updateCommune, fetchCommuneDetail, fetchProvinces, fetchRegions } = useGeography()

const isNew = computed(() => route.params.id === 'new')
const loading = ref(!isNew.value)
const saving = ref(false)
const error = ref('')
const provinces = ref<any[]>([])
const regions = ref<any[]>([])
const selectedProvinceId = ref('')
const initialRegionId = ref('')

const form = ref({
  name: '',
  code: '',
  region_id: '',
  description_json: null as any,
})

const provinceOptions = computed(() =>
  provinces.value.map((p: any) => ({ value: p.id, label: p.name }))
)
const regionOptions = computed(() =>
  regions.value.map((r: any) => ({ value: r.id, label: r.name }))
)

watch(selectedProvinceId, async (provinceId) => {
  regions.value = []
  form.value.region_id = ''
  if (provinceId) {
    try {
      regions.value = await fetchRegions(provinceId)
      if (initialRegionId.value) {
        form.value.region_id = initialRegionId.value
        initialRegionId.value = ''
      }
    } catch {
      error.value = 'Impossible de charger les regions'
    }
  }
})

onMounted(async () => {
  try {
    provinces.value = await fetchProvinces()
  } catch {
    error.value = 'Impossible de charger les provinces'
  }

  if (!isNew.value) {
    try {
      const data = await fetchCommuneDetail(route.params.id as string)
      form.value = {
        name: data.name,
        code: data.code,
        region_id: data.region_id,
        description_json: data.description_json || [],
      }
      if (data.region_id) {
        const { fetchRegionDetail } = useGeography()
        const regionData = await fetchRegionDetail(data.region_id)
        if (regionData?.province_id) {
          initialRegionId.value = data.region_id
          selectedProvinceId.value = regionData.province_id
        }
      }
    } catch {
      error.value = 'Commune introuvable'
    } finally {
      loading.value = false
    }
  }
})

async function handleSubmit() {
  saving.value = true
  error.value = ''

  if (!form.value.region_id) {
    error.value = 'Veuillez selectionner une region'
    saving.value = false
    return
  }

  try {
    if (isNew.value) {
      await createCommune(form.value)
    } else {
      await updateCommune(route.params.id as string, form.value)
    }
    navigateTo('/admin/geography/communes')
  } catch (e: any) {
    const detail = e?.response?._data?.detail || e?.data?.detail || ''
    if (detail.includes('already exists')) {
      error.value = detail
    } else {
      error.value = 'Erreur lors de la sauvegarde'
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold mb-6 text-(--text-primary)">
      {{ isNew ? 'Nouvelle commune' : 'Modifier la commune' }}
    </h1>

    <div v-if="loading" class="text-center py-12">
      <UiLoadingSpinner size="lg" />
    </div>

    <template v-else>
      <UiAlert v-if="error" variant="error" class="mb-4" dismissible @dismiss="error = ''">
        {{ error }}
      </UiAlert>

      <form
        class="p-6 space-y-5 rounded-lg border border-(--border-default)"
        :style="{ backgroundColor: 'var(--bg-card)', boxShadow: 'var(--shadow-sm)' }"
        @submit.prevent="handleSubmit"
      >
        <UiFormInput v-model="form.name" label="Nom" required />
        <UiFormInput v-model="form.code" label="Code" required />

        <UiFormSelect
          v-model="selectedProvinceId"
          label="Province (filtre)"
          :options="provinceOptions"
          placeholder="-- Selectionner une province --"
        />

        <UiFormSelect
          v-model="form.region_id"
          label="Region"
          :options="regionOptions"
          placeholder="-- Selectionner une region --"
          required
          :disabled="!selectedProvinceId"
        />

        <div>
          <label class="block text-sm font-medium mb-1 text-(--text-secondary)">Description</label>
          <ClientOnly>
            <RichContentEditor v-model="form.description_json" />
            <template #fallback>
              <div class="h-50 rounded-lg flex items-center justify-center text-sm bg-(--interactive-hover) text-(--text-muted)">
                Chargement de l'editeur...
              </div>
            </template>
          </ClientOnly>
        </div>

        <div class="flex items-center gap-4 pt-2">
          <UiButton type="submit" :loading="saving" :icon="['fas', 'floppy-disk']">
            Enregistrer
          </UiButton>
          <UiButton variant="ghost" to="/admin/geography/communes">
            Annuler
          </UiButton>
        </div>
      </form>
    </template>
  </div>
</template>

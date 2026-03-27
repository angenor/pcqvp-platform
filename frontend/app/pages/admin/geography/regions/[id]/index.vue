<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const { createRegion, updateRegion, fetchRegionDetail, fetchProvinces } = useGeography()

const isNew = computed(() => route.params.id === 'new')
const loading = ref(!isNew.value)
const saving = ref(false)
const error = ref('')
const provinces = ref<any[]>([])

const form = ref({
  name: '',
  code: '',
  province_id: '',
  description_json: null as any,
})

const provinceOptions = computed(() =>
  provinces.value.map((p: any) => ({ value: p.id, label: p.name }))
)

onMounted(async () => {
  try {
    const data = await fetchProvinces()
    provinces.value = data
  } catch {
    error.value = 'Impossible de charger les provinces'
  }

  if (!isNew.value) {
    try {
      const data = await fetchRegionDetail(route.params.id as string)
      form.value = {
        name: data.name,
        code: data.code,
        province_id: data.province_id,
        description_json: data.description_json || [],
      }
    } catch {
      error.value = 'Region introuvable'
    } finally {
      loading.value = false
    }
  }
})

async function handleSubmit() {
  saving.value = true
  error.value = ''

  if (!form.value.province_id) {
    error.value = 'Veuillez selectionner une province'
    saving.value = false
    return
  }

  try {
    if (isNew.value) {
      await createRegion(form.value)
    } else {
      await updateRegion(route.params.id as string, form.value)
    }
    navigateTo('/admin/geography/regions')
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
      {{ isNew ? 'Nouvelle region' : 'Modifier la region' }}
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
          v-model="form.province_id"
          label="Province"
          :options="provinceOptions"
          placeholder="-- Selectionner une province --"
          required
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
          <UiButton variant="ghost" to="/admin/geography/regions">
            Annuler
          </UiButton>
          <UiButton
            v-if="!isNew"
            variant="ghost"
            :to="`/admin/accounts?collectivite_type=region&collectivite_id=${route.params.id}`"
            :icon="['fas', 'calculator']"
          >
            Voir les comptes
          </UiButton>
        </div>
      </form>
    </template>
  </div>
</template>

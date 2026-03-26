<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const { createProvince, updateProvince, fetchProvinceDetail } = useGeography()

const isNew = computed(() => route.params.id === 'new')
const loading = ref(!isNew.value)
const saving = ref(false)
const error = ref('')

const form = ref({
  name: '',
  code: '',
  description_json: null as any,
})

onMounted(async () => {
  if (!isNew.value) {
    try {
      const data = await fetchProvinceDetail(route.params.id as string)
      form.value = {
        name: data.name,
        code: data.code,
        description_json: data.description_json || [],
      }
    } catch {
      error.value = 'Province introuvable'
    } finally {
      loading.value = false
    }
  }
})

async function handleSubmit() {
  saving.value = true
  error.value = ''

  try {
    if (isNew.value) {
      await createProvince(form.value)
    } else {
      await updateProvince(route.params.id as string, form.value)
    }
    navigateTo('/admin/geography/provinces')
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
      {{ isNew ? 'Nouvelle province' : 'Modifier la province' }}
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
          <UiButton variant="ghost" to="/admin/geography/provinces">
            Annuler
          </UiButton>
        </div>
      </form>
    </template>
  </div>
</template>

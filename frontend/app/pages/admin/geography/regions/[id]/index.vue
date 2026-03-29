<script setup lang="ts">
import type { ImageVariants } from '~/types/api'

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
  banner_image: null as string | null,
})

const uploading = ref(false)
const token = useState<string | null>('access_token')
const bannerFile = ref<File | null>(null)
const showImageEditor = ref(false)

const provinceOptions = computed(() =>
  provinces.value.map((p: any) => ({ value: p.id, label: p.name }))
)

function handleFileSelect(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  bannerFile.value = file
  showImageEditor.value = true
}

async function uploadBlob(blob: Blob, suffix: string): Promise<string | null> {
  const formData = new FormData()
  formData.append('image', blob, `banner${suffix}.${blob.type.split('/')[1] || 'jpg'}`)
  const res = await $fetch<{ success: number; file: { url: string } }>('/api/admin/upload/image', {
    method: 'POST',
    body: formData,
    headers: { Authorization: `Bearer ${token.value}` },
  })
  return res.success ? res.file.url : null
}

async function handleEditorSave(variants: ImageVariants) {
  uploading.value = true
  showImageEditor.value = false
  try {
    const [_lowUrl, _mediumUrl, originalUrl] = await Promise.all([
      uploadBlob(variants.low, '-low'),
      uploadBlob(variants.medium, '-medium'),
      uploadBlob(variants.original, ''),
    ])
    if (originalUrl) {
      form.value.banner_image = originalUrl
    }
  } catch {
    error.value = "Erreur lors de l'upload de l'image"
  } finally {
    uploading.value = false
    bannerFile.value = null
  }
}

function handleEditorCancel() {
  showImageEditor.value = false
  bannerFile.value = null
}

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
        description_json: data.description_json || null,
        banner_image: data.banner_image || null,
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

        <div>
          <label class="block text-sm font-medium mb-1 text-(--text-secondary)">Image banniere</label>
          <div v-if="form.banner_image" class="mb-3">
            <img :src="form.banner_image" alt="Banniere" class="w-full h-40 object-cover rounded-lg border border-(--border-default)" />
            <button type="button" class="mt-2 text-sm text-red-600 dark:text-red-400 hover:underline" @click="form.banner_image = null">
              Supprimer l'image
            </button>
          </div>
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            class="block w-full text-sm text-(--text-secondary) file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-(--interactive-hover) file:text-(--text-primary) hover:file:bg-(--interactive-active)"
            :disabled="uploading"
            @change="handleFileSelect"
          />
          <p v-if="uploading" class="mt-1 text-sm text-(--text-muted)">Upload en cours...</p>
        </div>

        <UiModal v-model="showImageEditor" title="Editer l'image banniere" size="full" :closable="true" @close="handleEditorCancel">
          <ClientOnly>
            <ImageEditor
              v-if="bannerFile"
              :image-file="bannerFile"
              :generate-variants="true"
              @save="handleEditorSave"
              @cancel="handleEditorCancel"
            />
          </ClientOnly>
        </UiModal>

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

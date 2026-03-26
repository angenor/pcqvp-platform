<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

useHead({ title: 'Admin - Configuration' })

const { getConfig, updateConfig } = useSiteConfig()

const globalleaksUrl = ref('')
const loading = ref(true)
const saving = ref(false)
const saved = ref(false)

onMounted(async () => {
  try {
    const config = await getConfig('globalleaks_url')
    globalleaksUrl.value = config.value
  } catch {
    // Config might not exist yet
  } finally {
    loading.value = false
  }
})

async function handleSave() {
  saving.value = true
  saved.value = false
  try {
    await updateConfig('globalleaks_url', globalleaksUrl.value)
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6 text-(--text-primary)">Configuration</h1>

    <div v-if="loading" class="flex justify-center py-8">
      <UiLoadingSpinner size="lg" />
    </div>

    <div
      v-else
      class="max-w-xl p-6 rounded-lg border border-(--border-default)"
      :style="{ backgroundColor: 'var(--bg-card)' }"
    >
      <h2 class="text-lg font-semibold mb-4 text-(--text-primary)">GlobalLeaks</h2>

      <form @submit.prevent="handleSave">
        <UiFormInput
          v-model="globalleaksUrl"
          type="text"
          label="URL de l'instance GlobalLeaks"
          placeholder="https://globalleaks.example.com"
        />
        <p class="mt-1 text-xs text-(--text-muted)">
          Cette URL sera affichee sur la page publique "Signaler"
        </p>

        <div class="mt-4 flex items-center gap-3">
          <UiButton type="submit" :loading="saving" :icon="['fas', 'floppy-disk']">
            Enregistrer
          </UiButton>
          <UiAlert v-if="saved" variant="success" class="flex-1">
            Configuration sauvegardee
          </UiAlert>
        </div>
      </form>
    </div>
  </div>
</template>

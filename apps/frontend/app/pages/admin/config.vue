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
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Configuration</h1>

    <div v-if="loading" class="flex justify-center py-8">
      <div class="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>

    <div v-else class="max-w-xl bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">GlobalLeaks</h2>

      <form @submit.prevent="handleSave">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          URL de l'instance GlobalLeaks
        </label>
        <input
          v-model="globalleaksUrl"
          type="url"
          placeholder="https://globalleaks.example.com"
          class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
        />
        <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Cette URL sera affichee sur la page publique "Signaler"
        </p>

        <div class="mt-4 flex items-center gap-3">
          <button
            type="submit"
            :disabled="saving"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg disabled:opacity-50 transition-colors"
          >
            {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
          <span v-if="saved" class="text-sm text-green-600 dark:text-green-400">
            Configuration sauvegardee
          </span>
        </div>
      </form>
    </div>
  </div>
</template>

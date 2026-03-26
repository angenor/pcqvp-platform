<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

useHead({ title: 'Signaler - PCQVP Madagascar' })

const { getPublicGlobalLeaksUrl } = useSiteConfig()
const globalleaksUrl = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    globalleaksUrl.value = await getPublicGlobalLeaksUrl()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">
      Signalement anonyme
    </h1>

    <div class="prose dark:prose-invert max-w-none">
      <p class="text-lg text-gray-600 dark:text-gray-300 mb-6">
        Vous disposez d'informations sur des irregularites dans la gestion des industries extractives a Madagascar ?
        Vous pouvez les signaler de maniere anonyme et securisee via notre plateforme GlobalLeaks.
      </p>

      <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 mb-8">
        <h2 class="text-xl font-semibold text-blue-900 dark:text-blue-100 mb-4">
          Comment ca fonctionne ?
        </h2>
        <ol class="space-y-3 text-gray-700 dark:text-gray-300">
          <li class="flex gap-3">
            <span class="flex-shrink-0 w-7 h-7 bg-blue-100 dark:bg-blue-800 text-blue-600 dark:text-blue-300 rounded-full flex items-center justify-center text-sm font-bold">1</span>
            <span>Cliquez sur le bouton ci-dessous pour acceder a la plateforme securisee</span>
          </li>
          <li class="flex gap-3">
            <span class="flex-shrink-0 w-7 h-7 bg-blue-100 dark:bg-blue-800 text-blue-600 dark:text-blue-300 rounded-full flex items-center justify-center text-sm font-bold">2</span>
            <span>Remplissez le formulaire en decrivant la situation</span>
          </li>
          <li class="flex gap-3">
            <span class="flex-shrink-0 w-7 h-7 bg-blue-100 dark:bg-blue-800 text-blue-600 dark:text-blue-300 rounded-full flex items-center justify-center text-sm font-bold">3</span>
            <span>Votre signalement est transmis de maniere chiffree et anonyme</span>
          </li>
        </ol>
      </div>

      <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-8">
        <p class="text-sm text-yellow-800 dark:text-yellow-200">
          <strong>Votre anonymat est garanti.</strong> GlobalLeaks utilise le reseau Tor et le chiffrement de bout en bout.
          Aucune information permettant de vous identifier n'est collectee.
        </p>
      </div>

      <div v-if="loading" class="flex justify-center py-8">
        <div class="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>

      <div v-else class="text-center">
        <a
          v-if="globalleaksUrl"
          :href="globalleaksUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 px-8 py-4 text-lg font-medium text-white bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600 rounded-lg transition-colors"
        >
          Acceder a GlobalLeaks
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
            <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
          </svg>
        </a>
        <p v-else class="text-gray-500 dark:text-gray-400">
          La plateforme de signalement n'est pas encore configuree. Veuillez contacter l'administrateur.
        </p>
      </div>
    </div>
  </div>
</template>

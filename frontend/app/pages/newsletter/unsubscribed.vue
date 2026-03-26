<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

const route = useRoute()
const hasError = computed(() => route.query.error === 'invalid')

useHead({
  title: 'Newsletter - Desinscription',
})
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-16 text-center">
    <template v-if="hasError">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Lien invalide
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Le lien de desinscription est invalide.
      </p>
    </template>

    <template v-else>
      <div class="text-blue-500 dark:text-blue-400 mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Desinscription confirmee
      </h1>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Vous avez ete desinscrit de la newsletter PCQVP. Vous pouvez vous reinscrire a tout moment.
      </p>
      <NuxtLink
        to="/"
        class="inline-block px-6 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
      >
        Retour a l'accueil
      </NuxtLink>
    </template>
  </div>
</template>

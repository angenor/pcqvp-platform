<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

const route = useRoute()
const hasError = computed(() => route.query.error === 'invalid')

useHead({
  title: 'Newsletter - Confirmation',
})
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-16 text-center">
    <template v-if="hasError">
      <div class="text-red-500 dark:text-red-400 mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Lien invalide ou expire
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Le lien de confirmation est invalide ou a expire. Veuillez vous reinscrire.
      </p>
    </template>

    <template v-else>
      <div class="text-green-500 dark:text-green-400 mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Inscription confirmee
      </h1>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Votre inscription a la newsletter PCQVP a ete confirmee avec succes.
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

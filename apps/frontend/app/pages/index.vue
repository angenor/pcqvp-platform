<script setup lang="ts">
useSeoMeta({
  title: 'Plateforme de suivi des revenus miniers - PCQVP Madagascar',
  description: 'Consultez les comptes administratifs publies des collectivites territoriales malgaches. Transparence des industries extractives.',
  ogTitle: 'Plateforme de suivi des revenus miniers - PCQVP Madagascar',
  ogDescription: 'Consultez les comptes administratifs publies des collectivites territoriales malgaches.',
})

function handleGeoSubmit(selection: { type: string; id: string }) {
  navigateTo(`/collectivite/${selection.type}-${selection.id}`)
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header with theme toggle -->
    <header class="bg-white dark:bg-gray-800 shadow-sm">
      <div class="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-blue-600 dark:bg-blue-500 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-lg">TI</span>
          </div>
          <span class="text-sm text-gray-500 dark:text-gray-400">Transparency International Madagascar</span>
        </div>
        <button
          class="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          @click="useColorMode().preference = useColorMode().value === 'dark' ? 'light' : 'dark'"
        >
          <svg v-if="useColorMode().value === 'dark'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        </button>
      </div>
    </header>

    <!-- Main content -->
    <main class="max-w-4xl mx-auto px-4 py-12">
      <div class="text-center mb-10">
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white leading-tight">
          Plateforme de suivi des revenus miniers des collectivites territoriales
        </h1>
        <p class="mt-4 text-lg text-gray-600 dark:text-gray-400">
          Publiez Ce Que Vous Payez - Madagascar
        </p>
      </div>

      <div class="max-w-2xl mx-auto">
        <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
          Selectionnez une collectivite
        </h2>
        <GeographySelector :on-submit="handleGeoSubmit" />
      </div>

      <div class="mt-12 text-center text-sm text-gray-400 dark:text-gray-500">
        <p>Consultez les comptes administratifs publies des collectivites territoriales malgaches.</p>
      </div>
    </main>
  </div>
</template>

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
  <div>
    <!-- Main content -->
    <div class="max-w-4xl mx-auto px-4 py-12">
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
    </div>
  </div>
</template>

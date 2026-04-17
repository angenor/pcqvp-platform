<script setup lang="ts">
const route = useRoute()
const { fetchCommuneDetail, fetchRegionDetail } = useGeography()

const commune = ref<any>(null)
const parentRegion = ref<any>(null)
const error = ref(false)
const loading = ref(true)

onMounted(async () => {
  try {
    commune.value = await fetchCommuneDetail(route.params.id as string)
    if (commune.value?.region_id) {
      parentRegion.value = await fetchRegionDetail(commune.value.region_id)
    }
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <div v-if="loading" class="text-center text-gray-500 dark:text-gray-400">Chargement...</div>
      <div v-else-if="error" class="text-center">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Commune introuvable</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Cette commune n'existe pas.</p>
        <NuxtLink to="/" class="mt-4 inline-block text-blue-600 dark:text-blue-400 hover:underline">Retour a l'accueil</NuxtLink>
      </div>
      <div v-else>
        <!-- Breadcrumb -->
        <nav class="mb-6 text-sm text-gray-500 dark:text-gray-400">
          <template v-if="parentRegion?.province">
            <NuxtLink
              :to="`/provinces/${parentRegion.province.id}`"
              class="text-blue-600 dark:text-blue-400 hover:underline"
            >
              {{ parentRegion.province.name }}
            </NuxtLink>
            <span class="mx-2 text-gray-400 dark:text-gray-500">/</span>
          </template>
          <template v-if="parentRegion">
            <NuxtLink
              :to="`/regions/${parentRegion.id}`"
              class="text-blue-600 dark:text-blue-400 hover:underline"
            >
              {{ parentRegion.name }}
            </NuxtLink>
            <span class="mx-2 text-gray-400 dark:text-gray-500">/</span>
          </template>
          <span class="text-gray-700 dark:text-gray-300">{{ commune.name }}</span>
        </nav>

        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">{{ commune.name }}</h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Code : {{ commune.code }}</p>

        <CollectivityDocumentsList :documents="commune.documents ?? []" />

        <div class="mt-6">
          <RichContentRenderer :description-json="commune.description_json" />
        </div>
      </div>
    </div>
  </div>
</template>

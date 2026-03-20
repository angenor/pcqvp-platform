<script setup lang="ts">
const route = useRoute()
const { fetchRegionDetail, fetchProvinceDetail } = useGeography()

const region = ref<any>(null)
const parentProvince = ref<any>(null)
const error = ref(false)
const loading = ref(true)

onMounted(async () => {
  try {
    region.value = await fetchRegionDetail(route.params.id as string)
    if (region.value?.province_id) {
      parentProvince.value = await fetchProvinceDetail(region.value.province_id)
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
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Region introuvable</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Cette region n'existe pas.</p>
        <NuxtLink to="/" class="mt-4 inline-block text-blue-600 dark:text-blue-400 hover:underline">Retour a l'accueil</NuxtLink>
      </div>
      <div v-else>
        <!-- Breadcrumb -->
        <nav class="mb-6 text-sm text-gray-500 dark:text-gray-400">
          <template v-if="parentProvince">
            <NuxtLink
              :to="`/provinces/${parentProvince.id}`"
              class="text-blue-600 dark:text-blue-400 hover:underline"
            >
              {{ parentProvince.name }}
            </NuxtLink>
            <span class="mx-2 text-gray-400 dark:text-gray-500">/</span>
          </template>
          <span class="text-gray-700 dark:text-gray-300">{{ region.name }}</span>
        </nav>

        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">{{ region.name }}</h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Code : {{ region.code }}</p>

        <div class="mt-6">
          <RichContentRenderer :description-json="region.description_json" />
        </div>

        <div v-if="region.communes?.length" class="mt-8">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Communes ({{ region.communes.length }})</h2>
          <div class="grid gap-3">
            <NuxtLink
              v-for="commune in region.communes"
              :key="commune.id"
              :to="`/communes/${commune.id}`"
              class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
            >
              <span class="font-medium text-gray-900 dark:text-white">{{ commune.name }}</span>
              <span class="ml-2 text-sm text-gray-500 dark:text-gray-400">({{ commune.code }})</span>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

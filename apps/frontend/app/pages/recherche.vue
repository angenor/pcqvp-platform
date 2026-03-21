<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

const route = useRoute()
const { results, loading, search } = useSearch()

const query = computed(() => (route.query.q as string) || '')

watch(query, (q) => {
  if (q && q.length >= 2) {
    search(q, 20)
  }
}, { immediate: true })

useHead({
  title: computed(() => query.value ? `Recherche : ${query.value}` : 'Recherche'),
})
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
      <template v-if="query">Resultats pour "{{ query }}"</template>
      <template v-else>Recherche</template>
    </h1>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>

    <div v-else-if="!results || results.total === 0" class="text-center py-12">
      <p class="text-gray-500 dark:text-gray-400">
        <template v-if="query">Aucun resultat pour "{{ query }}"</template>
        <template v-else>Saisissez un terme de recherche</template>
      </p>
    </div>

    <template v-else>
      <!-- Collectivites -->
      <section v-if="results.results.collectivites?.length" class="mb-8">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Collectivites ({{ results.results.collectivites.length }})
        </h2>
        <div class="space-y-2">
          <NuxtLink
            v-for="item in results.results.collectivites"
            :key="item.id"
            :to="item.url"
            class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div>
                <span class="font-medium text-gray-900 dark:text-white">{{ item.name }}</span>
                <span v-if="item.parent_name" class="ml-2 text-sm text-gray-500 dark:text-gray-400">
                  {{ item.parent_name }}
                </span>
              </div>
              <span class="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 capitalize">
                {{ item.type }}
              </span>
            </div>
          </NuxtLink>
        </div>
      </section>

      <!-- Comptes -->
      <section v-if="results.results.comptes?.length">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Comptes administratifs ({{ results.results.comptes.length }})
        </h2>
        <div class="space-y-2">
          <NuxtLink
            v-for="item in results.results.comptes"
            :key="item.id"
            :to="item.url"
            class="block p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium text-gray-900 dark:text-white">{{ item.collectivite_name }}</span>
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ item.annee_exercice }}</span>
            </div>
          </NuxtLink>
        </div>
      </section>
    </template>
  </div>
</template>

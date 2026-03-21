<script setup lang="ts">
const { results, loading, debouncedSearch, clear } = useSearch()
const query = ref('')
const showDropdown = ref(false)
const searchBarRef = ref<HTMLDivElement | null>(null)

function onInput() {
  if (query.value.length >= 2) {
    showDropdown.value = true
    debouncedSearch(query.value)
  } else {
    showDropdown.value = false
    clear()
  }
}

function goToResults() {
  if (query.value.length >= 2) {
    showDropdown.value = false
    navigateTo(`/recherche?q=${encodeURIComponent(query.value)}`)
  }
}

function selectResult(url: string) {
  showDropdown.value = false
  query.value = ''
  clear()
  navigateTo(url)
}

function onClickOutside(e: MouseEvent) {
  if (searchBarRef.value && !searchBarRef.value.contains(e.target as Node)) {
    showDropdown.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div ref="searchBarRef" class="relative w-full max-w-md">
    <div class="relative">
      <input
        v-model="query"
        type="text"
        placeholder="Rechercher une collectivite, un compte..."
        class="w-full pl-10 pr-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
        @input="onInput"
        @keydown.enter="goToResults"
      />
      <svg
        class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-gray-500"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fill-rule="evenodd"
          d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
          clip-rule="evenodd"
        />
      </svg>
      <div v-if="loading" class="absolute right-3 top-1/2 -translate-y-1/2">
        <div class="h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    </div>

    <!-- Dropdown results -->
    <div
      v-if="showDropdown && results"
      class="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto"
    >
      <div v-if="results.total === 0" class="p-4 text-sm text-gray-500 dark:text-gray-400 text-center">
        Aucun resultat pour "{{ query }}"
      </div>

      <template v-else>
        <!-- Collectivites -->
        <div v-if="results.results.collectivites?.length" class="p-2">
          <p class="px-2 py-1 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">
            Collectivites
          </p>
          <button
            v-for="item in results.results.collectivites.slice(0, 5)"
            :key="item.id"
            class="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            @click="selectResult(item.url)"
          >
            <span class="text-gray-900 dark:text-gray-100">{{ item.name }}</span>
            <span class="ml-2 text-xs text-gray-500 dark:text-gray-400">
              {{ item.type }}
              <template v-if="item.parent_name"> - {{ item.parent_name }}</template>
            </span>
          </button>
        </div>

        <!-- Comptes -->
        <div v-if="results.results.comptes?.length" class="p-2 border-t border-gray-200 dark:border-gray-700">
          <p class="px-2 py-1 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">
            Comptes administratifs
          </p>
          <button
            v-for="item in results.results.comptes.slice(0, 5)"
            :key="item.id"
            class="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            @click="selectResult(item.url)"
          >
            <span class="text-gray-900 dark:text-gray-100">{{ item.collectivite_name }}</span>
            <span class="ml-2 text-xs text-gray-500 dark:text-gray-400">
              {{ item.annee_exercice }}
            </span>
          </button>
        </div>

        <!-- See all results -->
        <div class="p-2 border-t border-gray-200 dark:border-gray-700">
          <button
            class="w-full text-center px-3 py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
            @click="goToResults"
          >
            Voir tous les resultats
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

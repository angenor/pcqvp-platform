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
        class="w-full pl-10 pr-4 py-2 text-sm rounded-lg border border-(--border-default) outline-none transition-colors focus:ring-2 focus:ring-(--color-primary)/20 focus:border-(--border-focus)"
        :style="{ backgroundColor: 'var(--bg-input)', color: 'var(--text-primary)' }"
        @input="onInput"
        @keydown.enter="goToResults"
      />
      <font-awesome-icon
        :icon="['fas', 'magnifying-glass']"
        class="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-(--text-muted)"
      />
      <div v-if="loading" class="absolute right-3 top-1/2 -translate-y-1/2">
        <UiLoadingSpinner size="sm" />
      </div>
    </div>

    <!-- Dropdown results -->
    <div
      v-if="showDropdown && results"
      class="absolute top-full left-0 right-0 mt-1 border border-(--border-default) rounded-lg max-h-96 overflow-y-auto"
      :style="{ backgroundColor: 'var(--bg-card)', boxShadow: 'var(--shadow-lg)', zIndex: 'var(--z-dropdown)' }"
    >
      <div v-if="results.total === 0" class="p-4 text-sm text-(--text-muted) text-center">
        Aucun resultat pour "{{ query }}"
      </div>

      <template v-else>
        <div v-if="results.results.collectivites?.length" class="p-2">
          <p class="px-2 py-1 text-xs font-semibold uppercase text-(--text-muted)">
            Collectivites
          </p>
          <button
            v-for="item in results.results.collectivites.slice(0, 5)"
            :key="item.id"
            class="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-(--interactive-hover) transition-colors cursor-pointer"
            @click="selectResult(item.url)"
          >
            <span class="text-(--text-primary)">{{ item.name }}</span>
            <span class="ml-2 text-xs text-(--text-muted)">
              {{ item.type }}
              <template v-if="item.parent_name"> - {{ item.parent_name }}</template>
            </span>
          </button>
        </div>

        <div v-if="results.results.comptes?.length" class="p-2 border-t border-(--border-default)">
          <p class="px-2 py-1 text-xs font-semibold uppercase text-(--text-muted)">
            Comptes administratifs
          </p>
          <button
            v-for="item in results.results.comptes.slice(0, 5)"
            :key="item.id"
            class="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-(--interactive-hover) transition-colors cursor-pointer"
            @click="selectResult(item.url)"
          >
            <span class="text-(--text-primary)">{{ item.collectivite_name }}</span>
            <span class="ml-2 text-xs text-(--text-muted)">{{ item.annee_exercice }}</span>
          </button>
        </div>

        <div class="p-2 border-t border-(--border-default)">
          <button
            class="w-full text-center px-3 py-2 text-sm text-(--color-primary) hover:bg-(--interactive-hover) rounded-md transition-colors cursor-pointer"
            @click="goToResults"
          >
            Voir tous les resultats
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

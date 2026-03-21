<script setup lang="ts">
const colorMode = useColorMode()

function toggleTheme() {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors">
    <!-- Header -->
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <NuxtLink to="/" class="flex items-center gap-2">
            <span class="text-xl font-bold text-gray-900 dark:text-white">PCQVP</span>
            <span class="hidden sm:inline text-sm text-gray-500 dark:text-gray-400">Madagascar</span>
          </NuxtLink>

          <!-- Search -->
          <SearchBar class="hidden md:block mx-4" />

          <!-- Navigation -->
          <nav class="flex items-center gap-4">
            <NuxtLink
              to="/signaler"
              class="text-sm font-medium text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 transition-colors"
            >
              Signaler
            </NuxtLink>

            <button
              class="p-2 rounded-md text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              :title="colorMode.value === 'dark' ? 'Mode clair' : 'Mode sombre'"
              @click="toggleTheme"
            >
              <svg v-if="colorMode.value === 'dark'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            </button>
          </nav>
        </div>

        <!-- Mobile search -->
        <div class="md:hidden pb-3">
          <SearchBar />
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- About -->
          <div>
            <h3 class="text-sm font-semibold uppercase text-gray-900 dark:text-white mb-3">
              PCQVP Madagascar
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Plateforme de transparence des industries extractives de Madagascar.
            </p>
          </div>

          <!-- Links -->
          <div>
            <h3 class="text-sm font-semibold uppercase text-gray-900 dark:text-white mb-3">
              Liens
            </h3>
            <ul class="space-y-2">
              <li>
                <NuxtLink to="/signaler" class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                  Signaler
                </NuxtLink>
              </li>
            </ul>
          </div>

          <!-- Newsletter -->
          <div>
            <h3 class="text-sm font-semibold uppercase text-gray-900 dark:text-white mb-3">
              Newsletter
            </h3>
            <NewsletterForm />
          </div>
        </div>

        <div class="mt-8 pt-4 border-t border-gray-200 dark:border-gray-700 text-center">
          <p class="text-xs text-gray-500 dark:text-gray-400">
            &copy; {{ new Date().getFullYear() }} PCQVP Madagascar. Tous droits reserves.
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

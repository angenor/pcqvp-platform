<script setup lang="ts">
const { user, logout } = useAuth()
const colorMode = useColorMode()

function toggleTheme() {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}

const navItems = [
  { label: 'Tableau de bord', to: '/admin', icon: 'home' },
]

const geoNavItems = [
  { label: 'Provinces', to: '/admin/geography/provinces' },
  { label: 'Regions', to: '/admin/geography/regions' },
  { label: 'Communes', to: '/admin/geography/communes' },
]

const templateNavItems = [
  { label: 'Templates', to: '/admin/templates' },
]

const comptesNavItems = [
  { label: 'Comptes administratifs', to: '/admin/accounts' },
]

const toolsNavItems = [
  { label: 'Utilisateurs', to: '/admin/users' },
  { label: 'Newsletter', to: '/admin/newsletter' },
  { label: 'Analytics', to: '/admin/analytics' },
  { label: 'Configuration', to: '/admin/config' },
]
</script>

<template>
  <div class="min-h-screen flex bg-gray-100 dark:bg-gray-900 transition-colors">
    <!-- Sidebar -->
    <aside class="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">PCQVP</h2>
        <p class="text-xs text-gray-500 dark:text-gray-400">Administration</p>
      </div>

      <nav class="flex-1 p-4 space-y-1">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          active-class="bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
        >
          {{ item.label }}
        </NuxtLink>

        <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p class="px-3 mb-2 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Geographie</p>
          <NuxtLink
            v-for="item in geoNavItems"
            :key="item.to"
            :to="item.to"
            class="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            active-class="bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
          >
            {{ item.label }}
          </NuxtLink>
        </div>

        <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p class="px-3 mb-2 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Comptes</p>
          <NuxtLink
            v-for="item in templateNavItems"
            :key="item.to"
            :to="item.to"
            class="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            active-class="bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
          >
            {{ item.label }}
          </NuxtLink>
          <NuxtLink
            v-for="item in comptesNavItems"
            :key="item.to"
            :to="item.to"
            class="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            active-class="bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
          >
            {{ item.label }}
          </NuxtLink>
        </div>

        <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p class="px-3 mb-2 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Outils</p>
          <NuxtLink
            v-for="item in toolsNavItems"
            :key="item.to"
            :to="item.to"
            class="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            active-class="bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
          >
            {{ item.label }}
          </NuxtLink>
        </div>
      </nav>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col">
      <!-- Header -->
      <header class="h-14 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6">
        <div />
        <div class="flex items-center gap-4">
          <!-- Theme toggle -->
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

          <!-- User info -->
          <span class="text-sm text-gray-600 dark:text-gray-300">
            {{ user?.email }}
          </span>

          <!-- Logout -->
          <button
            class="text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 transition-colors"
            @click="logout"
          >
            Deconnexion
          </button>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

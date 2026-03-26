<script setup lang="ts">
defineProps<{
  sidebarCollapsed: boolean
}>()

const emit = defineEmits<{
  'toggle-sidebar': []
}>()

const { user, logout } = useAuth()
const colorMode = useColorMode()

function toggleTheme() {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<template>
  <header
    class="fixed top-0 right-0 flex items-center justify-between px-4 md:px-6 border-b border-[var(--border-default)] transition-all duration-300 ease-in-out"
    :style="{
      height: 'var(--header-height)',
      left: sidebarCollapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)',
      backgroundColor: 'var(--bg-header)',
      zIndex: 'var(--z-sticky)',
    }"
  >
    <div class="flex items-center gap-4">
      <!-- Mobile hamburger -->
      <button
        class="p-2 rounded-[var(--radius-sm)] text-[var(--text-secondary)] hover:bg-[var(--interactive-hover)] transition-colors cursor-pointer lg:hidden"
        @click="emit('toggle-sidebar')"
      >
        <font-awesome-icon :icon="['fas', 'bars']" />
      </button>

      <AdminBreadcrumb />
    </div>

    <div class="flex items-center gap-3">
      <!-- Theme toggle -->
      <button
        class="p-2 rounded-[var(--radius-sm)] text-[var(--text-secondary)] hover:bg-[var(--interactive-hover)] transition-colors cursor-pointer"
        :title="colorMode.value === 'dark' ? 'Mode clair' : 'Mode sombre'"
        @click="toggleTheme"
      >
        <font-awesome-icon :icon="['fas', colorMode.value === 'dark' ? 'sun' : 'moon']" />
      </button>

      <!-- User email -->
      <span class="text-sm text-[var(--text-secondary)] hidden sm:inline">
        {{ user?.email }}
      </span>

      <!-- Logout -->
      <button
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)] text-sm text-[var(--color-error)] hover:bg-[var(--color-error-light)] transition-colors cursor-pointer"
        @click="logout"
      >
        <font-awesome-icon :icon="['fas', 'right-from-bracket']" class="text-xs" />
        <span class="hidden sm:inline">Deconnexion</span>
      </button>
    </div>
  </header>
</template>

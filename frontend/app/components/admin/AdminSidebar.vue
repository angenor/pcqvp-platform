<script setup lang="ts">
interface MenuItem {
  label: string
  to: string
  icon: string[]
}

interface MenuGroup {
  title: string
  items: MenuItem[]
}

const props = defineProps<{
  collapsed: boolean
}>()

const emit = defineEmits<{
  toggle: []
}>()

const route = useRoute()
const { isMobileOpen, closeMobile } = useSidebar()

const menuGroups: MenuGroup[] = [
  {
    title: '',
    items: [
      { label: 'Tableau de bord', to: '/admin', icon: ['fas', 'home'] },
    ],
  },
  {
    title: 'Geographie',
    items: [
      { label: 'Provinces', to: '/admin/geography/provinces', icon: ['fas', 'map'] },
      { label: 'Regions', to: '/admin/geography/regions', icon: ['fas', 'map-marked'] },
      { label: 'Communes', to: '/admin/geography/communes', icon: ['fas', 'city'] },
    ],
  },
  {
    title: 'Comptes',
    items: [
      { label: 'Templates', to: '/admin/templates', icon: ['fas', 'file-alt'] },
      { label: 'Comptes administratifs', to: '/admin/accounts', icon: ['fas', 'calculator'] },
    ],
  },
  {
    title: 'Outils',
    items: [
      { label: 'Éditoriaux', to: '/admin/editorial', icon: ['fas', 'pen-to-square'] },
      { label: 'Utilisateurs', to: '/admin/users', icon: ['fas', 'users'] },
      { label: 'Newsletter', to: '/admin/newsletter', icon: ['fas', 'envelope'] },
      { label: 'Analytics', to: '/admin/analytics', icon: ['fas', 'chart-bar'] },
      { label: 'Configuration', to: '/admin/config', icon: ['fas', 'cog'] },
    ],
  },
]

function isActive(to: string): boolean {
  if (to === '/admin') {
    return route.path === '/admin' || route.path === '/admin/'
  }
  return route.path.startsWith(to)
}
</script>

<template>
  <!-- Mobile overlay -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="isMobileOpen"
        class="fixed inset-0 bg-black/50 lg:hidden"
        :style="{ zIndex: 'var(--z-modal-backdrop)' }"
        @click="closeMobile"
      />
    </Transition>
  </Teleport>

  <aside
    class="fixed top-0 left-0 h-full flex flex-col border-r border-[var(--border-default)] transition-all duration-300 ease-in-out"
    :class="[
      isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
    ]"
    :style="{
      width: collapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)',
      backgroundColor: 'var(--bg-sidebar)',
      zIndex: 'var(--z-sticky)',
    }"
  >
    <!-- Header -->
    <div
      class="flex items-center border-b border-[var(--border-default)] px-4"
      :class="collapsed ? 'justify-center' : 'justify-between'"
      :style="{ height: 'var(--header-height)' }"
    >
      <div v-if="!collapsed" class="flex items-center gap-2">
        <span class="font-heading text-xl font-bold text-[var(--color-primary)] uppercase">PCQVP</span>
      </div>
      <button
        class="p-1.5 rounded-[var(--radius-sm)] text-[var(--text-secondary)] hover:bg-[var(--interactive-hover)] transition-colors cursor-pointer hidden lg:block"
        :title="collapsed ? 'Deplier' : 'Replier'"
        @click="emit('toggle')"
      >
        <font-awesome-icon :icon="['fas', collapsed ? 'angles-right' : 'angles-left']" class="text-sm" />
      </button>
      <!-- Mobile close button -->
      <button
        class="p-1.5 rounded-[var(--radius-sm)] text-[var(--text-secondary)] hover:bg-[var(--interactive-hover)] transition-colors cursor-pointer lg:hidden"
        @click="closeMobile"
      >
        <font-awesome-icon :icon="['fas', 'xmark']" />
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-3 px-2">
      <div v-for="(group, gIdx) in menuGroups" :key="gIdx" :class="gIdx > 0 ? 'mt-4' : ''">
        <p
          v-if="group.title && !collapsed"
          class="px-3 mb-1.5 text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]"
        >
          {{ group.title }}
        </p>
        <div v-if="group.title && collapsed" class="mb-1 border-t border-[var(--border-default)] mx-2" />

        <NuxtLink
          v-for="item in group.items"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-sm font-medium transition-colors cursor-pointer"
          :class="[
            isActive(item.to)
              ? 'bg-[var(--interactive-selected)] text-[var(--color-primary)]'
              : 'text-[var(--text-secondary)] hover:bg-[var(--interactive-hover)] hover:text-[var(--text-primary)]',
            collapsed ? 'justify-center' : '',
          ]"
          :title="collapsed ? item.label : undefined"
          @click="closeMobile"
        >
          <font-awesome-icon :icon="item.icon" class="w-5 shrink-0 text-center" />
          <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
        </NuxtLink>
      </div>
    </nav>

    <!-- Footer -->
    <div
      v-if="!collapsed"
      class="border-t border-[var(--border-default)] p-4"
    >
      <p class="text-xs text-[var(--text-muted)]">Plateforme PCQVP</p>
    </div>
  </aside>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<script setup lang="ts">
const { isCollapsed, toggle, openMobile } = useSidebar()
</script>

<template>
  <div class="min-h-screen" :style="{ backgroundColor: 'var(--bg-page)' }">
    <!-- Sidebar -->
    <AdminSidebar :collapsed="isCollapsed" @toggle="toggle" />

    <!-- Main content -->
    <div
      class="min-h-screen flex flex-col transition-all duration-300 ease-in-out"
      :style="{ marginLeft: isCollapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)' }"
    >
      <!-- Header -->
      <AdminHeader :sidebar-collapsed="isCollapsed" @toggle-sidebar="openMobile" />

      <!-- Page content -->
      <main
        class="flex-1 p-4 md:p-6"
        :style="{ marginTop: 'var(--header-height)' }"
      >
        <slot />
      </main>
    </div>
  </div>
</template>

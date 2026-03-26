<script setup lang="ts">
const route = useRoute()

const segmentLabels: Record<string, string> = {
  admin: 'Administration',
  geography: 'Geographie',
  provinces: 'Provinces',
  regions: 'Regions',
  communes: 'Communes',
  accounts: 'Comptes administratifs',
  templates: 'Templates',
  users: 'Utilisateurs',
  newsletter: 'Newsletter',
  analytics: 'Analytics',
  config: 'Configuration',
  new: 'Nouveau',
  recettes: 'Recettes',
  depenses: 'Depenses',
  recap: 'Recapitulatif',
}

const breadcrumbs = computed(() => {
  const path = route.path
  const segments = path.split('/').filter(Boolean)
  const items: { label: string; to?: string }[] = []

  let currentPath = ''
  for (let i = 0; i < segments.length; i++) {
    const segment = segments[i]
    currentPath += `/${segment}`

    // Skip dynamic segments (UUIDs)
    const isUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(segment)
    if (isUUID) continue

    const label = segmentLabels[segment] ?? segment.charAt(0).toUpperCase() + segment.slice(1)
    const isLast = i === segments.length - 1

    items.push({
      label,
      to: isLast ? undefined : currentPath,
    })
  }

  return items
})
</script>

<template>
  <nav class="flex items-center gap-1.5 text-sm" aria-label="Fil d'Ariane">
    <template v-for="(item, index) in breadcrumbs" :key="index">
      <span v-if="index > 0" class="text-[var(--text-muted)]">/</span>
      <NuxtLink
        v-if="item.to"
        :to="item.to"
        class="text-[var(--text-secondary)] hover:text-[var(--color-primary)] transition-colors"
      >
        {{ item.label }}
      </NuxtLink>
      <span v-else class="text-[var(--text-primary)] font-medium">
        {{ item.label }}
      </span>
    </template>
  </nav>
</template>

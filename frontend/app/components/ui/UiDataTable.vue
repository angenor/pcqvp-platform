<script setup lang="ts">
interface Column {
  key: string
  label: string
  sortable?: boolean
  align?: 'left' | 'center' | 'right'
}

const props = defineProps<{
  columns: Column[]
  data: any[]
  loading?: boolean
  searchable?: boolean
  searchPlaceholder?: string
  sortable?: boolean
  emptyIcon?: string[]
  emptyMessage?: string
  pagination?: boolean
  pageSize?: number
  rowLink?: (row: any) => string | undefined
}>()

const emit = defineEmits<{
  search: [query: string]
  sort: [key: string, direction: 'asc' | 'desc']
  'page-change': [page: number]
}>()

const searchQuery = ref('')
const sortKey = ref('')
const sortDirection = ref<'asc' | 'desc'>('asc')
const currentPage = ref(1)

const effectivePageSize = computed(() => props.pageSize ?? 20)
const showSearch = computed(() => props.searchable !== false)
const showPagination = computed(() => props.pagination !== false)

const filteredData = computed(() => {
  let result = [...props.data]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(row =>
      props.columns.some(col => {
        const val = row[col.key]
        return val != null && String(val).toLowerCase().includes(q)
      })
    )
  }

  if (sortKey.value) {
    result.sort((a, b) => {
      const aVal = a[sortKey.value] ?? ''
      const bVal = b[sortKey.value] ?? ''
      const cmp = String(aVal).localeCompare(String(bVal), undefined, { numeric: true })
      return sortDirection.value === 'asc' ? cmp : -cmp
    })
  }

  return result
})

const totalPages = computed(() =>
  showPagination.value ? Math.ceil(filteredData.value.length / effectivePageSize.value) : 1
)

const paginatedData = computed(() => {
  if (!showPagination.value) return filteredData.value
  const start = (currentPage.value - 1) * effectivePageSize.value
  return filteredData.value.slice(start, start + effectivePageSize.value)
})

function handleSort(col: Column) {
  if (!col.sortable && props.sortable === false) return
  if (sortKey.value === col.key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = col.key
    sortDirection.value = 'asc'
  }
  emit('sort', sortKey.value, sortDirection.value)
}

function handleSearch() {
  currentPage.value = 1
  emit('search', searchQuery.value)
}

function goToPage(page: number) {
  currentPage.value = page
  emit('page-change', page)
}

watch(searchQuery, handleSearch)

const router = useRouter()

function onRowClick(row: any) {
  if (props.rowLink) {
    const link = props.rowLink(row)
    if (link) router.push(link)
  }
}

const alignClass = (align?: string) => {
  if (align === 'center') return 'text-center'
  if (align === 'right') return 'text-right'
  return 'text-left'
}
</script>

<template>
  <div
    class="rounded-lg border border-(--border-default) overflow-hidden"
    :style="{ backgroundColor: 'var(--bg-card)' }"
  >
    <!-- Toolbar -->
    <div v-if="showSearch || $slots.toolbar" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 border-b border-(--border-default)">
      <div v-if="showSearch" class="relative w-full sm:max-w-xs">
        <font-awesome-icon :icon="['fas', 'magnifying-glass']" class="absolute left-3 top-1/2 -translate-y-1/2 text-(--text-muted) text-sm" />
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="searchPlaceholder ?? 'Rechercher...'"
          class="w-full pl-9 pr-3 py-2 text-sm border border-(--border-default) rounded-md outline-none transition-colors focus:ring-2 focus:ring-(--color-primary)/20 focus:border-(--border-focus)"
          :style="{ backgroundColor: 'var(--bg-input)', color: 'var(--text-primary)' }"
        />
      </div>
      <div v-if="$slots.toolbar">
        <slot name="toolbar" />
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="p-4 space-y-3">
      <div v-for="i in 5" :key="i" class="animate-pulse flex gap-4">
        <div v-for="j in columns.length" :key="j" class="h-4 rounded flex-1 bg-(--interactive-hover)" />
      </div>
    </div>

    <!-- Table -->
    <div v-else-if="paginatedData.length > 0" class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b border-(--border-default) bg-(--interactive-hover)">
            <th
              v-for="col in columns"
              :key="col.key"
              class="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-(--text-secondary)"
              :class="[alignClass(col.align), col.sortable !== false ? 'cursor-pointer select-none hover:text-(--text-primary)' : '']"
              @click="col.sortable !== false && handleSort(col)"
            >
              <div class="flex items-center gap-1" :class="col.align === 'right' ? 'justify-end' : col.align === 'center' ? 'justify-center' : ''">
                {{ col.label }}
                <template v-if="col.sortable !== false && sortKey === col.key">
                  <font-awesome-icon :icon="['fas', sortDirection === 'asc' ? 'sort-up' : 'sort-down']" class="text-xs text-(--color-primary)" />
                </template>
              </div>
            </th>
            <th v-if="$slots.actions" class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-(--text-secondary)">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, idx) in paginatedData"
            :key="idx"
            class="border-b border-(--border-default) last:border-b-0 hover:bg-(--interactive-hover) transition-colors"
            :class="{ 'cursor-pointer': !!rowLink }"
            @click="onRowClick(row)"
          >
            <td
              v-for="col in columns"
              :key="col.key"
              class="px-4 py-3 text-sm"
              :class="[alignClass(col.align)]"
              :style="{ color: 'var(--text-primary)' }"
            >
              <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
                {{ row[col.key] ?? '-' }}
              </slot>
            </td>
            <td v-if="$slots.actions" class="px-4 py-3 text-right">
              <slot name="actions" :row="row" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-12 text-center">
      <font-awesome-icon
        :icon="emptyIcon ?? ['fas', 'inbox']"
        class="text-4xl mb-3 text-(--text-muted)"
      />
      <p class="text-sm text-(--text-muted)">{{ emptyMessage ?? 'Aucune donnee' }}</p>
      <div v-if="$slots['empty-action']" class="mt-4">
        <slot name="empty-action" />
      </div>
    </div>

    <!-- Pagination -->
    <div
      v-if="showPagination && totalPages > 1"
      class="flex items-center justify-between px-4 py-3 border-t border-(--border-default)"
    >
      <p class="text-sm text-(--text-muted)">
        Page {{ currentPage }} sur {{ totalPages }} ({{ filteredData.length }} resultats)
      </p>
      <div class="flex gap-1">
        <button
          :disabled="currentPage <= 1"
          class="px-3 py-1 text-sm rounded-md border border-(--border-default) text-(--text-secondary) hover:bg-(--interactive-hover) disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer"
          @click="goToPage(currentPage - 1)"
        >
          Precedent
        </button>
        <button
          :disabled="currentPage >= totalPages"
          class="px-3 py-1 text-sm rounded-md border border-(--border-default) text-(--text-secondary) hover:bg-(--interactive-hover) disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer"
          @click="goToPage(currentPage + 1)"
        >
          Suivant
        </button>
      </div>
    </div>
  </div>
</template>

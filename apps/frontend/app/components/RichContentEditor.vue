<script setup lang="ts">
import type { EditorJSData } from '~/types/geography'

const model = defineModel<EditorJSData | null>({ default: null })

let editorInstance: any = null
const editorHolder = ref<HTMLElement>()
const isReady = ref(false)

onMounted(async () => {
  if (!editorHolder.value) return

  const EditorJS = (await import('@editorjs/editorjs')).default
  const Header = (await import('@editorjs/header')).default
  const ImageTool = (await import('@editorjs/image')).default
  const Table = (await import('@editorjs/table')).default
  const List = (await import('@editorjs/list')).default

  editorInstance = new EditorJS({
    holder: editorHolder.value,
    data: model.value || { blocks: [] },
    placeholder: 'Commencez à rédiger le contenu...',
    tools: {
      header: {
        class: Header,
        config: {
          levels: [2, 3, 4],
          defaultLevel: 2,
        },
      },
      image: {
        class: ImageTool,
        config: {
          endpoints: {
            byFile: '/api/admin/upload/image',
            byUrl: '/api/admin/upload/image-by-url',
          },
          field: 'image',
        },
      },
      table: {
        class: Table,
        inlineToolbar: true,
      },
      list: {
        class: List,
        inlineToolbar: true,
      },
    },
    onChange: async () => {
      if (editorInstance) {
        const data = await editorInstance.save()
        model.value = data
      }
    },
    onReady: () => {
      isReady.value = true
    },
  })
})

onBeforeUnmount(() => {
  if (editorInstance) {
    editorInstance.destroy()
    editorInstance = null
  }
})
</script>

<template>
  <div
    class="rich-content-editor min-h-50 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 px-4 py-2"
  >
    <div ref="editorHolder" />
    <p
      v-if="!isReady"
      class="text-sm text-gray-400 dark:text-gray-500 italic py-4 text-center"
    >
      Chargement de l'éditeur...
    </p>
  </div>
</template>

<style>
/* EditorJS dark mode styles */
.dark .codex-editor .ce-block__content,
.dark .codex-editor .ce-toolbar__content {
  max-width: 100%;
}

.dark .ce-block__content {
  color: #e5e7eb;
}

.dark .ce-paragraph[data-placeholder]:empty::before {
  color: #6b7280;
}

.dark .ce-header {
  color: #f3f4f6;
}

.dark .ce-toolbar__plus,
.dark .ce-toolbar__settings-btn {
  color: #9ca3af;
  background: #374151;
}

.dark .ce-toolbar__plus:hover,
.dark .ce-toolbar__settings-btn:hover {
  background: #4b5563;
}

.dark .ce-inline-toolbar {
  background: #1f2937;
  border-color: #4b5563;
  color: #e5e7eb;
}

.dark .ce-inline-toolbar__dropdown {
  border-color: #4b5563;
}

.dark .ce-inline-tool:hover {
  background: #374151;
}

.dark .ce-conversion-toolbar {
  background: #1f2937;
  border-color: #4b5563;
}

.dark .ce-conversion-tool:hover {
  background: #374151;
}

.dark .ce-conversion-tool__icon {
  background: #374151;
}

.dark .ce-settings {
  background: #1f2937;
  border-color: #4b5563;
}

.dark .ce-settings__button:hover {
  background: #374151;
}

.dark .ce-popover {
  background: #1f2937;
  border-color: #4b5563;
}

.dark .ce-popover-item:hover {
  background: #374151;
}

.dark .ce-popover-item__icon {
  background: #374151;
  color: #e5e7eb;
}

.dark .ce-popover-item__title {
  color: #e5e7eb;
}

.dark .cdx-search-field {
  background: #374151;
  border-color: #4b5563;
  color: #e5e7eb;
}

/* Table dark mode */
.dark .tc-table {
  border-color: #4b5563;
}

.dark .tc-row {
  border-color: #4b5563;
}

.dark .tc-cell {
  border-color: #4b5563;
  color: #e5e7eb;
}

.dark .tc-cell--selected {
  background: #374151;
}

.dark .tc-add-column,
.dark .tc-add-row {
  color: #9ca3af;
  border-color: #4b5563;
}

.dark .tc-add-column:hover,
.dark .tc-add-row:hover {
  background: #374151;
}

/* Image tool dark mode */
.dark .image-tool__caption {
  background: #374151;
  border-color: #4b5563;
  color: #e5e7eb;
}

.dark .cdx-input {
  background: #374151;
  border-color: #4b5563;
  color: #e5e7eb;
}

/* List dark mode */
.dark .cdx-list__item {
  color: #e5e7eb;
}
</style>

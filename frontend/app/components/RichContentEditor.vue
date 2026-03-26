<script setup lang="ts">
import EditorJS, { type OutputData, type BlockTune, type API } from '@editorjs/editorjs'
import Header from '@editorjs/header'
import List from '@editorjs/list'
import Quote from '@editorjs/quote'
import Embed from '@editorjs/embed'
import Table from '@editorjs/table'
import Delimiter from '@editorjs/delimiter'
import Marker from '@editorjs/marker'
import InlineCode from '@editorjs/inline-code'
import Paragraph from '@editorjs/paragraph'
import ImageTool from '@editorjs/image'
import Checklist from '@editorjs/checklist'

// Custom Block Tune for image positioning (float left/right)
class ImagePositionTune implements BlockTune {
  private api: API
  private data: { position: 'center' | 'left' | 'right' }
  private blockHolder: HTMLElement | null = null

  static get isTune() {
    return true
  }

  constructor({ api, data }: { api: API; block: { id: string }; data?: { position?: string } }) {
    this.api = api
    this.data = {
      position: (data?.position as 'center' | 'left' | 'right') || 'center',
    }
  }

  render() {
    const wrapper = document.createElement('div')
    wrapper.classList.add('ce-popover-item-container')

    const positions = [
      { value: 'center', label: 'Centré', icon: '⬜' },
      { value: 'left', label: 'Flottant gauche', icon: '◧' },
      { value: 'right', label: 'Flottant droite', icon: '◨' },
    ]

    positions.forEach((pos) => {
      const button = document.createElement('button')
      button.type = 'button'
      button.classList.add('ce-popover-item')
      if (this.data.position === pos.value) {
        button.classList.add('ce-popover-item--active')
      }
      button.innerHTML = `
        <span class="ce-popover-item__icon">${pos.icon}</span>
        <span class="ce-popover-item__title">${pos.label}</span>
      `
      button.addEventListener('click', () => {
        this.data.position = pos.value as 'center' | 'left' | 'right'
        this.applyClass()
        wrapper.querySelectorAll('.ce-popover-item').forEach((btn) => {
          btn.classList.remove('ce-popover-item--active')
        })
        button.classList.add('ce-popover-item--active')
        this.api.saver.save()
      })
      wrapper.appendChild(button)
    })

    return wrapper
  }

  private applyClass() {
    if (!this.blockHolder) return

    this.blockHolder.classList.remove('image-float-left', 'image-float-right', 'image-center')
    if (this.data.position === 'left') {
      this.blockHolder.classList.add('image-float-left')
    }
    else if (this.data.position === 'right') {
      this.blockHolder.classList.add('image-float-right')
    }
    else {
      this.blockHolder.classList.add('image-center')
    }
  }

  wrap(blockContent: HTMLElement) {
    setTimeout(() => {
      this.blockHolder = blockContent.closest('.ce-block') as HTMLElement
      this.applyClass()
    }, 0)
    return blockContent
  }

  save() {
    return this.data
  }
}

interface Props {
  modelValue?: OutputData | null
  placeholder?: string
  readOnly?: boolean
  minHeight?: number
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  placeholder: 'Commencez à écrire ou appuyez sur Tab pour choisir un bloc...',
  readOnly: false,
  minHeight: 300,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: OutputData): void
  (e: 'ready'): void
  (e: 'change', value: OutputData): void
}>()

const editorContainer = ref<HTMLElement | null>(null)
let editor: EditorJS | null = null

const getInitialData = (): OutputData | undefined => {
  if (!props.modelValue) return undefined
  if (typeof props.modelValue === 'object' && props.modelValue.blocks) {
    return props.modelValue
  }
  return undefined
}

onMounted(async () => {
  if (!editorContainer.value) return

  const initialData = getInitialData()

  editor = new EditorJS({
    holder: editorContainer.value,
    placeholder: props.placeholder,
    readOnly: props.readOnly,
    minHeight: props.minHeight,
    data: initialData,
    i18n: {
      messages: {
        ui: {
          blockTunes: {
            toggler: {
              'Click to tune': 'Cliquez pour configurer',
              'or drag to move': 'ou glissez pour déplacer',
            },
          },
          inlineToolbar: {
            converter: {
              'Convert to': 'Convertir en',
            },
          },
          toolbar: {
            toolbox: {
              Add: 'Ajouter',
            },
          },
        },
        toolNames: {
          Text: 'Texte',
          Heading: 'Titre',
          List: 'Liste',
          Checklist: 'Liste de tâches',
          Quote: 'Citation',
          Delimiter: 'Séparateur',
          Table: 'Tableau',
          Image: 'Image',
          Embed: 'Vidéo intégrée',
        },
        tools: {
          header: {
            'Heading 2': 'Titre 2',
            'Heading 3': 'Titre 3',
            'Heading 4': 'Titre 4',
          },
          list: {
            Unordered: 'Liste à puces',
            Ordered: 'Liste numérotée',
          },
          table: {
            'Add row above': 'Ajouter une ligne au-dessus',
            'Add row below': 'Ajouter une ligne en-dessous',
            'Delete row': 'Supprimer la ligne',
            'Add column to left': 'Ajouter une colonne à gauche',
            'Add column to right': 'Ajouter une colonne à droite',
            'Delete column': 'Supprimer la colonne',
            'With headings': 'Avec en-têtes',
            'Without headings': 'Sans en-têtes',
          },
        },
        blockTunes: {
          delete: {
            Delete: 'Supprimer',
          },
          moveUp: {
            'Move up': 'Déplacer vers le haut',
          },
          moveDown: {
            'Move down': 'Déplacer vers le bas',
          },
        },
      },
    },
    tools: {
      header: {
        class: Header,
        inlineToolbar: true,
        config: {
          placeholder: 'Titre',
          levels: [2, 3, 4],
          defaultLevel: 2,
        },
      },
      paragraph: {
        class: Paragraph,
        inlineToolbar: true,
      },
      list: {
        class: List,
        inlineToolbar: true,
        config: {
          defaultStyle: 'unordered',
        },
      },
      quote: {
        class: Quote,
        inlineToolbar: true,
        config: {
          quotePlaceholder: 'Citation',
          captionPlaceholder: 'Auteur',
        },
      },
      embed: {
        class: Embed,
        config: {
          services: {
            youtube: true,
            vimeo: true,
          },
        },
      },
      table: {
        class: Table,
        inlineToolbar: true,
      },
      delimiter: Delimiter,
      marker: {
        class: Marker,
      },
      inlineCode: {
        class: InlineCode,
      },
      checklist: {
        class: Checklist,
        inlineToolbar: true,
      },
      image: {
        class: ImageTool,
        tunes: ['imagePosition'],
        config: {
          endpoints: {
            byFile: '/api/admin/upload/image',
            byUrl: '/api/admin/upload/image-by-url',
          },
          field: 'image',
          captionPlaceholder: 'Légende de l\'image',
          buttonContent: 'Sélectionner une image',
        },
      },
      imagePosition: {
        class: ImagePositionTune,
      },
    },
    defaultBlock: 'paragraph',
    onChange: async () => {
      if (editor) {
        const data = await editor.save()
        emit('update:modelValue', data)
        emit('change', data)
      }
    },
    onReady: () => {
      emit('ready')
    },
  })
})

watch(() => props.modelValue, async (newValue) => {
  if (!editor || !newValue) return

  try {
    await editor.isReady
  }
  catch {
    return
  }

  let newData: OutputData | undefined
  if (typeof newValue === 'object' && newValue.blocks) {
    newData = newValue
  }

  if (newData && newData.blocks && newData.blocks.length > 0) {
    const currentData = await editor.save()
    if (JSON.stringify(currentData.blocks) !== JSON.stringify(newData.blocks)) {
      await editor.render(newData)
    }
  }
}, { deep: false })

onBeforeUnmount(() => {
  if (editor) {
    editor.destroy()
    editor = null
  }
})

// Insert block functions
async function insertBlock(type: string, data: Record<string, unknown> = {}) {
  if (!editor) return

  try {
    await editor.isReady
    const currentIndex = editor.blocks.getCurrentBlockIndex()
    const insertIndex = currentIndex >= 0 ? currentIndex + 1 : 0

    await editor.blocks.insert(type, data, undefined, insertIndex, true)
    editor.caret.setToBlock(insertIndex, 'start')
  }
  catch (err) {
    console.error('Error inserting block:', err)
  }
}

function insertHeading() {
  insertBlock('header', { text: '', level: 2 })
}

function insertParagraph() {
  insertBlock('paragraph', { text: '' })
}

function insertList() {
  insertBlock('list', { style: 'unordered', items: [''] })
}

function insertChecklist() {
  insertBlock('checklist', { items: [{ text: '', checked: false }] })
}

function insertQuote() {
  insertBlock('quote', { text: '', caption: '' })
}

function insertTable() {
  insertBlock('table', { withHeadings: true, content: [['', ''], ['', '']] })
}

function insertImage() {
  insertBlock('image', {})
}

function insertDelimiter() {
  insertBlock('delimiter', {})
}

function insertEmbed() {
  insertBlock('embed', {})
}

const save = async (): Promise<OutputData | null> => {
  if (editor) {
    return await editor.save()
  }
  return null
}

defineExpose({ save })
</script>

<template>
  <div class="content-editor-wrapper">
    <div class="content-editor">
      <!-- Toolbar fixe -->
      <div v-if="!readOnly" class="editor-toolbar">
        <span class="toolbar-label">Insérer :</span>
        <div class="toolbar-buttons">
          <button type="button" class="toolbar-btn" title="Titre" @click="insertHeading">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="toolbar-icon"><path fill-rule="evenodd" d="M3 4.5A1.5 1.5 0 014.5 3h11A1.5 1.5 0 0117 4.5v.5a.5.5 0 01-1 0v-.5a.5.5 0 00-.5-.5h-4v13h1.5a.5.5 0 010 1h-4a.5.5 0 010-1H10V4H5.5a.5.5 0 00-.5.5v.5a.5.5 0 01-1 0v-.5z" clip-rule="evenodd" /></svg>
            <span class="btn-label">Titre</span>
          </button>
          <button type="button" class="toolbar-btn" title="Paragraphe" @click="insertParagraph">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="toolbar-icon"><path d="M2 4.75A.75.75 0 012.75 4h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 4.75zm0 5A.75.75 0 012.75 9h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 9.75zm0 5a.75.75 0 01.75-.75h9.5a.75.75 0 010 1.5h-9.5a.75.75 0 01-.75-.75z" /></svg>
            <span class="btn-label">Texte</span>
          </button>
          <button type="button" class="toolbar-btn" title="Liste" @click="insertList">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="toolbar-icon"><path fill-rule="evenodd" d="M2.5 4a.5.5 0 100 1 .5.5 0 000-1zm2.25.5a.75.75 0 01.75-.75h11.5a.75.75 0 010 1.5H5.5a.75.75 0 01-.75-.75zm0 5a.75.75 0 01.75-.75h11.5a.75.75 0 010 1.5H5.5a.75.75 0 01-.75-.75zm0 5a.75.75 0 01.75-.75h11.5a.75.75 0 010 1.5H5.5a.75.75 0 01-.75-.75zM2.5 9a.5.5 0 100 1 .5.5 0 000-1zm0 5a.5.5 0 100 1 .5.5 0 000-1z" clip-rule="evenodd" /></svg>
            <span class="btn-label">Liste</span>
          </button>
          <button type="button" class="toolbar-btn" title="Liste de tâches" @click="insertChecklist">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="toolbar-icon"><path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clip-rule="evenodd" /></svg>
            <span class="btn-label">Tâches</span>
          </button>
          <button type="button" class="toolbar-btn" title="Tableau" @click="insertTable">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="toolbar-icon"><path fill-rule="evenodd" d="M.99 5.24A2.25 2.25 0 013.25 3h13.5A2.25 2.25 0 0119 5.25v9.5A2.25 2.25 0 0116.75 17H3.25A2.25 2.25 0 011 14.75v-9.5zm8.26 4.5v4.5h5.25a.75.75 0 00.75-.75v-3.75H9.25zm0-1.5h5.75V5.25a.75.75 0 00-.75-.75H9.25v3.75zm-1.5 0V4.5H3.25a.75.75 0 00-.75.75v3h5.25zm0 1.5h-5.25v3.75c0 .414.336.75.75.75h4.5v-4.5z" clip-rule="evenodd" /></svg>
            <span class="btn-label">Tableau</span>
          </button>
          <button type="button" class="toolbar-btn" title="Image" @click="insertImage">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="toolbar-icon"><path fill-rule="evenodd" d="M1 5.25A2.25 2.25 0 013.25 3h13.5A2.25 2.25 0 0119 5.25v9.5A2.25 2.25 0 0116.75 17H3.25A2.25 2.25 0 011 14.75v-9.5zm1.5 5.81v3.69c0 .414.336.75.75.75h13.5a.75.75 0 00.75-.75v-2.69l-2.22-2.219a.75.75 0 00-1.06 0l-1.91 1.909-4.97-4.969a.75.75 0 00-1.06 0L2.5 11.06zM12.75 7a1.25 1.25 0 11-2.5 0 1.25 1.25 0 012.5 0z" clip-rule="evenodd" /></svg>
            <span class="btn-label">Image</span>
          </button>
          <button type="button" class="toolbar-btn" title="Citation" @click="insertQuote">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="toolbar-icon"><path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" /><path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" /></svg>
            <span class="btn-label">Citation</span>
          </button>
          <button type="button" class="toolbar-btn" title="Séparateur" @click="insertDelimiter">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="toolbar-icon"><path fill-rule="evenodd" d="M2 10a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 10z" clip-rule="evenodd" /></svg>
            <span class="btn-label">Séparateur</span>
          </button>
          <button type="button" class="toolbar-btn" title="Vidéo YouTube/Vimeo" @click="insertEmbed">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="toolbar-icon"><path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" /></svg>
            <span class="btn-label">Vidéo</span>
          </button>
        </div>
      </div>
      <!-- Éditeur -->
      <div
        ref="editorContainer"
        class="editor-container"
        :style="{ minHeight: `${minHeight}px` }"
      />
    </div>
  </div>
</template>

<style scoped>
.content-editor-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.content-editor {
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background-color: white;
  overflow: visible;
}

.dark .content-editor {
  border-color: #4b5563;
  background-color: #1f2937;
}

/* Toolbar styles */
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: wrap;
}

.dark .editor-toolbar {
  background-color: #1f2937;
  border-bottom-color: #374151;
}

.toolbar-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  white-space: nowrap;
}

.dark .toolbar-label {
  color: #9ca3af;
}

.toolbar-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.toolbar-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #374151;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.toolbar-btn:hover {
  background-color: #f3f4f6;
  border-color: #9ca3af;
  color: #111827;
}

.toolbar-btn:active {
  background-color: #e5e7eb;
}

.dark .toolbar-btn {
  color: #d1d5db;
  background-color: #374151;
  border-color: #4b5563;
}

.dark .toolbar-btn:hover {
  background-color: #4b5563;
  border-color: #6b7280;
  color: white;
}

.dark .toolbar-btn:active {
  background-color: #6b7280;
}

.toolbar-icon {
  width: 0.875rem;
  height: 0.875rem;
}

.toolbar-btn .btn-label {
  display: none;
}

@media (min-width: 768px) {
  .toolbar-btn .btn-label {
    display: inline;
  }
}

.editor-container {
  padding: 1rem;
}

/* Editor.js core styles */
:deep(.codex-editor) {
  color: #111827;
}

.dark :deep(.codex-editor) {
  color: white;
}

:deep(.codex-editor__redactor) {
  padding-bottom: 1rem;
  padding-left: 40px;
}

:deep(.ce-block__content) {
  max-width: none;
  margin: 0;
}

:deep(.ce-toolbar__content) {
  max-width: none;
  margin: 0;
}

:deep(.ce-toolbar__actions) {
  left: -36px;
  position: absolute;
  opacity: 1 !important;
}

:deep(.ce-toolbar) {
  z-index: 10;
}

:deep(.ce-toolbar__plus),
:deep(.ce-toolbar__settings-btn) {
  color: #4b5563;
  background-color: #f3f4f6;
  border-radius: 0.25rem;
  width: 28px;
  height: 28px;
}

:deep(.ce-toolbar__plus) {
  background-color: #dcfce7;
  color: #16a34a;
  font-weight: bold;
}

.dark :deep(.ce-toolbar__plus) {
  background-color: rgba(22, 163, 74, 0.2);
  color: #4ade80;
}

.dark :deep(.ce-toolbar__settings-btn) {
  color: #9ca3af;
  background-color: #374151;
}

:deep(.ce-toolbar__plus:hover) {
  background-color: #bbf7d0;
  color: #15803d;
}

:deep(.ce-toolbar__settings-btn:hover) {
  background-color: #e5e7eb;
}

.dark :deep(.ce-toolbar__plus:hover) {
  background-color: rgba(22, 163, 74, 0.3);
  color: #86efac;
}

.dark :deep(.ce-toolbar__settings-btn:hover) {
  background-color: #4b5563;
}

/* Toolbox popup */
:deep(.ce-toolbox) {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  z-index: 100 !important;
}

.dark :deep(.ce-toolbox) {
  background-color: #374151;
  border-color: #4b5563;
}

:deep(.ce-toolbox__button) {
  color: #374151;
  border-radius: 0.25rem;
}

.dark :deep(.ce-toolbox__button) {
  color: #e5e7eb;
}

:deep(.ce-toolbox__button:hover) {
  background-color: #f3f4f6;
}

.dark :deep(.ce-toolbox__button:hover) {
  background-color: #4b5563;
}

:deep(.ce-inline-toolbar),
:deep(.ce-conversion-toolbar),
:deep(.ce-settings) {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  z-index: 100 !important;
}

.dark :deep(.ce-inline-toolbar),
.dark :deep(.ce-conversion-toolbar),
.dark :deep(.ce-settings) {
  background-color: #374151;
  border-color: #4b5563;
}

/* Delete button red */
:deep(.ce-settings .cdx-settings-button[data-tune="delete"]),
:deep(.ce-settings .ce-settings__button--delete) {
  color: #dc2626;
}

:deep(.ce-settings .cdx-settings-button[data-tune="delete"]:hover),
:deep(.ce-settings .ce-settings__button--delete:hover) {
  background-color: #fef2f2;
  color: #b91c1c;
}

.dark :deep(.ce-settings .cdx-settings-button[data-tune="delete"]),
.dark :deep(.ce-settings .ce-settings__button--delete) {
  color: #f87171;
}

.dark :deep(.ce-settings .cdx-settings-button[data-tune="delete"]:hover),
.dark :deep(.ce-settings .ce-settings__button--delete:hover) {
  background-color: rgba(220, 38, 38, 0.2);
  color: #fca5a5;
}

:deep(.ce-inline-tool),
:deep(.ce-conversion-tool),
:deep(.cdx-settings-button) {
  color: #374151;
}

.dark :deep(.ce-inline-tool),
.dark :deep(.ce-conversion-tool),
.dark :deep(.cdx-settings-button) {
  color: #d1d5db;
}

:deep(.ce-inline-tool:hover),
:deep(.ce-conversion-tool:hover),
:deep(.cdx-settings-button:hover) {
  background-color: #f3f4f6;
}

.dark :deep(.ce-inline-tool:hover),
.dark :deep(.ce-conversion-tool:hover),
.dark :deep(.cdx-settings-button:hover) {
  background-color: #4b5563;
}

:deep(.ce-block--selected .ce-block__content) {
  background-color: #eff6ff;
}

.dark :deep(.ce-block--selected .ce-block__content) {
  background-color: rgba(59, 130, 246, 0.2);
}

/* Block-specific styles */
:deep(.ce-paragraph) {
  line-height: 1.625;
}

:deep(.ce-header) {
  font-weight: 700;
}

:deep(.cdx-list) {
  padding-left: 1.5rem;
}

:deep(.cdx-list__item) {
  padding: 0.25rem 0;
}

:deep(.cdx-quote) {
  border-left: 4px solid #3695d8;
  padding-left: 1rem;
  font-style: italic;
}

:deep(.cdx-quote__caption) {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
}

.dark :deep(.cdx-quote__caption) {
  color: #9ca3af;
}

:deep(.ce-delimiter) {
  text-align: center;
  margin: 1.5rem 0;
}

:deep(.ce-delimiter::before) {
  content: '***';
  color: #9ca3af;
  font-size: 1.5rem;
  letter-spacing: 0.1em;
}

.dark :deep(.ce-delimiter::before) {
  color: #6b7280;
}

/* Table */
:deep(.tc-table) {
  width: 100%;
  border-collapse: collapse;
}

:deep(.tc-table td) {
  border: 1px solid #d1d5db;
  padding: 0.5rem;
}

.dark :deep(.tc-table td) {
  border-color: #4b5563;
}

/* Marker & inline code */
:deep(.cdx-marker) {
  background-color: #fef08a;
  padding: 0 0.25rem;
  border-radius: 0.25rem;
}

.dark :deep(.cdx-marker) {
  background-color: rgba(202, 138, 4, 0.5);
}

:deep(.inline-code) {
  background-color: #f3f4f6;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-family: ui-monospace, monospace;
  color: #db2777;
}

.dark :deep(.inline-code) {
  background-color: #374151;
  color: #f472b6;
}

/* Image tool */
:deep(.image-tool) {
  padding: 0;
}

:deep(.image-tool__image) {
  border-radius: 0.5rem;
  overflow: hidden;
}

:deep(.image-tool__image-picture) {
  max-width: 100%;
  vertical-align: bottom;
}

:deep(.image-tool__caption) {
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
}

.dark :deep(.image-tool__caption) {
  border-color: #4b5563;
  background-color: #374151;
  color: #9ca3af;
}

:deep(.cdx-button) {
  background-color: #f3f4f6;
  border: 1px dashed #d1d5db;
  border-radius: 0.5rem;
  padding: 1rem;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

:deep(.cdx-button:hover) {
  background-color: #e5e7eb;
  border-color: #9ca3af;
}

.dark :deep(.cdx-button) {
  background-color: #374151;
  border-color: #4b5563;
  color: #9ca3af;
}

.dark :deep(.cdx-button:hover) {
  background-color: #4b5563;
  border-color: #6b7280;
}

:deep(.image-tool--withBorder .image-tool__image) {
  border: 1px solid #e5e7eb;
}

.dark :deep(.image-tool--withBorder .image-tool__image) {
  border-color: #4b5563;
}

:deep(.image-tool--withBackground .image-tool__image) {
  background-color: #f3f4f6;
  padding: 1rem;
}

.dark :deep(.image-tool--withBackground .image-tool__image) {
  background-color: #374151;
}

:deep(.image-tool--stretched .image-tool__image-picture) {
  width: 100%;
}

/* Image position tunes (float left/right) */
:deep(.ce-block.image-float-left) {
  float: left;
  width: 45%;
  margin-right: 1.5rem;
  margin-bottom: 1rem;
}

:deep(.ce-block.image-float-right) {
  float: right;
  width: 45%;
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

:deep(.ce-block.image-center) {
  float: none;
  width: 100%;
  clear: both;
}

:deep(.ce-block.image-float-left + .ce-block:not(.image-float-left):not(.image-float-right)),
:deep(.ce-block.image-float-right + .ce-block:not(.image-float-left):not(.image-float-right)) {
  overflow: hidden;
}

/* Custom tune buttons styling */
:deep(.ce-popover-item-container) {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

:deep(.ce-popover-item--active) {
  background-color: #dcfce7 !important;
  color: #16a34a !important;
}

.dark :deep(.ce-popover-item--active) {
  background-color: rgba(22, 163, 74, 0.2) !important;
  color: #4ade80 !important;
}

/* Checklist styles */
:deep(.cdx-checklist) {
  padding-left: 0;
}

:deep(.cdx-checklist__item) {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.375rem 0;
}

:deep(.cdx-checklist__item-checkbox) {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
  border: 2px solid #9ca3af;
  border-radius: 0.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.dark :deep(.cdx-checklist__item-checkbox) {
  border-color: #6b7280;
}

:deep(.cdx-checklist__item--checked .cdx-checklist__item-checkbox) {
  background-color: #16a34a;
  border-color: #16a34a;
}

:deep(.cdx-checklist__item--checked .cdx-checklist__item-checkbox::after) {
  content: '';
  width: 0.375rem;
  height: 0.625rem;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

:deep(.cdx-checklist__item--checked .cdx-checklist__item-text) {
  text-decoration: line-through;
  color: #9ca3af;
}

:deep(.cdx-checklist__item-text) {
  flex: 1;
  outline: none;
  line-height: 1.5;
}

/* Popover (EditorJS 2.31+) */
:deep(.ce-popover) {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.dark :deep(.ce-popover) {
  background-color: #1f2937;
  border-color: #4b5563;
}

:deep(.ce-popover-item:hover) {
  background-color: #f3f4f6;
}

.dark :deep(.ce-popover-item:hover) {
  background-color: #374151;
}

:deep(.ce-popover-item__icon) {
  background: #f3f4f6;
  color: #374151;
}

.dark :deep(.ce-popover-item__icon) {
  background: #374151;
  color: #e5e7eb;
}

:deep(.ce-popover-item__title) {
  color: #111827;
}

.dark :deep(.ce-popover-item__title) {
  color: #e5e7eb;
}

:deep(.cdx-search-field) {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  color: #111827;
}

.dark :deep(.cdx-search-field) {
  background: #374151;
  border-color: #4b5563;
  color: #e5e7eb;
}

/* cdx-input (used by image URL input etc.) */
:deep(.cdx-input) {
  background: white;
  border-color: #d1d5db;
  color: #111827;
}

.dark :deep(.cdx-input) {
  background: #374151;
  border-color: #4b5563;
  color: #e5e7eb;
}
</style>

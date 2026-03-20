<script setup lang="ts">
import type { RichContentBlock } from '~/types/geography'

const model = defineModel<RichContentBlock[]>({ default: () => [] })

function addBlock(type: 'heading' | 'paragraph' | 'image') {
  const block: RichContentBlock = type === 'image'
    ? { type: 'image', url: '', alt: '' }
    : { type, content: '' }
  model.value = [...model.value, block]
}

function removeBlock(index: number) {
  model.value = model.value.filter((_, i) => i !== index)
}

function moveBlock(index: number, direction: -1 | 1) {
  const target = index + direction
  if (target < 0 || target >= model.value.length) return
  const arr = [...model.value]
  const temp = arr[index]
  arr[index] = arr[target]
  arr[target] = temp
  model.value = arr
}

function updateBlock(index: number, field: string, value: string) {
  const arr = [...model.value]
  arr[index] = { ...arr[index], [field]: value }
  model.value = arr
}
</script>

<template>
  <div class="space-y-3">
    <!-- Blocks -->
    <div
      v-for="(block, index) in model"
      :key="index"
      class="flex gap-2 items-start p-3 bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-lg"
    >
      <!-- Controls -->
      <div class="flex flex-col gap-1 pt-1">
        <button
          type="button"
          :disabled="index === 0"
          class="p-1 text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 disabled:opacity-30 disabled:cursor-not-allowed"
          title="Monter"
          @click="moveBlock(index, -1)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
          </svg>
        </button>
        <button
          type="button"
          :disabled="index === model.length - 1"
          class="p-1 text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 disabled:opacity-30 disabled:cursor-not-allowed"
          title="Descendre"
          @click="moveBlock(index, 1)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <span class="text-xs font-medium uppercase text-gray-500 dark:text-gray-400 mb-1 block">
          {{ block.type === 'heading' ? 'Titre' : block.type === 'paragraph' ? 'Paragraphe' : 'Image' }}
        </span>

        <!-- Heading -->
        <input
          v-if="block.type === 'heading'"
          type="text"
          :value="block.content"
          placeholder="Titre de section..."
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-lg font-bold focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          @input="updateBlock(index, 'content', ($event.target as HTMLInputElement).value)"
        />

        <!-- Paragraph -->
        <textarea
          v-else-if="block.type === 'paragraph'"
          :value="block.content"
          placeholder="Texte du paragraphe..."
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          @input="updateBlock(index, 'content', ($event.target as HTMLTextAreaElement).value)"
        />

        <!-- Image -->
        <div v-else-if="block.type === 'image'" class="space-y-2">
          <input
            type="text"
            :value="block.url"
            placeholder="URL de l'image..."
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            @input="updateBlock(index, 'url', ($event.target as HTMLInputElement).value)"
          />
          <input
            type="text"
            :value="block.alt"
            placeholder="Texte alternatif (optionnel)..."
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            @input="updateBlock(index, 'alt', ($event.target as HTMLInputElement).value)"
          />
          <div v-if="block.url" class="mt-1">
            <img
              :src="block.url"
              :alt="block.alt || ''"
              class="max-h-32 rounded border border-gray-200 dark:border-gray-600"
              @error="(e: Event) => (e.target as HTMLImageElement).style.display = 'none'"
            />
          </div>
          <div v-else class="w-full h-24 bg-gray-200 dark:bg-gray-600 rounded flex items-center justify-center text-gray-400 dark:text-gray-500 text-sm">
            Apercu image
          </div>
        </div>
      </div>

      <!-- Delete -->
      <button
        type="button"
        class="p-1.5 text-red-400 hover:text-red-600 dark:text-red-500 dark:hover:text-red-400"
        title="Supprimer ce bloc"
        @click="removeBlock(index)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <!-- Empty state -->
    <p v-if="!model.length" class="text-sm text-gray-500 dark:text-gray-400 italic py-4 text-center">
      Aucun bloc de contenu. Utilisez les boutons ci-dessous pour ajouter du contenu.
    </p>

    <!-- Add buttons -->
    <div class="flex gap-2 pt-2">
      <button
        type="button"
        class="px-3 py-1.5 text-sm font-medium rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
        @click="addBlock('heading')"
      >
        + Titre
      </button>
      <button
        type="button"
        class="px-3 py-1.5 text-sm font-medium rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
        @click="addBlock('paragraph')"
      >
        + Paragraphe
      </button>
      <button
        type="button"
        class="px-3 py-1.5 text-sm font-medium rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
        @click="addBlock('image')"
      >
        + Image
      </button>
    </div>
  </div>
</template>

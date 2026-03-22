<script setup lang="ts">
import type { EditorJSData } from '~/types/geography'

defineProps<{
  descriptionJson: EditorJSData | null
}>()

const brokenImages = ref(new Set<string>())

function handleImageError(blockId: string) {
  brokenImages.value = new Set([...brokenImages.value, blockId])
}
</script>

<template>
  <div class="space-y-4">
    <template v-if="descriptionJson?.blocks?.length">
      <template v-for="(block, index) in descriptionJson.blocks" :key="block.id || index">
        <!-- Header -->
        <h2
          v-if="block.type === 'header' && block.data.level === 2"
          class="text-xl font-bold text-gray-900 dark:text-white"
          v-html="block.data.text"
        />
        <h3
          v-else-if="block.type === 'header' && block.data.level === 3"
          class="text-lg font-bold text-gray-900 dark:text-white"
          v-html="block.data.text"
        />
        <h4
          v-else-if="block.type === 'header'"
          class="text-base font-bold text-gray-900 dark:text-white"
          v-html="block.data.text"
        />

        <!-- Paragraph -->
        <p
          v-else-if="block.type === 'paragraph'"
          class="text-gray-700 dark:text-gray-300 leading-relaxed"
          v-html="block.data.text"
        />

        <!-- Image -->
        <figure v-else-if="block.type === 'image'" class="my-2">
          <img
            v-if="block.data.file?.url && !brokenImages.has(block.id || String(index))"
            :src="block.data.file.url"
            :alt="block.data.caption || ''"
            class="max-w-full rounded-lg"
            :class="{
              'border border-gray-200 dark:border-gray-600': block.data.withBorder,
              'w-full': block.data.stretched,
              'bg-gray-100 dark:bg-gray-700 p-4': block.data.withBackground,
            }"
            @error="handleImageError(block.id || String(index))"
          />
          <div
            v-else
            class="w-full h-48 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center text-gray-500 dark:text-gray-400"
          >
            Image non disponible
          </div>
          <figcaption
            v-if="block.data.caption"
            class="mt-2 text-sm text-center text-gray-500 dark:text-gray-400"
            v-html="block.data.caption"
          />
        </figure>

        <!-- Table -->
        <div v-else-if="block.type === 'table'" class="overflow-x-auto my-2">
          <table class="min-w-full border border-gray-200 dark:border-gray-600 rounded-lg">
            <thead v-if="block.data.withHeadings && block.data.content?.length">
              <tr>
                <th
                  v-for="(cell, ci) in block.data.content[0]"
                  :key="ci"
                  class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-left text-sm font-medium text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-gray-600"
                  v-html="cell"
                />
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, ri) in (block.data.withHeadings ? block.data.content?.slice(1) : block.data.content)"
                :key="ri"
                class="border-b border-gray-200 dark:border-gray-600 last:border-b-0"
              >
                <td
                  v-for="(cell, ci) in row"
                  :key="ci"
                  class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300"
                  v-html="cell"
                />
              </tr>
            </tbody>
          </table>
        </div>

        <!-- List -->
        <ul
          v-else-if="block.type === 'list' && block.data.style === 'unordered'"
          class="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300"
        >
          <li v-for="(item, li) in block.data.items" :key="li" v-html="item" />
        </ul>
        <ol
          v-else-if="block.type === 'list' && block.data.style === 'ordered'"
          class="list-decimal list-inside space-y-1 text-gray-700 dark:text-gray-300"
        >
          <li v-for="(item, li) in block.data.items" :key="li" v-html="item" />
        </ol>
      </template>
    </template>
    <p v-else class="text-gray-500 dark:text-gray-400 italic">
      Aucune description disponible.
    </p>
  </div>
</template>

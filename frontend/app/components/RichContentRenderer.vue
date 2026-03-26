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
  <div class="rich-content space-y-4">
    <template v-if="descriptionJson?.blocks?.length">
      <template v-for="(block, index) in descriptionJson.blocks" :key="block.id || index">
        <!-- Header -->
        <h2
          v-if="block.type === 'header' && block.data.level === 2"
          class="text-xl font-bold text-(--text-primary)"
          v-html="block.data.text"
        />
        <h3
          v-else-if="block.type === 'header' && block.data.level === 3"
          class="text-lg font-bold text-(--text-primary)"
          v-html="block.data.text"
        />
        <h4
          v-else-if="block.type === 'header'"
          class="text-base font-bold text-(--text-primary)"
          v-html="block.data.text"
        />

        <!-- Paragraph -->
        <p
          v-else-if="block.type === 'paragraph'"
          class="text-(--text-secondary) leading-relaxed"
          v-html="block.data.text"
        />

        <!-- Image -->
        <figure
          v-else-if="block.type === 'image'"
          class="my-2"
          :class="{
            'float-left w-[45%] mr-6 mb-4': block.tunes?.imagePosition?.position === 'left',
            'float-right w-[45%] ml-6 mb-4': block.tunes?.imagePosition?.position === 'right',
          }"
        >
          <img
            v-if="block.data.file?.url && !brokenImages.has(block.id || String(index))"
            :src="block.data.file.url"
            :alt="block.data.caption || ''"
            class="max-w-full rounded-lg"
            :class="{
              'border border-(--border-default)': block.data.withBorder,
              'w-full': block.data.stretched,
              'bg-(--interactive-hover) p-4': block.data.withBackground,
            }"
            @error="handleImageError(block.id || String(index))"
          />
          <div
            v-else
            class="w-full h-48 bg-(--interactive-active) rounded-lg flex items-center justify-center text-(--text-muted)"
          >
            Image non disponible
          </div>
          <figcaption
            v-if="block.data.caption"
            class="mt-2 text-sm text-center text-(--text-muted)"
            v-html="block.data.caption"
          />
        </figure>

        <!-- Table -->
        <div v-else-if="block.type === 'table'" class="overflow-x-auto my-2">
          <table class="min-w-full border border-(--border-default) rounded-lg">
            <thead v-if="block.data.withHeadings && block.data.content?.length">
              <tr>
                <th
                  v-for="(cell, ci) in block.data.content[0]"
                  :key="ci"
                  class="px-4 py-2 bg-(--interactive-hover) text-left text-sm font-medium text-(--text-secondary) border-b border-(--border-default)"
                  v-html="cell"
                />
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, ri) in (block.data.withHeadings ? block.data.content?.slice(1) : block.data.content)"
                :key="ri"
                class="border-b border-(--border-default) last:border-b-0"
              >
                <td
                  v-for="(cell, ci) in row"
                  :key="ci"
                  class="px-4 py-2 text-sm text-(--text-secondary)"
                  v-html="cell"
                />
              </tr>
            </tbody>
          </table>
        </div>

        <!-- List (unordered) -->
        <ul
          v-else-if="block.type === 'list' && block.data.style === 'unordered'"
          class="list-disc list-inside space-y-1 text-(--text-secondary)"
        >
          <li v-for="(item, li) in block.data.items" :key="li" v-html="item" />
        </ul>

        <!-- List (ordered) -->
        <ol
          v-else-if="block.type === 'list' && block.data.style === 'ordered'"
          class="list-decimal list-inside space-y-1 text-(--text-secondary)"
        >
          <li v-for="(item, li) in block.data.items" :key="li" v-html="item" />
        </ol>

        <!-- Quote -->
        <blockquote
          v-else-if="block.type === 'quote'"
          class="border-l-4 border-(--color-primary) pl-4 py-2 italic text-(--text-secondary)"
        >
          <p v-html="block.data.text" />
          <cite
            v-if="block.data.caption"
            class="block mt-2 text-sm not-italic text-(--text-muted)"
            v-html="block.data.caption"
          />
        </blockquote>

        <!-- Delimiter -->
        <hr
          v-else-if="block.type === 'delimiter'"
          class="my-6 border-t border-(--border-default)"
        />

        <!-- Checklist -->
        <div v-else-if="block.type === 'checklist'" class="space-y-2">
          <div
            v-for="(item, ci) in block.data.items"
            :key="ci"
            class="flex items-start gap-2"
          >
            <span
              class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border-2"
              :class="item.checked
                ? 'bg-green-600 border-green-600 text-white'
                : 'border-(--border-default)'"
            >
              <svg
                v-if="item.checked"
                xmlns="http://www.w3.org/2000/svg"
                class="h-3 w-3"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clip-rule="evenodd"
                />
              </svg>
            </span>
            <span
              class="text-(--text-secondary)"
              :class="{ 'line-through text-(--text-muted)': item.checked }"
              v-html="item.text"
            />
          </div>
        </div>

        <!-- Embed -->
        <div v-else-if="block.type === 'embed'" class="my-4">
          <div class="relative overflow-hidden rounded-lg" style="padding-bottom: 56.25%">
            <iframe
              :src="block.data.embed"
              class="absolute inset-0 h-full w-full"
              frameborder="0"
              allowfullscreen
            />
          </div>
          <p
            v-if="block.data.caption"
            class="mt-2 text-sm text-center text-(--text-muted)"
            v-html="block.data.caption"
          />
        </div>
      </template>
    </template>
    <p v-else class="text-(--text-muted) italic">
      Aucune description disponible.
    </p>
  </div>
</template>

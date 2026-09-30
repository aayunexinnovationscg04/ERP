<!-- Pagination footer for a table: "1–10 of 42", page size, prev/next + pages. -->
<template>
  <div v-if="pager.total.value > 0" class="pager">
    <div class="pager-size">
      <span>{{ pager.from.value }}–{{ pager.to.value }} of {{ pager.total.value }}</span>
      <select v-model.number="pager.size.value" class="select" aria-label="Rows per page">
        <option v-for="n in [10, 25, 50]" :key="n" :value="n">{{ n }} / page</option>
      </select>
    </div>
    <div v-if="pager.pages.value > 1" class="pager-nav">
      <button type="button" class="pager-btn" :disabled="pager.page.value === 1" aria-label="Previous page" @click="pager.page.value--">
        <ChevronLeft :size="16" />
      </button>
      <button v-for="n in pageNumbers" :key="n" type="button" class="pager-btn pager-num" :class="{ on: n === pager.page.value }"
              :aria-current="n === pager.page.value ? 'page' : undefined" @click="pager.page.value = n">{{ n }}</button>
      <button type="button" class="pager-btn" :disabled="pager.page.value === pager.pages.value" aria-label="Next page" @click="pager.page.value++">
        <ChevronRight :size="16" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps({ pager: { type: Object, required: true } })
// Up to 5 page numbers around the current one.
const pageNumbers = computed(() => {
  const n = props.pager.pages.value; const cur = props.pager.page.value
  const start = Math.max(1, Math.min(cur - 2, n - 4))
  return Array.from({ length: Math.min(5, n) }, (_, i) => start + i)
})
</script>

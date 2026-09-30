import { computed, ref, watch } from 'vue'

// Client-side pagination for a (filtered) list. Goes back to page 1 when the
// list length or page size changes, or when any `resetOn` source (search text,
// filter chips) changes; clamps if rows disappear. Periodic data refreshes
// that keep the same rows leave the current page alone.
export function usePaging(list, initialSize = 10, resetOn = []) {
  const page = ref(1)
  const size = ref(initialSize)
  const total = computed(() => list.value.length)
  const pages = computed(() => Math.max(1, Math.ceil(total.value / size.value)))
  const rows = computed(() => list.value.slice((page.value - 1) * size.value, page.value * size.value))
  const from = computed(() => (total.value ? (page.value - 1) * size.value + 1 : 0))
  const to = computed(() => Math.min(total.value, page.value * size.value))
  watch([() => list.value.length, size, ...resetOn], () => { page.value = 1 })
  watch(pages, (n) => { if (page.value > n) page.value = n })
  return { page, size, total, pages, rows, from, to }
}

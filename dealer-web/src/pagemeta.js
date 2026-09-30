import { reactive } from 'vue'

// Set by a detail page's PageHeader (e.g. the vehicle's name) so the top-bar
// breadcrumb can name the record instead of the page carrying a big title.
export const pageMeta = reactive({ title: '' })

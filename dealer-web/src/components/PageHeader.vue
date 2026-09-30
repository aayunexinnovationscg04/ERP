<!-- Pages carry no big title/description any more: the top-bar breadcrumb
     names the page and this component only
       * teleports the page's actions (default slot) into the top bar,
       * marks sample-data modules (`preview`) with a small tag there,
       * on detail pages (`back`) names the record in the breadcrumb and shows
         a one-line strip with its status badge and key facts. -->
<template>
  <Teleport v-if="$slots.default || preview" defer to="#page-actions">
    <span v-if="preview" class="preview-tag" title="This module has no live data source yet — figures shown are sample data.">
      <FlaskConical :size="13" /><span class="pt-text">Sample data</span>
    </span>
    <slot />
  </Teleport>
  <div v-if="back && ($slots.badge || $slots.description || description)" class="detail-strip">
    <slot name="badge" />
    <span class="ds-meta"><slot name="description">{{ description }}</slot></span>
  </div>
</template>

<script setup>
import { onBeforeUnmount, watch } from 'vue'
import { FlaskConical } from 'lucide-vue-next'
import { pageMeta } from '../pagemeta'

// title/description are still accepted so every page keeps working; only
// detail pages (with `back`) surface them.
const props = defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  back: { type: Object, default: null },
  preview: { type: Boolean, default: false },
})
watch(() => props.back && props.title, (t) => { pageMeta.title = t || '' }, { immediate: true })
onBeforeUnmount(() => { if (props.back) pageMeta.title = '' })
</script>

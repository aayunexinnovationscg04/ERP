<!-- Page actions (e.g. "New user") shown in the top bar next to the page name.
     Pages no longer carry their own big title/description: the top bar names
     the page, and the content starts straight away. -->
<template>
  <Teleport v-if="$slots.default" defer to="#page-actions"><slot /></Teleport>
</template>

<script setup>
// title/description/icon are kept as accepted props so existing pages don't break.
defineProps({ title: String, description: String, icon: [Object, Function] })
</script>

<template>
  <tbody aria-hidden="true">
    <tr v-for="n in rows" :key="n" class="table-empty">
      <td :colspan="cols" style="padding:14px 18px !important">
        <div style="display:flex;gap:14px;align-items:center">
          <div class="skel" style="width:32px;height:32px;border-radius:8px;flex:none"></div>
          <div style="flex:1"><div class="skel" style="height:11px;width:38%;margin-bottom:8px"></div><div class="skel" style="height:9px;width:22%"></div></div>
          <div class="skel" style="height:22px;width:70px;border-radius:999px"></div>
        </div>
      </td>
    </tr>
  </tbody>
</template>

<script setup>
defineProps({ rows: { type: Number, default: 5 }, cols: { type: Number, default: 5 } })
</script>

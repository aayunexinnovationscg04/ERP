<!-- Flat side-view fuel tanker, drawn at origin (~212 x 86). Used inside the
     portal scenes via <TruckGlyph :x :y :scale />. Solid fills only. -->
<template>
  <g :transform="`translate(${x} ${y}) scale(${scale})`">
    <rect x="0" y="62" width="212" height="8" rx="2" fill="#071524" />
    <rect x="2" y="8" width="140" height="52" rx="26" fill="#E2E8F0" />
    <rect x="2" y="30" width="140" height="7" fill="#EA580C" />
    <rect x="18" y="0" width="22" height="9" rx="2" fill="#CBD5E1" />
    <rect x="150" y="18" width="60" height="45" rx="8" fill="#EA580C" />
    <rect x="176" y="25" width="28" height="17" rx="3" fill="#38BDF8" />
    <rect x="156" y="48" width="14" height="4" rx="2" fill="#FDBA74" />
    <g v-for="cx in [30, 62, 118, 188]" :key="cx">
      <circle :cx="cx" cy="72" r="12" fill="#071524" />
      <circle :cx="cx" cy="72" r="5" fill="#94A6BD" />
    </g>
  </g>
</template>

<script setup>
defineProps({ x: { type: Number, default: 0 }, y: { type: Number, default: 0 }, scale: { type: Number, default: 1 } })
</script>

<!--
  Admin sign-in artwork: the platform "control room" — one hub linked to every
  company, devices reporting in, and live health panels. Inline SVG, solid
  palette colours only; motion is off for prefers-reduced-motion.
-->
<template>
  <svg class="art" viewBox="0 0 800 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <pattern id="aa-dots" width="28" height="28" patternUnits="userSpaceOnUse">
        <circle cx="2" cy="2" r="1.6" fill="#102A43" />
      </pattern>
    </defs>
    <rect width="800" height="900" fill="#0B1F33" />
    <rect width="800" height="900" fill="url(#aa-dots)" />

    <!-- rings around the hub -->
    <circle cx="400" cy="450" r="250" fill="none" stroke="#102A43" stroke-width="2" />
    <circle cx="400" cy="450" r="170" fill="none" stroke="#1B3A5C" stroke-width="1.5" stroke-dasharray="4 10" class="spin" />
    <circle cx="400" cy="450" r="110" fill="none" stroke="#1B3A5C" stroke-width="1.5" />

    <!-- links hub -> companies, with data pulses -->
    <g v-for="(n, i) in nodes" :key="'l' + i">
      <line x1="400" y1="450" :x2="n.x" :y2="n.y" stroke="#1B3A5C" stroke-width="2" />
      <line x1="400" y1="450" :x2="n.x" :y2="n.y" :stroke="n.c" stroke-width="3" stroke-linecap="round"
            stroke-dasharray="6 260" class="pulse" :style="{ animationDelay: i * 0.45 + 's' }" />
    </g>

    <!-- company nodes -->
    <g v-for="(n, i) in nodes" :key="'n' + i" :transform="`translate(${n.x - 34} ${n.y - 34})`">
      <rect width="68" height="68" rx="16" fill="#102A43" stroke="#264B73" stroke-width="1.5" />
      <rect x="20" y="20" width="16" height="30" rx="2" fill="#C9D4E1" />
      <rect x="38" y="30" width="12" height="20" rx="2" fill="#8196AE" />
      <rect x="24" y="25" width="3" height="3" fill="#102A43" /><rect x="29" y="25" width="3" height="3" fill="#102A43" />
      <rect x="24" y="32" width="3" height="3" fill="#102A43" /><rect x="29" y="32" width="3" height="3" fill="#102A43" />
      <circle cx="58" cy="10" r="6" :fill="n.c" class="blink" :style="{ animationDelay: i * 0.3 + 's' }" />
    </g>

    <!-- devices reporting (small dots on the outer ring) -->
    <circle v-for="(d, i) in devices" :key="'d' + i" :cx="d.x" :cy="d.y" r="5" :fill="i % 3 ? '#38BDF8' : '#F97316'"
            class="blink" :style="{ animationDelay: i * 0.22 + 's' }" />

    <!-- hub -->
    <circle cx="400" cy="450" r="72" fill="#102A43" stroke="#264B73" stroke-width="2" />
    <circle cx="400" cy="450" r="72" fill="none" stroke="#EA580C" stroke-width="3" stroke-dasharray="60 392" class="spin-slow" />
    <path d="M400 410 L432 422 V450 C432 472 418 486 400 494 C382 486 368 472 368 450 V422 Z" fill="#EA580C" />
    <path d="M386 452 l10 10 l20 -22" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" />

    <!-- health panel (top right) -->
    <g transform="translate(560 90)">
      <rect width="180" height="112" rx="12" fill="#102A43" stroke="#1B3A5C" />
      <circle cx="22" cy="24" r="5" fill="#38BDF8" /><rect x="34" y="20" width="70" height="8" rx="4" fill="#264B73" />
      <g v-for="(h, i) in bars" :key="'h' + i">
        <rect :x="22 + i * 20" :y="92 - h" width="12" :height="h" rx="3" :fill="i === 5 ? '#F97316' : '#264B73'" />
      </g>
    </g>

    <!-- activity panel (bottom left) -->
    <g transform="translate(60 700)">
      <rect width="200" height="104" rx="12" fill="#102A43" stroke="#1B3A5C" />
      <circle cx="22" cy="24" r="5" fill="#F97316" /><rect x="34" y="20" width="84" height="8" rx="4" fill="#264B73" />
      <polyline points="20,84 48,70 76,76 104,52 132,60 160,38 182,44" fill="none" stroke="#38BDF8" stroke-width="3"
                stroke-linecap="round" stroke-linejoin="round" class="draw" />
    </g>
  </svg>
</template>

<script setup>
const R = 250
const nodes = [0, 60, 120, 180, 240, 300].map((deg, i) => {
  const a = (deg - 90) * Math.PI / 180
  return { x: 400 + R * Math.cos(a), y: 450 + R * Math.sin(a), c: i % 2 ? '#38BDF8' : '#F97316' }
})
const devices = Array.from({ length: 12 }, (_, i) => {
  const a = (i * 30 + 15 - 90) * Math.PI / 180
  return { x: 400 + 170 * Math.cos(a), y: 450 + 170 * Math.sin(a) }
})
const bars = [30, 44, 26, 52, 38, 60, 34]
</script>

<style scoped>
.art { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.pulse { animation: pulse 2.7s linear infinite; }
@keyframes pulse { from { stroke-dashoffset: 266; } to { stroke-dashoffset: 0; } }
.blink { animation: blink 2.4s ease-in-out infinite; }
@keyframes blink { 50% { opacity: .35; } }
.spin, .spin-slow { transform-box: view-box; transform-origin: 400px 450px; }
.spin { animation: spin 60s linear infinite; }
.spin-slow { animation: spin 8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.draw { stroke-dasharray: 260; animation: draw 5s ease-in-out infinite alternate; }
@keyframes draw { from { stroke-dashoffset: 260; } to { stroke-dashoffset: 0; } }
@media (prefers-reduced-motion: reduce) {
  .pulse, .blink, .spin, .spin-slow, .draw { animation: none; }
  .draw { stroke-dashoffset: 0; }
}
</style>

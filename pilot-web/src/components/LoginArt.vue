<!--
  Pilot sign-in artwork: the driver's view — the road ahead, the planned route,
  a next-turn card and the speedometer, seen from the cab. Inline SVG, solid
  palette colours only; motion is off for prefers-reduced-motion.
-->
<template>
  <svg class="art" viewBox="0 0 800 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <rect width="800" height="900" fill="#0B1F33" />

    <!-- hills on the horizon -->
    <path d="M0 430 C120 360 220 400 320 380 S520 330 620 372 S760 360 800 350 V440 H0 Z" fill="#102A43" />
    <path d="M0 440 C160 400 260 430 400 420 S640 400 800 420 V440 H0 Z" fill="#1B3A5C" />

    <!-- ground -->
    <rect x="0" y="440" width="800" height="460" fill="#102A43" />

    <!-- road in perspective -->
    <path d="M388 440 H412 L720 900 H80 Z" fill="#1B3A5C" />
    <path d="M388 440 L80 900" stroke="#8196AE" stroke-width="4" />
    <path d="M412 440 L720 900" stroke="#8196AE" stroke-width="4" />
    <!-- centre dashes rushing toward the cab -->
    <g class="dashes">
      <path v-for="(d, i) in dashes" :key="i" :d="d" fill="#C9D4E1" />
    </g>

    <!-- roadside posts -->
    <g v-for="(p, i) in posts" :key="'post' + i">
      <rect :x="p.x" :y="p.y" :width="p.w" :height="p.h" rx="2" fill="#264B73" />
      <rect :x="p.x" :y="p.y" :width="p.w" :height="p.h * .25" rx="2" fill="#F97316" />
    </g>

    <!-- planned route: up the road, then a right turn -->
    <path d="M400 820 L400 560 Q400 520 440 520 L640 520" fill="none" stroke="#38BDF8" stroke-width="10"
          stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="620" class="route" />
    <circle cx="640" cy="520" r="14" fill="#38BDF8" />
    <circle cx="640" cy="520" r="26" fill="none" stroke="#38BDF8" stroke-width="2" class="ping" />

    <!-- next-turn card -->
    <g transform="translate(60 110)">
      <rect width="280" height="96" rx="16" fill="#102A43" stroke="#1B3A5C" />
      <rect x="18" y="18" width="60" height="60" rx="14" fill="#EA580C" />
      <path d="M38 64 V46 Q38 36 48 36 H60" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" />
      <path d="M54 26 L66 36 L54 46" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" />
      <rect x="96" y="28" width="110" height="14" rx="7" fill="#C9D4E1" />
      <rect x="96" y="54" width="150" height="10" rx="5" fill="#264B73" />
    </g>

    <!-- ETA chip -->
    <g transform="translate(560 130)">
      <rect width="180" height="56" rx="28" fill="#102A43" stroke="#1B3A5C" />
      <circle cx="30" cy="28" r="10" fill="#38BDF8" class="blink" />
      <rect x="52" y="22" width="104" height="12" rx="6" fill="#264B73" />
    </g>

    <!-- cab dashboard + steering wheel -->
    <path d="M0 790 Q400 720 800 790 V900 H0 Z" fill="#071524" />
    <g transform="translate(400 900)">
      <circle r="150" fill="none" stroke="#1B3A5C" stroke-width="26" />
      <rect x="-150" y="-16" width="300" height="20" rx="8" fill="#1B3A5C" />
      <circle r="34" fill="#102A43" stroke="#264B73" stroke-width="4" />
    </g>

    <!-- speedometer -->
    <g transform="translate(150 842)">
      <path d="M-62 0 A62 62 0 0 1 62 0" fill="none" stroke="#1B3A5C" stroke-width="10" stroke-linecap="round" />
      <path d="M-62 0 A62 62 0 0 1 62 0" fill="none" stroke="#F97316" stroke-width="10" stroke-linecap="round"
            stroke-dasharray="195" stroke-dashoffset="80" />
      <line x1="0" y1="0" x2="0" y2="-48" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" class="needle" />
      <circle r="8" fill="#FFFFFF" />
    </g>
  </svg>
</template>

<script setup>
// centre-line dashes in perspective: thin near the horizon, wide near the cab
const dashes = []
for (let i = 0; i < 9; i++) {
  const t0 = i / 9; const t1 = t0 + 0.05
  const y0 = 440 + 460 * t0 * t0; const y1 = 440 + 460 * t1 * t1
  const w0 = 1 + 9 * t0; const w1 = 1 + 9 * t1
  dashes.push(`M${400 - w0} ${y0} L${400 + w0} ${y0} L${400 + w1} ${y1} L${400 - w1} ${y1} Z`)
}
const posts = [0.2, 0.45, 0.75].flatMap((t) => {
  const y = 440 + 460 * t * t; const h = 14 + 60 * t; const w = 3 + 8 * t
  const off = 12 + 330 * t * t + 40 * t
  return [{ x: 400 - off - w - 20 * t, y: y - h, w, h }, { x: 400 + off + 20 * t, y: y - h, w, h }]
})
</script>

<style scoped>
.art { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.dashes { transform-origin: 400px 440px; animation: rush 1.1s linear infinite; }
@keyframes rush { from { transform: scale(1); } to { transform: scale(1.12); } }
.route { animation: route 4s ease-in-out infinite alternate; }
@keyframes route { from { stroke-dashoffset: 620; } to { stroke-dashoffset: 0; } }
.ping { transform-box: fill-box; transform-origin: center; animation: ping 2.2s ease-out infinite; }
@keyframes ping { from { transform: scale(.6); opacity: 1; } to { transform: scale(1.5); opacity: 0; } }
.blink { animation: blink 2s ease-in-out infinite; }
@keyframes blink { 50% { opacity: .35; } }
.needle { transform-origin: 0 0; animation: needle 5s ease-in-out infinite alternate; }
@keyframes needle { from { transform: rotate(-40deg); } to { transform: rotate(35deg); } }
@media (prefers-reduced-motion: reduce) {
  .dashes, .route, .ping, .blink, .needle { animation: none; }
  .route { stroke-dashoffset: 0; }
}
</style>

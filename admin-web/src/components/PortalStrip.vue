<!--
  Small portal-identity scene at the foot of the sidebar (Admin Console): the same
  world as this portal's sign-in artwork. Decorative; hidden when the sidebar is
  collapsed or the screen is short, and still for prefers-reduced-motion.
-->
<template>
  <svg class="portal-strip" viewBox="0 0 232 80" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
    <line x1="20" y1="40" x2="212" y2="40" stroke="#1B3A5C" stroke-width="2" />
    <line x1="20" y1="40" x2="212" y2="40" stroke="#38BDF8" stroke-width="3" stroke-linecap="round" stroke-dasharray="6 200" class="ps-flow" />
    <g v-for="(x, i) in [20, 68, 116, 164, 212]" :key="i">
      <rect :x="x - 13" y="27" width="26" height="26" rx="7" :fill="i === 2 ? '#EA580C' : '#102A43'" :stroke="i === 2 ? '#EA580C' : '#264B73'" />
      <circle :cx="x + 11" cy="29" r="3.5" :fill="i % 2 ? '#38BDF8' : '#F97316'" class="ps-blink" :style="{ animationDelay: i * 0.4 + 's' }" />
    </g>
    <path d="M116 33 l6 2.4 v4.6 c0 3.6 -2.6 5.8 -6 7 c-3.4 -1.2 -6 -3.4 -6 -7 v-4.6 Z" fill="#FFFFFF" />
  </svg>
</template>

<style scoped>
.portal-strip { display: block; width: 100%; height: 72px; flex: none; margin-top: auto; padding-top: 12px; opacity: .95; }
.ps-flow { animation: ps-flow 3s linear infinite; }
@keyframes ps-flow { from { stroke-dashoffset: 206; } to { stroke-dashoffset: 0; } }
.ps-blink { animation: ps-blink 2.4s ease-in-out infinite; }
@keyframes ps-blink { 50% { opacity: .3; } }
.ps-lane { animation: ps-lane 1.1s linear infinite; }
@keyframes ps-lane { to { stroke-dashoffset: 26; } }
.ps-drive { animation: ps-drive 9s linear infinite; }
@keyframes ps-drive { from { transform: translateX(-60px); } to { transform: translateX(240px); } }
.ps-rush { transform-origin: 116px 16px; animation: ps-rush .9s linear infinite; }
@keyframes ps-rush { to { transform: scale(1.18); } }
.ps-route { animation: ps-route 3.5s ease-in-out infinite alternate; }
@keyframes ps-route { from { stroke-dashoffset: 110; } to { stroke-dashoffset: 0; } }
@media (prefers-reduced-motion: reduce) {
  .ps-flow, .ps-blink, .ps-lane, .ps-drive, .ps-rush, .ps-route { animation: none; }
  .ps-drive { transform: translateX(95px); } .ps-route { stroke-dashoffset: 0; }
}
</style>

<!--
  Small portal-identity scene at the foot of the sidebar (Pilot App): the same
  world as this portal's sign-in artwork. Decorative; hidden when the sidebar is
  collapsed or the screen is short, and still for prefers-reduced-motion.
-->
<template>
  <svg class="portal-strip" viewBox="0 0 232 80" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
    <path d="M108 16 H124 L200 76 H32 Z" fill="#1B3A5C" />
    <path d="M108 16 L32 76 M124 16 L200 76" stroke="#8196AE" stroke-width="2" />
    <g class="ps-rush"><rect x="115" y="22" width="2" height="7" fill="#C9D4E1" /><rect x="114.5" y="38" width="3" height="10" fill="#C9D4E1" /><rect x="114" y="57" width="4" height="14" fill="#C9D4E1" /></g>
    <path d="M116 76 V42 Q116 34 124 34 H170" fill="none" stroke="#38BDF8" stroke-width="4" stroke-linecap="round" stroke-dasharray="110" class="ps-route" />
    <circle cx="172" cy="34" r="5" fill="#38BDF8" />
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

<!--
  Small portal-identity scene at the foot of the sidebar (Dealer Portal): the same
  world as this portal's sign-in artwork. Decorative; hidden when the sidebar is
  collapsed or the screen is short, and still for prefers-reduced-motion.
-->
<template>
  <svg class="portal-strip" viewBox="0 0 232 80" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
    <rect x="0" y="48" width="232" height="22" fill="#1B3A5C" />
    <line x1="0" y1="59" x2="232" y2="59" stroke="#8196AE" stroke-width="2" stroke-dasharray="14 12" class="ps-lane" />
    <path d="M20 48 L50 30 L80 48 Z" fill="#264B73" /><rect x="26" y="40" width="48" height="8" fill="#264B73" />
    <path d="M20 48 L50 30 L80 48" fill="none" stroke="#EA580C" stroke-width="2.5" />
    <rect x="160" y="24" width="56" height="6" rx="2" fill="#C9D4E1" /><rect x="160" y="29" width="56" height="2.5" fill="#EA580C" />
    <rect x="166" y="31" width="3" height="17" fill="#264B73" /><rect x="207" y="31" width="3" height="17" fill="#264B73" />
    <g class="ps-drive">
      <rect x="0" y="45" width="36" height="12" rx="6" fill="#C9D4E1" /><rect x="3" y="50" width="30" height="2" fill="#EA580C" />
      <path d="M38 44 h8 l5 6 v7 h-13 Z" fill="#EA580C" />
      <circle cx="9" cy="58" r="3.5" fill="#071524" /><circle cx="45" cy="58" r="3.5" fill="#071524" />
    </g>
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

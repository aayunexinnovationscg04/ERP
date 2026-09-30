<!--
  Dealer sign-in artwork: the dealer's own operation — depot, fuel station and
  tankers on the road, with a live fuel gauge and tracked-truck pins. Inline
  SVG, solid palette colours only; motion is off for prefers-reduced-motion.
-->
<template>
  <svg class="art" viewBox="0 0 800 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <!-- fuel tanker, facing right, drawn from its rear-left corner at 0,0 -->
      <g id="dl-tanker">
        <rect x="0" y="6" width="118" height="40" rx="20" fill="#C9D4E1" />
        <rect x="12" y="22" width="94" height="6" rx="3" fill="#EA580C" />
        <rect x="118" y="20" width="10" height="24" fill="#8196AE" />
        <path d="M128 4 h26 l14 18 v24 h-40 Z" fill="#EA580C" />
        <path d="M134 10 h18 l9 12 h-27 Z" fill="#0B1F33" />
        <circle cx="26" cy="50" r="10" fill="#071524" /><circle cx="26" cy="50" r="4" fill="#8196AE" />
        <circle cx="54" cy="50" r="10" fill="#071524" /><circle cx="54" cy="50" r="4" fill="#8196AE" />
        <circle cx="150" cy="50" r="10" fill="#071524" /><circle cx="150" cy="50" r="4" fill="#8196AE" />
      </g>
    </defs>
    <rect width="800" height="900" fill="#0B1F33" />

    <!-- distant skyline -->
    <g fill="#102A43">
      <rect x="0" y="420" width="70" height="170" /><rect x="80" y="380" width="54" height="210" />
      <rect x="146" y="440" width="90" height="150" /><rect x="520" y="400" width="64" height="190" />
      <rect x="596" y="450" width="100" height="140" /><rect x="706" y="390" width="94" height="200" />
    </g>

    <!-- depot (left) -->
    <g transform="translate(40 470)">
      <path d="M0 50 L130 0 L260 50 V150 H0 Z" fill="#1B3A5C" />
      <path d="M0 50 L130 0 L260 50" fill="none" stroke="#EA580C" stroke-width="6" stroke-linejoin="round" />
      <g v-for="i in 3" :key="'door' + i">
        <rect :x="22 + (i - 1) * 78" y="72" width="60" height="78" fill="#102A43" />
        <line v-for="j in 5" :key="j" :x1="22 + (i - 1) * 78" :x2="82 + (i - 1) * 78" :y1="72 + j * 13" :y2="72 + j * 13" stroke="#264B73" stroke-width="2" />
      </g>
    </g>

    <!-- fuel station (right) -->
    <g transform="translate(470 470)">
      <rect x="0" y="0" width="290" height="26" rx="4" fill="#C9D4E1" />
      <rect x="0" y="20" width="290" height="8" fill="#EA580C" />
      <rect x="40" y="28" width="12" height="122" fill="#264B73" /><rect x="238" y="28" width="12" height="122" fill="#264B73" />
      <g v-for="(x, i) in [96, 170]" :key="'pump' + i" :transform="`translate(${x} 78)`">
        <rect width="34" height="72" rx="5" fill="#1B3A5C" />
        <rect x="6" y="8" width="22" height="14" rx="2" fill="#38BDF8" class="blink" :style="{ animationDelay: i * 0.8 + 's' }" />
        <path d="M34 26 h8 v30" fill="none" stroke="#8196AE" stroke-width="3" />
      </g>
    </g>

    <!-- ground + road -->
    <rect x="0" y="620" width="800" height="280" fill="#102A43" />
    <rect x="0" y="660" width="800" height="96" fill="#1B3A5C" />
    <line x1="0" y1="708" x2="800" y2="708" stroke="#8196AE" stroke-width="4" stroke-dasharray="36 28" class="lane" />

    <!-- tankers driving -->
    <g class="drive"><use href="#dl-tanker" x="0" y="652" /></g>
    <g class="drive drive-2"><use href="#dl-tanker" x="0" y="652" /></g>

    <!-- tracked-truck pins -->
    <g v-for="(p, i) in pins" :key="'pin' + i" :transform="`translate(${p.x} ${p.y})`">
      <circle r="22" fill="none" :stroke="p.c" stroke-width="2" class="ping" :style="{ animationDelay: i * 0.7 + 's' }" />
      <path d="M0 -16 C9 -16 14 -9 14 -2 C14 8 0 20 0 20 C0 20 -14 8 -14 -2 C-14 -9 -9 -16 0 -16 Z" :fill="p.c" />
      <circle cy="-3" r="5" fill="#0B1F33" />
    </g>

    <!-- fuel gauge card -->
    <g transform="translate(470 150)">
      <rect width="250" height="150" rx="14" fill="#102A43" stroke="#1B3A5C" />
      <path d="M50 118 A75 75 0 0 1 200 118" fill="none" stroke="#1B3A5C" stroke-width="16" stroke-linecap="round" />
      <path d="M50 118 A75 75 0 0 1 200 118" fill="none" stroke="#EA580C" stroke-width="16" stroke-linecap="round"
            stroke-dasharray="236" stroke-dashoffset="52" class="gauge" />
      <rect x="112" y="92" width="26" height="30" rx="4" fill="#C9D4E1" />
      <rect x="116" y="97" width="18" height="9" rx="2" fill="#102A43" />
    </g>

    <!-- mini fleet list card -->
    <g transform="translate(70 150)">
      <rect width="230" height="150" rx="14" fill="#102A43" stroke="#1B3A5C" />
      <g v-for="(r, i) in rows" :key="'row' + i" :transform="`translate(20 ${26 + i * 38})`">
        <circle cx="8" cy="8" r="7" :fill="r" />
        <rect x="26" y="3" width="92" height="10" rx="5" fill="#264B73" />
        <rect x="140" y="3" width="50" height="10" rx="5" fill="#1B3A5C" />
      </g>
    </g>
  </svg>
</template>

<script setup>
const pins = [{ x: 190, y: 400, c: '#F97316' }, { x: 610, y: 400, c: '#38BDF8' }, { x: 400, y: 360, c: '#F97316' }]
const rows = ['#38BDF8', '#F97316', '#8196AE']
</script>

<style scoped>
.art { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.drive { animation: drive 14s linear infinite; }
.drive-2 { animation-delay: -7s; }
@keyframes drive { from { transform: translateX(-200px); } to { transform: translateX(820px); } }
.lane { animation: lane 1.2s linear infinite; }
@keyframes lane { to { stroke-dashoffset: 64; } }
.blink { animation: blink 2.2s ease-in-out infinite; }
@keyframes blink { 50% { opacity: .35; } }
.ping { transform-box: fill-box; transform-origin: center; animation: ping 2.4s ease-out infinite; }
@keyframes ping { from { transform: scale(.6); opacity: 1; } to { transform: scale(1.6); opacity: 0; } }
.gauge { animation: gauge 6s ease-in-out infinite alternate; }
@keyframes gauge { from { stroke-dashoffset: 120; } to { stroke-dashoffset: 40; } }
@media (prefers-reduced-motion: reduce) {
  .drive, .lane, .blink, .ping, .gauge { animation: none; }
  .drive { transform: translateX(120px); } .drive-2 { transform: translateX(500px); }
}
</style>

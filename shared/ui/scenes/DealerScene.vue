<!-- Dealer portal scene: live fleet map with routes and vehicle pins, a fuel
     level card and a tanker on the road. -->
<template>
  <svg viewBox="0 0 480 320" role="img" aria-label="Live fleet map with vehicles, routes and fuel levels">
    <!-- map -->
    <rect x="20" y="16" width="340" height="220" rx="12" fill="#102A43" stroke="#264B73" />
    <g stroke="#1B3A5C" stroke-width="10" stroke-linecap="round">
      <line x1="20" y1="90" x2="360" y2="70" /><line x1="20" y1="180" x2="360" y2="196" />
      <line x1="110" y1="16" x2="130" y2="236" /><line x1="250" y1="16" x2="236" y2="236" />
    </g>
    <rect x="148" y="100" width="70" height="56" rx="6" fill="#0B1F33" />
    <rect x="264" y="104" width="70" height="60" rx="6" fill="#0B1F33" />
    <rect x="36" y="110" width="58" height="50" rx="6" fill="#0B1F33" />
    <!-- route -->
    <polyline points="56,206 122,186 128,122 244,112 300,84 336,40" fill="none" stroke="#38BDF8" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
    <circle cx="56" cy="206" r="7" fill="#F1F5F9" stroke="#38BDF8" stroke-width="3" />
    <!-- geofence -->
    <circle cx="300" cy="84" r="34" fill="none" stroke="#F1F5F9" stroke-width="2" stroke-dasharray="5 5" />
    <!-- vehicle pins -->
    <g v-for="(p, i) in pins" :key="i" :transform="`translate(${p[0]} ${p[1]})`">
      <path d="M0 0 c-12 0 -20 -9 -20 -19 a20 20 0 0 1 40 0 c0 10 -8 19 -20 19 z" transform="translate(0 -2)" :fill="p[2]" />
      <rect x="-9" y="-28" width="12" height="9" rx="1.5" fill="#FFFFFF" />
      <rect x="3" y="-25" width="6" height="6" rx="1.5" fill="#FFFFFF" />
    </g>
    <!-- fuel card -->
    <rect x="300" y="170" width="160" height="92" rx="10" fill="#F8FAFC" stroke="#CBD5E1" />
    <rect x="316" y="184" width="60" height="7" rx="3.5" fill="#5B6B80" />
    <rect x="316" y="200" width="54" height="16" rx="3" fill="#0B1F33" />
    <rect x="316" y="228" width="128" height="10" rx="5" fill="#E2E8F0" />
    <rect x="316" y="228" width="98" height="10" rx="5" fill="#EA580C" />
    <rect x="316" y="244" width="40" height="5" rx="2.5" fill="#94A6BD" />
    <circle cx="436" cy="194" r="10" fill="#E7F6EF" /><circle cx="436" cy="194" r="4" fill="#047857" />
    <!-- road + tanker -->
    <rect x="0" y="296" width="480" height="6" rx="3" fill="#1B3A5C" />
    <TruckGlyph :x="30" :y="214" :scale="0.95" />
  </svg>
</template>

<script setup>
import TruckGlyph from './TruckGlyph.vue'
const pins = [[128, 122, '#EA580C'], [244, 112, '#EA580C'], [300, 84, '#38BDF8'], [80, 60, '#94A6BD']]
</script>

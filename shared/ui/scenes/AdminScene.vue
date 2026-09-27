<!-- Admin portal scene: a platform console overseeing companies, users and
     access — network of tenant nodes, a usage chart and an access shield. -->
<template>
  <svg viewBox="0 0 480 320" role="img" aria-label="Platform console overseeing companies and access">
    <!-- console window -->
    <rect x="20" y="20" width="360" height="236" rx="12" fill="#102A43" stroke="#264B73" />
    <rect x="20" y="20" width="360" height="32" rx="12" fill="#1B3A5C" />
    <rect x="20" y="40" width="360" height="12" fill="#1B3A5C" />
    <circle cx="40" cy="36" r="4" fill="#EA580C" /><circle cx="54" cy="36" r="4" fill="#94A6BD" /><circle cx="68" cy="36" r="4" fill="#94A6BD" />
    <rect x="96" y="31" width="120" height="10" rx="5" fill="#264B73" />
    <!-- sidebar -->
    <rect x="20" y="52" width="72" height="204" fill="#0B1F33" />
    <rect x="32" y="68" width="48" height="8" rx="4" fill="#EA580C" />
    <rect x="32" y="88" width="40" height="6" rx="3" fill="#264B73" />
    <rect x="32" y="104" width="44" height="6" rx="3" fill="#264B73" />
    <rect x="32" y="120" width="36" height="6" rx="3" fill="#264B73" />
    <rect x="32" y="136" width="42" height="6" rx="3" fill="#264B73" />
    <!-- stat tiles -->
    <g v-for="(t, i) in tiles" :key="i">
      <rect :x="108 + i * 90" y="66" width="80" height="46" rx="8" fill="#0B1F33" stroke="#264B73" />
      <rect :x="118 + i * 90" y="76" width="34" height="6" rx="3" fill="#94A6BD" />
      <rect :x="118 + i * 90" y="90" :width="t" height="12" rx="3" :fill="i === 1 ? '#EA580C' : '#F1F5F9'" />
    </g>
    <!-- tenant network -->
    <rect x="108" y="124" width="170" height="118" rx="8" fill="#0B1F33" stroke="#264B73" />
    <g stroke="#38BDF8" stroke-width="2">
      <line x1="193" y1="183" x2="140" y2="150" /><line x1="193" y1="183" x2="248" y2="148" />
      <line x1="193" y1="183" x2="138" y2="220" /><line x1="193" y1="183" x2="252" y2="218" />
    </g>
    <circle cx="193" cy="183" r="14" fill="#EA580C" />
    <circle cx="140" cy="150" r="9" fill="#F1F5F9" /><circle cx="248" cy="148" r="9" fill="#F1F5F9" />
    <circle cx="138" cy="220" r="9" fill="#F1F5F9" /><circle cx="252" cy="218" r="9" fill="#38BDF8" />
    <!-- bar chart -->
    <rect x="288" y="124" width="80" height="118" rx="8" fill="#0B1F33" stroke="#264B73" />
    <g v-for="(h, i) in bars" :key="'b' + i">
      <rect :x="300 + i * 16" :y="228 - h" width="10" :height="h" rx="2" :fill="i === 2 ? '#EA580C' : '#38BDF8'" />
    </g>
    <!-- user role cards, floating below the console -->
    <g v-for="(c, i) in roles" :key="'r' + i">
      <rect :x="236 + i * 24" :y="246 + i * 36" width="200" height="30" rx="7" fill="#F8FAFC" stroke="#CBD5E1" />
      <circle :cx="254 + i * 24" :cy="261 + i * 36" r="9" :fill="c" />
      <rect :x="270 + i * 24" :y="255 + i * 36" width="84" height="6" rx="3" fill="#0B1F33" />
      <rect :x="270 + i * 24" :y="265 + i * 36" width="54" height="4" rx="2" fill="#94A6BD" />
      <rect :x="392 + i * 24" :y="256 + i * 36" width="32" height="10" rx="5" :fill="c" />
    </g>
    <!-- access shield -->
    <circle cx="410" cy="116" r="42" fill="#EA580C" />
    <path d="M410 90 l22 9 v17 c0 15 -9 25 -22 30 c-13 -5 -22 -15 -22 -30 v-17 z" fill="#FFFFFF" />
    <path d="M401 117 l7 7 l13 -14" fill="none" stroke="#EA580C" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />
  </svg>
</template>

<script setup>
const tiles = [52, 44, 58]
const bars = [30, 52, 78, 44, 64]
const roles = ['#EA580C', '#38BDF8']
</script>

<!-- Pilot portal scene: a driver's trip card (origin -> destination, ETA,
     progress) above a tanker on the highway. -->
<template>
  <svg viewBox="0 0 480 320" role="img" aria-label="Trip route card with ETA above a tanker on the highway">
    <!-- trip card -->
    <rect x="96" y="16" width="288" height="176" rx="14" fill="#F8FAFC" stroke="#CBD5E1" />
    <rect x="116" y="34" width="80" height="8" rx="4" fill="#5B6B80" />
    <rect x="304" y="30" width="60" height="18" rx="9" fill="#E7F6EF" />
    <circle cx="316" cy="39" r="4" fill="#047857" />
    <rect x="324" y="36" width="32" height="6" rx="3" fill="#047857" />
    <!-- route line -->
    <line x1="132" y1="80" x2="132" y2="140" stroke="#CBD5E1" stroke-width="4" stroke-linecap="round" />
    <line x1="132" y1="80" x2="132" y2="116" stroke="#38BDF8" stroke-width="4" stroke-linecap="round" />
    <circle cx="132" cy="78" r="8" fill="#FFFFFF" stroke="#0B1F33" stroke-width="3" />
    <circle cx="132" cy="146" r="9" fill="#EA580C" />
    <circle cx="132" cy="146" r="3.5" fill="#FFFFFF" />
    <rect x="152" y="70" width="110" height="8" rx="4" fill="#0B1F33" />
    <rect x="152" y="84" width="70" height="5" rx="2.5" fill="#94A6BD" />
    <rect x="152" y="138" width="124" height="8" rx="4" fill="#0B1F33" />
    <rect x="152" y="152" width="80" height="5" rx="2.5" fill="#94A6BD" />
    <!-- ETA block -->
    <rect x="290" y="70" width="76" height="86" rx="10" fill="#0B1F33" />
    <rect x="304" y="84" width="30" height="6" rx="3" fill="#94A6BD" />
    <rect x="304" y="100" width="48" height="16" rx="3" fill="#FFFFFF" />
    <rect x="304" y="128" width="48" height="6" rx="3" fill="#264B73" />
    <rect x="304" y="128" width="32" height="6" rx="3" fill="#EA580C" />
    <!-- speed / fuel gauge -->
    <circle cx="60" cy="118" r="40" fill="#102A43" stroke="#264B73" stroke-width="2" />
    <path d="M32 138 A34 34 0 1 1 88 138" fill="none" stroke="#264B73" stroke-width="7" stroke-linecap="round" />
    <path d="M32 138 A34 34 0 0 1 76 88" fill="none" stroke="#38BDF8" stroke-width="7" stroke-linecap="round" />
    <line x1="60" y1="118" x2="76" y2="98" stroke="#EA580C" stroke-width="4" stroke-linecap="round" />
    <circle cx="60" cy="118" r="5" fill="#F1F5F9" />
    <!-- highway -->
    <rect x="0" y="286" width="480" height="18" fill="#1B3A5C" />
    <g fill="#94A6BD"><rect x="20" y="293" width="40" height="4" rx="2" /><rect x="110" y="293" width="40" height="4" rx="2" /><rect x="200" y="293" width="40" height="4" rx="2" /><rect x="290" y="293" width="40" height="4" rx="2" /><rect x="380" y="293" width="40" height="4" rx="2" /></g>
    <TruckGlyph :x="150" :y="206" :scale="1" />
  </svg>
</template>

<script setup>
import TruckGlyph from './TruckGlyph.vue'
</script>

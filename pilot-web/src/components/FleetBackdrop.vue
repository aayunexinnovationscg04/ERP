<!--
  Decorative full-page backdrop for the pilot sign-in: a live fleet-operations
  map (city blocks, river, highways, active routes with moving trucks, depots
  with radar, geofences, telemetry panels). One inline SVG, solid colours only,
  motion switched off for prefers-reduced-motion.
-->
<template>
  <svg class="fb" viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <!-- truck marker, drawn centred on 0,0 -->
      <g id="fb-truck">
        <circle r="13" fill="#EA580C" />
        <rect x="-7" y="-4.5" width="8" height="7" rx="1" fill="#FFFFFF" />
        <rect x="1.5" y="-2.5" width="5" height="5" rx="1" fill="#FFFFFF" />
      </g>
      <path v-for="r in routes" :id="r.id" :key="r.id" :d="r.d" />
    </defs>

    <!-- city blocks -->
    <rect v-for="(b, i) in blocks" :key="'b' + i" :x="b.x" :y="b.y" :width="b.w" :height="b.h" rx="4" :fill="b.f" />

    <!-- river -->
    <path d="M0 560 C200 520 300 620 520 580 S900 480 1100 540 S1400 640 1600 580" fill="none" stroke="#0A2A46" stroke-width="30" />

    <!-- road network: ring highway, arterials (with lane markings), secondary -->
    <path :d="ring" fill="none" stroke="#1B3A5C" stroke-width="14" />
    <path :d="ring" fill="none" stroke="#2B4F78" stroke-width="1.5" stroke-dasharray="14 12" />
    <g fill="none">
      <path v-for="(a, i) in arterials" :key="'a' + i" :d="a" stroke="#17324F" stroke-width="18" />
      <path v-for="(a, i) in arterials" :key="'am' + i" :d="a" stroke="#264B73" stroke-width="1.5" stroke-dasharray="10 14" />
      <path v-for="(s, i) in secondary" :key="'s' + i" :d="s" stroke="#143049" stroke-width="7" />
    </g>

    <!-- geofences -->
    <g fill="none" stroke="#3B5E85" stroke-width="2" stroke-dasharray="6 7">
      <circle v-for="(h, i) in hubs" :key="'g' + i" :cx="h[0]" :cy="h[1]" :r="h[2]" />
    </g>

    <!-- active routes: steady line + moving flow -->
    <g fill="none" stroke-linecap="round">
      <use v-for="r in routes" :key="'rl' + r.id" :href="'#' + r.id" :stroke="r.c" stroke-width="4" />
      <use v-for="r in routes" :key="'rf' + r.id" :href="'#' + r.id" stroke="#F8FAFC" stroke-width="2"
           stroke-dasharray="3 22" class="fb-flow" />
    </g>

    <!-- depots with radar pulse -->
    <g v-for="(h, i) in hubs" :key="'h' + i" :transform="`translate(${h[0]} ${h[1]})`">
      <circle r="24" fill="none" :stroke="h[3]" stroke-width="2" class="fb-radar" :style="{ animationDelay: `${i * 0.7}s` }" />
      <rect x="-11" y="-11" width="22" height="22" rx="5" fill="#0B1F33" :stroke="h[3]" stroke-width="3" />
      <rect x="-4" y="-4" width="8" height="8" rx="1.5" :fill="h[3]" />
    </g>

    <!-- fuel stations -->
    <g v-for="(f, i) in fuel" :key="'f' + i" :transform="`translate(${f[0]} ${f[1]})`">
      <rect x="-10" y="-10" width="20" height="20" rx="4" fill="#0F2A44" stroke="#34D399" stroke-width="2" />
      <rect x="-4" y="-5" width="6" height="10" rx="1" fill="#34D399" />
      <rect x="3" y="-3" width="2" height="6" rx="1" fill="#34D399" />
    </g>

    <!-- trucks driving the routes -->
    <g v-for="(t, i) in trucks" :key="'t' + i">
      <use v-if="motion" href="#fb-truck">
        <animateMotion :dur="t.dur" :begin="t.begin" repeatCount="indefinite" rotate="0">
          <mpath :href="'#' + t.route" />
        </animateMotion>
      </use>
      <use v-else href="#fb-truck" :transform="`translate(${t.at[0]} ${t.at[1]})`" />
    </g>

    <!-- map labels -->
    <g font-family="ui-monospace, Menlo, Consolas, monospace" font-size="13" font-weight="700" fill="#4B6C92" letter-spacing="2">
      <text x="400" y="408">DEPOT A</text>
      <text x="1212" y="508">DEPOT B</text>
      <text x="1318" y="788">YARD C</text>
      <text x="92" y="740">NH 44</text>
      <text x="1400" y="290">NH 53</text>
      <text x="610" y="600">RING RD</text>
    </g>

    <!-- telemetry panels -->
    <g v-for="(p, i) in panels" :key="'p' + i" :transform="`translate(${p.x} ${p.y})`">
      <rect width="230" height="104" rx="10" fill="#0F2740" stroke="#21405F" stroke-width="1.5" />
      <circle cx="20" cy="22" r="5" :fill="p.c" />
      <rect x="34" y="17" width="90" height="10" rx="5" fill="#2B4F78" />
      <rect x="170" y="15" width="44" height="14" rx="7" :fill="p.c" />
      <polyline v-if="p.kind === 'spark'" :points="p.pts" fill="none" :stroke="p.c" stroke-width="3" stroke-linejoin="round" />
      <g v-else>
        <rect v-for="(v, j) in p.bars" :key="j" :x="18 + j * 26" :y="88 - v" width="16" :height="v" rx="3"
              :fill="j === p.hi ? p.c : '#2B4F78'" />
      </g>
    </g>
  </svg>
</template>

<script setup>
const motion = typeof matchMedia === 'undefined' || !matchMedia('(prefers-reduced-motion: reduce)').matches

// City blocks from a seeded generator: dense but deterministic (same every load).
let seed = 7
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647)
const blocks = []
for (let y = 10; y < 1000; y += 62) {
  for (let x = 10; x < 1600; x += 62) {
    if (rnd() < 0.22) continue
    const w = 44 + Math.floor(rnd() * 3) * 8
    const h = 40 + Math.floor(rnd() * 3) * 8
    blocks.push({ x, y, w, h, f: rnd() < 0.5 ? '#0E2338' : '#102A43' })
  }
}

const ring = 'M800 130 C1150 130 1360 330 1360 500 C1360 700 1110 880 800 880 C480 880 240 700 240 500 C240 300 450 130 800 130 Z'
const arterials = [
  'M0 300 C400 260 700 360 1600 280',
  'M0 740 C500 780 900 660 1600 720',
  'M380 0 C360 300 420 600 360 1000',
  'M1190 0 C1230 400 1150 700 1210 1000',
]
const secondary = [
  'M0 980 L700 520 L1600 40', 'M0 60 L520 360', 'M1600 960 L1050 620',
  'M800 0 L800 130', 'M800 880 L800 1000', 'M560 0 L620 300', 'M980 1000 L1040 700',
]
const routes = [
  { id: 'fb-r1', c: '#38BDF8', d: 'M60 760 C300 740 380 600 380 420 S600 290 900 300 S1300 250 1560 190' },
  { id: 'fb-r2', c: '#EA580C', d: 'M1540 110 C1300 160 1210 300 1190 520 S1000 780 760 840 S420 900 180 960' },
  { id: 'fb-r3', c: '#38BDF8', d: 'M100 140 C300 200 420 180 560 240 S760 180 900 140' },
  { id: 'fb-r4', c: '#38BDF8', d: 'M960 960 C1130 830 1290 800 1560 760' },
]
const trucks = [
  // `at` = where the truck sits when motion is reduced
  { route: 'fb-r1', dur: '26s', begin: '0s', at: [300, 700] }, { route: 'fb-r1', dur: '26s', begin: '-13s', at: [1100, 280] },
  { route: 'fb-r2', dur: '30s', begin: '-4s', at: [1220, 300] }, { route: 'fb-r2', dur: '30s', begin: '-19s', at: [560, 870] },
  { route: 'fb-r3', dur: '16s', begin: '-6s', at: [300, 190] }, { route: 'fb-r4', dur: '14s', begin: '-2s', at: [1290, 800] },
]
// [x, y, geofence radius, colour]
const hubs = [[380, 420, 74, '#EA580C'], [1190, 520, 80, '#38BDF8'], [560, 240, 56, '#38BDF8'], [1300, 800, 66, '#EA580C']]
const fuel = [[700, 520], [1040, 700], [250, 610], [1420, 380], [900, 140]]
// kept inside the area that stays visible on wide, short laptop screens
const panels = [
  { x: 70, y: 150, c: '#34D399', kind: 'bars', bars: [22, 34, 28, 42, 36, 48, 30], hi: 5 },
  { x: 1300, y: 150, c: '#38BDF8', kind: 'spark', pts: '18,86 48,76 78,80 108,62 138,68 168,48 212,52' },
  { x: 70, y: 740, c: '#EA580C', kind: 'spark', pts: '18,80 48,84 78,68 108,74 138,52 168,62 212,48' },
  { x: 1330, y: 590, c: '#FBBF24', kind: 'bars', bars: [18, 26, 40, 32, 46, 28, 36], hi: 4 },
]
</script>

<style scoped>
.fb { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; background: #0B1F33; }
.fb-flow { animation: fb-flow 1.6s linear infinite; }
@keyframes fb-flow { to { stroke-dashoffset: -25; } }
.fb-radar { transform-box: fill-box; transform-origin: center; animation: fb-radar 2.8s ease-out infinite; }
@keyframes fb-radar {
  from { transform: scale(.6); opacity: .9; }
  to { transform: scale(2.4); opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
  .fb-flow, .fb-radar { animation: none; }
}
</style>

<template>
  <canvas ref="el" class="ambient-canvas" aria-hidden="true"></canvas>
</template>

<script setup>
// One tasteful, lightweight 3D accent for the login screen: a slow-drifting
// field of points suggesting satellite/GPS tracking over a night highway.
// Perf-conscious by design (this is a mobile-first app, pilots open it on
// phones, often on battery in a cab):
//  - three.js is dynamically imported so it never blocks first paint/login.
//  - Rendering pauses via IntersectionObserver when the canvas scrolls off
//    screen, and via the Page Visibility API when the tab is hidden.
//  - Respects prefers-reduced-motion: renders one static frame, no rAF loop.
//  - Capped pixel ratio, low point count, no postprocessing.
// Purely decorative (aria-hidden) and non-interactive — never blocks input.
import { ref, onMounted, onBeforeUnmount } from 'vue'

const el = ref(null)
let renderer, scene, camera, points, clock, raf, io
let running = false
let reduced = false

function tick() {
  if (!running) return
  const t = clock.getElapsedTime()
  points.rotation.y = t * 0.035
  points.rotation.x = Math.sin(t * 0.08) * 0.05
  renderer.render(scene, camera)
  raf = requestAnimationFrame(tick)
}
function start() {
  if (running || reduced || !renderer) return
  running = true
  tick()
}
function stop() {
  running = false
  if (raf) cancelAnimationFrame(raf)
  raf = null
}
function onVisibility() {
  if (document.hidden) stop()
  else start()
}

async function init() {
  const canvas = el.value
  if (!canvas) return
  reduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches)

  const THREE = await import('three')
  const parent = canvas.parentElement
  const width = parent?.clientWidth || 400
  const height = parent?.clientHeight || 300

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 100)
  camera.position.z = 6
  renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75))
  renderer.setSize(width, height, false)

  const COUNT = 220
  const positions = new Float32Array(COUNT * 3)
  for (let i = 0; i < COUNT; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 12
    positions[i * 3 + 1] = (Math.random() - 0.5) * 9
    positions[i * 3 + 2] = (Math.random() - 0.5) * 8
  }
  const geo = new THREE.BufferGeometry()
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  const mat = new THREE.PointsMaterial({
    color: 0x9ec1ff, size: 0.045, transparent: true, opacity: 0.85, sizeAttenuation: true,
  })
  points = new THREE.Points(geo, mat)
  scene.add(points)
  clock = new THREE.Clock()

  renderer.render(scene, camera) // always show at least one frame

  if (!reduced) {
    io = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) start(); else stop()
    }, { threshold: 0.05 })
    io.observe(canvas)
    document.addEventListener('visibilitychange', onVisibility)
    start()
  }
}

onMounted(init)
onBeforeUnmount(() => {
  stop()
  if (io) io.disconnect()
  document.removeEventListener('visibilitychange', onVisibility)
  if (renderer) renderer.dispose()
})
</script>

<style scoped>
.ambient-canvas {
  position: absolute; inset: 0; width: 100%; height: 100%; display: block; pointer-events: none;
}
</style>

<!--
  Tasteful, lightweight 3D accent for the login screen: an ambient, slowly
  drifting grid of points that reads as "control tower / systems monitoring".
  - three.js is dynamically imported so it never bloats the main app bundle.
  - The render loop fully stops (no rAF calls at all) when the tab is hidden,
    and resumes on visibility return.
  - prefers-reduced-motion renders a single static frame, no animation loop.
  - Purely decorative: aria-hidden, pointer-events: none, never blocks input.
-->
<template>
  <canvas ref="canvasEl" class="particle-field" aria-hidden="true"></canvas>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'

const canvasEl = ref(null)
const reduced = typeof window !== 'undefined' && window.matchMedia
  ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
  : false

let renderer = null, scene = null, camera = null, points = null, clock = null
let raf = null, ro = null

function onVisibility() {
  if (document.hidden) {
    if (raf) { cancelAnimationFrame(raf); raf = null }
  } else if (!raf && renderer) {
    tick()
  }
}

function tick() {
  if (reduced) { renderer.render(scene, camera); return }
  const t = clock.getElapsedTime()
  points.rotation.z = t * 0.015
  points.position.y = Math.sin(t * 0.12) * 0.15
  renderer.render(scene, camera)
  raf = requestAnimationFrame(tick)
}

onMounted(async () => {
  const canvas = canvasEl.value
  if (!canvas) return
  const parent = canvas.parentElement

  const THREE = await import('three')
  if (!canvasEl.value) return // unmounted while the chunk was loading

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100)
  camera.position.set(0, 0, 11)

  renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))

  // sparse point grid — abstract "systems grid", not a gimmick
  const cols = 24, rows = 15
  const spacing = 0.85
  const positions = new Float32Array(cols * rows * 3)
  let i = 0
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      positions[i++] = (x - cols / 2) * spacing + (Math.random() - 0.5) * 0.18
      positions[i++] = (y - rows / 2) * spacing + (Math.random() - 0.5) * 0.18
      positions[i++] = (Math.random() - 0.5) * 1.4
    }
  }
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  const material = new THREE.PointsMaterial({ color: 0xffffff, size: 0.05, transparent: true, opacity: 0.5, sizeAttenuation: true })
  points = new THREE.Points(geometry, material)
  scene.add(points)

  function resize() {
    const w = parent.clientWidth || 1, h = parent.clientHeight || 1
    renderer.setSize(w, h, false)
    camera.aspect = w / h
    camera.updateProjectionMatrix()
  }
  resize()
  ro = new ResizeObserver(resize)
  ro.observe(parent)

  clock = new THREE.Clock()
  document.addEventListener('visibilitychange', onVisibility)
  if (!document.hidden) tick()
  else renderer.render(scene, camera)
})

onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', onVisibility)
  if (raf) cancelAnimationFrame(raf)
  if (ro) ro.disconnect()
  if (renderer) renderer.dispose()
  scene = camera = points = clock = renderer = null
})
</script>

<style scoped>
.particle-field { position: absolute; inset: 0; width: 100%; height: 100%; display: block; pointer-events: none; }
</style>

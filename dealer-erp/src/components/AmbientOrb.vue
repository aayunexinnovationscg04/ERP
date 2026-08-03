<!--
  Tiny, tasteful WebGL ambient accent for the login screen's brand panel —
  a slowly-rotating low-poly "orb" plus a soft particle halo, in brand orange.
  Performance-conscious by design:
    - only ever mounted on the Login screen (see Login.vue), so it's never
      loaded on the data-heavy dashboard/table views
    - render loop pauses via the Page Visibility API when the tab isn't active
    - a single IntersectionObserver pause when the canvas scrolls out of view
    - fully torn down (geometry/material/renderer disposed, rAF cancelled) on
      unmount — no leaked GL contexts if the user bounces on/off the login page
    - respects prefers-reduced-motion: renders one static frame, no rAF loop
  It never captures pointer events (inset canvas, pointer-events:none) and sits
  behind the actual login content (z-index), so it can never block interaction.
-->
<template>
  <canvas ref="canvasEl" class="ambient-orb" aria-hidden="true"></canvas>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as THREE from 'three'

const canvasEl = ref(null)
let renderer, scene, camera, orb, halo, particles, ro, io, raf, clock
let running = false

const reduceMotion = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

function build() {
  const el = canvasEl.value
  const parent = el.parentElement
  const w = parent.clientWidth || 1
  const h = parent.clientHeight || 1

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(42, w / h, 0.1, 100)
  camera.position.z = 6

  renderer = new THREE.WebGLRenderer({ canvas: el, alpha: true, antialias: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
  renderer.setSize(w, h, false)

  // soft glow core — unlit, so no lighting setup needed
  halo = new THREE.Mesh(
    new THREE.SphereGeometry(1.7, 24, 24),
    new THREE.MeshBasicMaterial({ color: 0xea580c, transparent: true, opacity: 0.14 }),
  )
  scene.add(halo)

  // low-poly wireframe orb — the focal "3D accent"
  orb = new THREE.Mesh(
    new THREE.IcosahedronGeometry(1.55, 1),
    new THREE.MeshBasicMaterial({ color: 0xfff1e8, wireframe: true, transparent: true, opacity: 0.55 }),
  )
  scene.add(orb)

  // sparse particle halo drifting around the orb
  const count = 140
  const positions = new Float32Array(count * 3)
  for (let i = 0; i < count; i++) {
    const r = 2.6 + Math.random() * 1.6
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(2 * Math.random() - 1)
    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta)
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
    positions[i * 3 + 2] = r * Math.cos(phi)
  }
  const geo = new THREE.BufferGeometry()
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  particles = new THREE.Points(geo, new THREE.PointsMaterial({
    color: 0xfff1e8, size: 0.045, transparent: true, opacity: 0.6,
    blending: THREE.AdditiveBlending, depthWrite: false,
  }))
  scene.add(particles)

  clock = new THREE.Clock()
}

function renderFrame() {
  const dt = clock.getDelta()
  orb.rotation.y += dt * 0.14
  orb.rotation.x += dt * 0.05
  particles.rotation.y -= dt * 0.05
  halo.scale.setScalar(1 + Math.sin(clock.elapsedTime * 0.6) * 0.04)
  renderer.render(scene, camera)
}

function loop() {
  if (!running) return
  renderFrame()
  raf = requestAnimationFrame(loop)
}

function start() {
  if (running || !renderer) return
  running = true
  if (reduceMotion()) { renderFrame(); running = false; return } // one static frame only
  raf = requestAnimationFrame(loop)
}
function stop() {
  running = false
  if (raf) cancelAnimationFrame(raf)
}

function onVisibility() { document.hidden ? stop() : start() }

function resize() {
  const parent = canvasEl.value?.parentElement
  if (!parent || !renderer) return
  const w = parent.clientWidth || 1
  const h = parent.clientHeight || 1
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h, false)
  if (!running) renderFrame()
}

onMounted(() => {
  build()
  resize()
  start()
  ro = new ResizeObserver(resize)
  ro.observe(canvasEl.value.parentElement)
  io = new IntersectionObserver(([entry]) => { entry.isIntersecting ? start() : stop() }, { threshold: 0.05 })
  io.observe(canvasEl.value)
  document.addEventListener('visibilitychange', onVisibility)
})

onBeforeUnmount(() => {
  stop()
  ro?.disconnect()
  io?.disconnect()
  document.removeEventListener('visibilitychange', onVisibility)
  orb?.geometry.dispose(); orb?.material.dispose()
  halo?.geometry.dispose(); halo?.material.dispose()
  particles?.geometry.dispose(); particles?.material.dispose()
  renderer?.dispose()
})
</script>

<style scoped>
.ambient-orb {
  position: absolute; inset: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 0;
}
</style>

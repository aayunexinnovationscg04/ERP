// Tiny Sonner-inspired toast store. Import { toast } in views; mount <Toaster/> once in App.vue.
import { reactive } from 'vue'
let seq = 0
export const toasts = reactive([])
function push(type, message, ttl) {
  const t = { id: ++seq, type, message }
  toasts.push(t)
  setTimeout(() => dismiss(t.id), ttl)
  return t.id
}
export function dismiss(id) {
  const i = toasts.findIndex((t) => t.id === id)
  if (i > -1) toasts.splice(i, 1)
}
export const toast = {
  success: (m) => push('success', m, 3000),
  error: (m) => push('error', m, 4500),
  info: (m) => push('info', m, 3000),
}

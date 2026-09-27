import { ref, onMounted } from 'vue'
import { getSummary } from './api'

// Real trip state for pages whose content only makes sense on an active trip
// (Route Guidance, Traffic & Delays): is a truck assigned, and is it on a trip?
export function useTripState() {
  const loading = ref(true)
  const assigned = ref(false)
  const onTrip = ref(false)
  const reg = ref('')
  const failed = ref(false)
  async function load() {
    loading.value = true
    failed.value = false
    try {
      const s = await getSummary()
      assigned.value = !!s.assigned
      onTrip.value = !!s.on_trip
      reg.value = s.vehicle?.registration_number || ''
    } catch (e) { failed.value = true }
    finally { loading.value = false }
  }
  onMounted(load)
  return { loading, assigned, onTrip, reg, failed, reload: load }
}

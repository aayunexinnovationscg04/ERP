<template>
  <Modal title="Rename vehicle" :description="vehicle.registration_number" @close="$emit('close')">
    <label class="field">
      <span>Local name</span>
      <input v-model="name" maxlength="10" placeholder="e.g. Loader 2" @keyup.enter="save" />
      <span class="field-hint">{{ name.length }}/10</span>
    </label>
    <p v-if="err" class="form-error" role="alert" style="margin-top:12px">{{ err }}</p>
    <template #footer>
      <button type="button" @click="$emit('close')">Cancel</button>
      <button type="button" class="primary" :disabled="!name.trim() || saving" @click="save">
        {{ saving ? 'Saving…' : 'Save' }}
      </button>
    </template>
  </Modal>
</template>
<script setup>
import { ref } from 'vue'
import Modal from './Modal.vue'
import { setVehicleLocalName } from '../api'
import { toast } from '../toast'

const props = defineProps({ vehicle: { type: Object, required: true } })
const emit = defineEmits(['close', 'saved'])

const name = ref(props.vehicle.local_name || '')
const saving = ref(false)
const err = ref('')

async function save() {
  const trimmed = name.value.trim()
  if (!trimmed) return
  saving.value = true; err.value = ''
  try {
    const data = await setVehicleLocalName(props.vehicle.id, trimmed)
    toast.success('Renamed')
    emit('saved', data.local_name)
    emit('close')
  } catch (e) {
    err.value = e.response?.data?.error || 'Could not rename.'
  } finally { saving.value = false }
}
</script>

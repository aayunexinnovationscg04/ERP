<template>
  <Modal title="Rename vehicle" @close="$emit('close')">
    <p class="muted" style="margin:0 0 14px;font-size:13px">{{ vehicle.registration_number }}</p>
    <label>
      <span class="muted">Local name</span>
      <input v-model="name" maxlength="10" autofocus placeholder="e.g. Loader 2" @keyup.enter="save" />
    </label>
    <p class="muted" style="margin:6px 0 0;font-size:12px">{{ name.length }}/10 characters</p>
    <div class="row" style="margin-top:16px;justify-content:flex-end">
      <button type="button" @click="$emit('close')">Cancel</button>
      <button type="button" class="primary" :disabled="!name.trim() || saving" @click="save">
        {{ saving ? 'Saving…' : 'Save' }}
      </button>
    </div>
    <p v-if="err" class="err" style="margin:10px 0 0">{{ err }}</p>
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

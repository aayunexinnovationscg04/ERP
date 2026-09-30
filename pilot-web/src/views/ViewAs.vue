<!-- Landing page for an admin "view as" link: redeems the one-time ticket from
     the URL fragment, then shows the portal exactly as that user sees it. -->
<template>
  <div class="va">
    <div class="va-card" role="status">
      <template v-if="!failed">
        <span class="va-spin" aria-hidden="true"></span>
        <p>Opening view-only session…</p>
      </template>
      <template v-else>
        <strong>This view link can't be used</strong>
        <p>{{ failed }}</p>
        <button type="button" class="va-btn" @click="closeTab">Close tab</button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { viewAs } from '../auth'

const router = useRouter()
const failed = ref('')

function closeTab() { window.close() }

onMounted(async () => {
  const ticket = new URLSearchParams(location.hash.slice(1)).get('t')
  history.replaceState(null, '', location.pathname)   // don't leave the ticket in the address bar
  if (!ticket) { failed.value = 'The link is incomplete. Open it again from the admin console.'; return }
  try {
    await viewAs(ticket)
    router.replace('/')
  } catch (e) {
    failed.value = e.response?.data?.detail || 'Could not open the view. Try again from the admin console.'
  }
})
</script>

<style scoped>
.va { min-height: 100vh; min-height: 100dvh; display: grid; place-items: center; padding: 16px; background: var(--bg); }
.va-card {
  width: 100%; max-width: 380px; padding: 28px 24px; text-align: center;
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px; box-shadow: var(--shadow-md);
  display: flex; flex-direction: column; align-items: center; gap: 10px; color: var(--text);
}
.va-card p { margin: 0; color: var(--muted); font-size: .92rem; line-height: 1.5; }
.va-card strong { font-size: 1.05rem; }
.va-spin {
  width: 28px; height: 28px; border-radius: 50%;
  border: 3px solid var(--border); border-top-color: var(--brand); animation: va-spin .8s linear infinite;
}
@keyframes va-spin { to { transform: rotate(360deg); } }
.va-btn {
  margin-top: 6px; min-height: 44px; padding: 0 18px; border: 0; border-radius: 10px;
  background: var(--brand); color: #FFFFFF; font: inherit; font-weight: 700; cursor: pointer;
}
</style>

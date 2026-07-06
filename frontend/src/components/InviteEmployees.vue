<template>
  <div :class="['invite-page', darkMode ? 'dark' : 'light']">
    <div class="invite-wrap">
      <div class="invite-topbar">
        <button class="btn-back" @click="$router.back()">
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
          Back
        </button>
        <h2 class="page-title">Invite Employees</h2>
      </div>
      <p class="page-sub">Share a code — anyone who signs up with it joins your company automatically, with the role you choose.</p>

      <!-- GENERATE FORM -->
      <div class="panel-card">
        <div class="panel-header"><span class="panel-title">Generate a New Invite Code</span></div>
        <form @submit.prevent="createNewInvite" class="invite-form">
          <div class="form-field">
            <label>Role</label>
            <select v-model="newInvite.role">
              <option value="team_member">Team Member</option>
              <option value="team_lead">Team Lead</option>
            </select>
          </div>
          <div class="form-field">
            <label>Max Uses (0 = unlimited)</label>
            <input type="number" min="0" v-model.number="newInvite.max_uses" />
          </div>
          <div class="form-field">
            <label>Expires (optional)</label>
            <input type="date" v-model="newInvite.expires_at" />
          </div>
          <button class="btn-primary" type="submit" :disabled="creating">
            {{ creating ? 'Generating…' : 'Generate Code' }}
          </button>
        </form>
      </div>

      <!-- INVITE LIST -->
      <div class="panel-card">
        <div class="panel-header"><span class="panel-title">Your Invite Codes</span></div>
        <div v-if="invites.length" class="invite-list">
          <div v-for="inv in invites" :key="inv.id" class="invite-row" :class="{ 'is-inactive': !inv.is_valid }">
            <div class="invite-code-block">
              <span class="invite-code">{{ inv.code }}</span>
              <button class="btn-copy" @click="copyCode(inv.code)">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 4h8a2 2 0 012 2v8a2 2 0 01-2 2h-8a2 2 0 01-2-2v-8a2 2 0 012-2z"/></svg>
                {{ copiedCode === inv.code ? 'Copied' : 'Copy' }}
              </button>
            </div>
            <span class="role-tag">{{ inv.role.replace('_',' ') }}</span>
            <span class="uses-pill">{{ inv.uses }}{{ inv.max_uses ? ' / ' + inv.max_uses : '' }} used</span>
            <span class="status-pill" :class="inv.is_valid ? 'pill-active' : 'pill-inactive'">
              {{ inv.is_valid ? 'Active' : (inv.is_active ? 'Expired/Full' : 'Revoked') }}
            </span>
            <button class="btn-xs" :class="inv.is_active ? 'btn-danger' : 'btn-accent'" @click="toggle(inv)">
              {{ inv.is_active ? 'Revoke' : 'Reactivate' }}
            </button>
          </div>
        </div>
        <div class="empty-state" v-else>No invite codes yet — generate one above.</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios"
const API_BASE = import.meta.env.VITE_API_URL

export default {
  name: "InviteEmployees",
  data() {
    return {
      darkMode: false,
      invites: [],
      creating: false,
      copiedCode: '',
      newInvite: { role: 'team_member', max_uses: 0, expires_at: '' },
    }
  },
  mounted() { this.fetchInvites() },
  methods: {
    async apiCall(method, url, data = null) {
      const token  = localStorage.getItem("access")
      const config = { method, url: `${API_BASE}${url}`, headers: { Authorization: token ? `Bearer ${token}` : "" } }
      if (data && method.toLowerCase() !== "get") { config.headers["Content-Type"] = "application/json"; config.data = data }
      const res = await axios(config)
      return res.data
    },
    async fetchInvites() {
      try { this.invites = await this.apiCall("get", "invites/") }
      catch (err) { console.error("Invite fetch failed:", err) }
    },
    async createNewInvite() {
      this.creating = true
      try {
        const payload = { role: this.newInvite.role, max_uses: this.newInvite.max_uses || 0 }
        if (this.newInvite.expires_at) payload.expires_at = new Date(this.newInvite.expires_at + 'T23:59:59').toISOString()
        await this.apiCall("post", "invites/", payload)
        this.newInvite = { role: 'team_member', max_uses: 0, expires_at: '' }
        await this.fetchInvites()
      } catch (err) {
        alert("Could not generate invite code.")
      } finally {
        this.creating = false
      }
    },
    async toggle(inv) {
      try {
        await this.apiCall("post", `invites/${inv.id}/toggle/`)
        await this.fetchInvites()
      } catch (err) { alert("Could not update invite.") }
    },
    copyCode(code) {
      navigator.clipboard.writeText(code)
      this.copiedCode = code
      setTimeout(() => { if (this.copiedCode === code) this.copiedCode = '' }, 1500)
    },
  }
}
</script>

<style scoped>
* { font-family:'Poppins',sans-serif; box-sizing:border-box; margin:0; padding:0; }
.light { --bg:#edf0f5; --card:#ffffff; --text:#121c2d; --text-muted:#64748b; --text-faint:#94a3b8; --border:rgba(15,23,42,0.07); --accent:#159aff; --accent-deep:#0c6bb8; --shadow-md:0 4px 16px rgba(16,24,40,0.07); }
.dark  { --bg:#080d15; --card:#111825; --text:#e8edf5; --text-muted:#7b8fa8; --text-faint:#4a5568; --border:rgba(255,255,255,0.065); --accent:#159aff; --accent-deep:#0c6bb8; --shadow-md:0 6px 20px rgba(0,0,0,0.4); }

.invite-page { min-height:100vh; background:var(--bg); padding:32px 20px; }
.invite-wrap { max-width:760px; margin:0 auto; display:flex; flex-direction:column; gap:16px; }
.invite-topbar { display:flex; align-items:center; gap:14px; }
.btn-back { padding:7px 13px; border-radius:9px; background:transparent; border:1px solid var(--border); color:var(--text-muted); cursor:pointer; font-size:12.5px; font-weight:600; display:inline-flex; align-items:center; gap:5px; }
.page-title { font-size:20px; font-weight:700; color:var(--text); }
.page-sub { font-size:12.5px; color:var(--text-muted); margin:-8px 0 4px; }

.panel-card { background:var(--card); border-radius:16px; padding:20px 22px; border:1px solid var(--border); box-shadow:var(--shadow-md); }
.panel-header { margin-bottom:16px; }
.panel-title { font-size:14px; font-weight:700; color:var(--text); }

.invite-form { display:grid; grid-template-columns:1fr 1fr 1fr auto; gap:12px; align-items:end; }
.form-field { display:flex; flex-direction:column; gap:5px; }
.form-field label { font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); }
.form-field input, .form-field select { padding:9px 11px; border-radius:9px; border:1px solid var(--border); background:var(--bg); color:var(--text); font-size:13px; }
.btn-primary { padding:9px 16px; border-radius:9px; background:var(--accent); color:#fff; border:none; cursor:pointer; font-weight:600; font-size:12.5px; }
.btn-primary:disabled { background:#cbd5e1; cursor:not-allowed; }

.invite-list { display:flex; flex-direction:column; gap:8px; }
.invite-row { display:flex; align-items:center; gap:12px; padding:11px 14px; border-radius:11px; background:var(--bg); border:1px solid var(--border); flex-wrap:wrap; }
.invite-row.is-inactive { opacity:.55; }
.invite-code-block { display:flex; align-items:center; gap:8px; }
.invite-code { font-family:'Courier New',monospace; font-weight:700; font-size:14px; letter-spacing:.08em; color:var(--accent); background:rgba(21,154,255,0.08); padding:4px 10px; border-radius:7px; }
.btn-copy { display:inline-flex; align-items:center; gap:4px; padding:4px 9px; border-radius:7px; border:1px solid var(--border); background:var(--card); color:var(--text-muted); font-size:10.5px; font-weight:600; cursor:pointer; }
.role-tag { background:var(--card); border:1px solid var(--border); color:var(--text-muted); border-radius:6px; padding:3px 9px; font-size:11px; font-weight:600; text-transform:capitalize; }
.uses-pill { font-size:11px; color:var(--text-faint); font-weight:600; }
.status-pill { font-size:10.5px; font-weight:700; padding:3px 10px; border-radius:16px; margin-left:auto; }
.pill-active   { background:rgba(34,197,94,0.1); color:#16a34a; }
.pill-inactive { background:rgba(220,38,38,0.1); color:#dc2626; }
.btn-xs { padding:5px 11px; font-size:11px; border-radius:7px; border:none; cursor:pointer; font-weight:600; }
.btn-danger { background:#dc2626; color:#fff; }
.btn-accent { background:var(--accent-deep); color:#fff; }
.empty-state { text-align:center; padding:24px; color:var(--text-muted); font-size:13px; }

@media (max-width:640px) {
  .invite-form { grid-template-columns:1fr; }
  .status-pill { margin-left:0; }
}
</style>

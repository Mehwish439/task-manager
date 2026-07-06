<template>
  <div :class="['dashboard-layout', darkMode ? 'dark' : 'light']">

    <!-- SIDEBAR -->
    <aside class="sidebar">
      <div class="user-info">
        <div class="avatar-circle">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor">
            <path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 2l7 4v6c0 5-3.4 8.4-7 10-3.6-1.6-7-5-7-10V6l7-4z"/>
          </svg>
        </div>
        <span class="username">{{ currentUser }}</span>
        <span class="user-role">Super Admin</span>
      </div>

      <div class="nav-group"><span class="nav-group-label">Platform</span></div>
      <button class="nav-btn active">
        <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7l9-4 9 4-9 4-9-4zm0 6l9 4 9-4M3 13v4l9 4 9-4v-4"/></svg>
        <span>Companies</span>
      </button>

      <div class="sidebar-divider"></div>
      <button class="nav-btn logout-btn" @click="logout">
        <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
        <span>Logout</span>
      </button>

      <div class="theme-toggle">
        <label class="theme-label">
          <input type="checkbox" v-model="darkMode"/>
          <span class="theme-track"><span class="theme-thumb"></span></span>
          {{ darkMode ? 'Dark' : 'Light' }}
        </label>
      </div>
    </aside>

    <!-- MAIN -->
    <main class="content">
      <div class="header-row">
        <div>
          <h2 class="greeting">Platform Overview</h2>
          <span class="greeting-sub">Every company running on this SaaS, in one place</span>
        </div>
        <div class="search-wrap">
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <input type="text" v-model="search" placeholder="Find a company…"/>
        </div>
      </div>

      <!-- STATS -->
      <div class="stats-grid" v-if="stats">
        <div class="stat-card">
          <div class="sc-icon sc-blue"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7l9-4 9 4-9 4-9-4z"/></svg></div>
          <div><p class="sc-label">Companies</p><p class="sc-value">{{ stats.total_companies }}</p></div>
        </div>
        <div class="stat-card">
          <div class="sc-icon sc-green"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg></div>
          <div><p class="sc-label">Active</p><p class="sc-value">{{ stats.active_companies }}</p></div>
        </div>
        <div class="stat-card">
          <div class="sc-icon sc-red"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M12 3l9 16H3z"/></svg></div>
          <div><p class="sc-label">Suspended</p><p class="sc-value">{{ stats.suspended_companies }}</p></div>
        </div>
        <div class="stat-card">
          <div class="sc-icon sc-slate"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87M12 12a4 4 0 100-8 4 4 0 000 8z"/></svg></div>
          <div><p class="sc-label">Total Users</p><p class="sc-value">{{ stats.total_users }}</p></div>
        </div>
        <div class="stat-card">
          <div class="sc-icon sc-navy"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg></div>
          <div><p class="sc-label">Leads</p><p class="sc-value">{{ stats.total_leads }}</p></div>
        </div>
        <div class="stat-card">
          <div class="sc-icon sc-blue"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg></div>
          <div><p class="sc-label">Employees</p><p class="sc-value">{{ stats.total_members }}</p></div>
        </div>
      </div>

      <!-- COMPANIES TABLE -->
      <div class="panel-card">
        <div class="panel-header">
          <span class="panel-title">Companies ({{ filteredCompanies.length }})</span>
          <button class="btn-ghost" @click="loadAll">
            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            Refresh
          </button>
        </div>

        <div class="table-wrap" v-if="filteredCompanies.length">
          <table class="admin-table">
            <thead>
              <tr>
                <th>Company</th><th>Plan</th><th>Users</th><th>Leads</th><th>Employees</th>
                <th>Status</th><th>Created</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in filteredCompanies" :key="c.id" :class="{ 'row-suspended': !c.is_active }">
                <td>
                  <div class="company-cell">
                    <span class="company-dot" :class="c.is_active ? 'dot-ok' : 'dot-off'"></span>
                    <div>
                      <strong>{{ c.name }}</strong>
                      <span class="company-owner">{{ c.owner_username || '—' }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <select class="plan-select" :value="c.plan" @change="changePlan(c, $event.target.value)">
                    <option value="trial">Trial</option>
                    <option value="basic">Basic</option>
                    <option value="pro">Pro</option>
                    <option value="enterprise">Enterprise</option>
                  </select>
                </td>
                <td><span class="count-pill">{{ c.member_count }} / {{ c.max_users }}</span></td>
                <td>{{ c.lead_count }}</td>
                <td>{{ c.employee_count }}</td>
                <td>
                  <span class="status-pill" :class="c.is_active ? 'pill-active' : 'pill-suspended'">
                    {{ c.is_active ? 'Active' : 'Suspended' }}
                  </span>
                </td>
                <td class="muted">{{ formatDate(c.created_at) }}</td>
                <td class="actions-cell">
                  <button class="btn-ghost btn-xs" @click="viewCompany(c)">View</button>
                  <button
                    class="btn-xs"
                    :class="c.is_active ? 'btn-danger' : 'btn-accent'"
                    @click="toggleCompany(c)"
                  >
                    {{ c.is_active ? 'Suspend' : 'Reactivate' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="empty-state" v-else>No companies found.</div>
      </div>

      <!-- COMPANY DETAIL DRAWER -->
      <div class="modal-overlay" v-if="selectedCompany" @click.self="selectedCompany = null">
        <div class="modal-box detail-modal">
          <div class="detail-header">
            <div>
              <h3>{{ selectedCompany.company.name }}</h3>
              <span class="muted">{{ selectedCompany.users.length }} user(s) · plan: {{ selectedCompany.company.plan }}</span>
            </div>
            <button class="btn-ghost btn-xs" @click="selectedCompany = null">Close</button>
          </div>
          <div class="table-wrap">
            <table class="admin-table">
              <thead><tr><th>Username</th><th>Role</th></tr></thead>
              <tbody>
                <tr v-for="u in selectedCompany.users" :key="u.id">
                  <td>{{ u.username }}</td>
                  <td><span class="role-tag">{{ u.role.replace('_',' ') }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script>
import axios from "axios"
const API_BASE = import.meta.env.VITE_API_URL

export default {
  name: "SuperAdminDashboard",
  data() {
    return {
      currentUser: "",
      darkMode: false,
      search: "",
      stats: null,
      companies: [],
      selectedCompany: null,
    }
  },
  computed: {
    filteredCompanies() {
      if (!this.search) return this.companies
      const t = this.search.toLowerCase()
      return this.companies.filter(c => c.name.toLowerCase().includes(t) || (c.owner_username || '').toLowerCase().includes(t))
    }
  },
  mounted() { this.loadAll() },
  methods: {
    async apiCall(method, url, data = null) {
      const token  = localStorage.getItem("access")
      const config = { method, url: `${API_BASE}${url}`, headers: { Authorization: token ? `Bearer ${token}` : "" } }
      if (data && method.toLowerCase() !== "get") { config.headers["Content-Type"] = "application/json"; config.data = data }
      const res = await axios(config)
      return res.data
    },
    async loadAll() {
      try {
        const me = await this.apiCall("get", "me/")
        this.currentUser = me.username
        this.stats = await this.apiCall("get", "admin/stats/")
        this.companies = await this.apiCall("get", "admin/companies/")
      } catch (err) { console.error("Admin load failed:", err) }
    },
    async viewCompany(c) {
      try { this.selectedCompany = await this.apiCall("get", `admin/companies/${c.id}/`) }
      catch (err) { console.error(err) }
    },
    async toggleCompany(c) {
      const verb = c.is_active ? 'suspend' : 'reactivate'
      if (!confirm(`Are you sure you want to ${verb} "${c.name}"?`)) return
      try {
        const updated = await this.apiCall("post", `admin/companies/${c.id}/toggle/`)
        Object.assign(c, updated)
      } catch (err) { alert("Could not update company status.") }
    },
    async changePlan(c, plan) {
      try {
        const updated = await this.apiCall("patch", `admin/companies/${c.id}/plan/`, { plan })
        Object.assign(c, updated)
      } catch (err) { alert("Could not update plan.") }
    },
    formatDate(d) { return d ? new Date(d).toLocaleDateString() : '—' },
    logout() {
      if (!confirm("Log out?")) return
      localStorage.removeItem("access"); localStorage.removeItem("refresh")
      this.$router.push("/login")
    }
  }
}
</script>

<style scoped>
* { font-family:'Poppins',sans-serif; box-sizing:border-box; margin:0; padding:0; }

.light {
  --bg:#edf0f5; --card:#ffffff; --text:#121c2d; --text-muted:#64748b; --text-faint:#94a3b8;
  --border:rgba(15,23,42,0.07); --accent:#159aff; --accent-deep:#0c6bb8;
  --shadow-md:0 4px 16px rgba(16,24,40,0.07); --shadow-lg:0 20px 48px rgba(16,24,40,0.10);
  --sidebar-bg:linear-gradient(175deg,#0a1525 0%,#0f1e34 50%,#0b1828 100%);
}
.dark {
  --bg:#080d15; --card:#111825; --text:#e8edf5; --text-muted:#7b8fa8; --text-faint:#4a5568;
  --border:rgba(255,255,255,0.065); --accent:#159aff; --accent-deep:#0c6bb8;
  --shadow-md:0 6px 20px rgba(0,0,0,0.4); --shadow-lg:0 24px 64px rgba(0,0,0,0.55);
  --sidebar-bg:linear-gradient(175deg,#050a12 0%,#0a1220 50%,#060c18 100%);
}

.dashboard-layout { display:flex; min-height:100vh; background:var(--bg); }

.sidebar { width:220px; margin:12px; border-radius:20px; padding:20px 14px 16px; color:#fff; background:var(--sidebar-bg);
  box-shadow:0 20px 60px rgba(5,12,24,0.5); border:1px solid rgba(255,255,255,0.045); display:flex; flex-direction:column; gap:4px; flex-shrink:0; }
.user-info { display:flex; flex-direction:column; align-items:center; padding-bottom:16px; margin-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.06); }
.avatar-circle { width:42px; height:42px; border-radius:50%; margin-bottom:8px; display:flex; align-items:center; justify-content:center; background:rgba(21,154,255,0.16); color:#9bd2ff; border:2px solid rgba(21,154,255,0.5); }
.username { font-weight:700; font-size:12.5px; color:#f0f4fa; }
.user-role { font-size:10.5px; color:rgba(255,255,255,0.4); margin-top:2px; font-weight:600; letter-spacing:.05em; text-transform:uppercase; }
.nav-group { padding:4px 4px 2px; }
.nav-group-label { font-size:9.5px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:rgba(255,255,255,0.28); }
.nav-btn { border:none; background:transparent; color:rgba(255,255,255,0.55); padding:9px 10px; border-radius:10px; font-size:12.5px; font-weight:500; cursor:pointer; text-align:left; display:flex; align-items:center; gap:9px; width:100%; }
.nav-btn.active { background:rgba(21,154,255,0.14); color:#fff; box-shadow:inset 3px 0 0 #159aff; }
.icon { width:16px; height:16px; flex-shrink:0; }
.sidebar-divider { height:1px; background:rgba(255,255,255,0.06); margin:8px 0; }
.logout-btn { color:rgba(255,107,107,0.85); }
.logout-btn:hover { background:rgba(220,38,38,0.12); }
.theme-toggle { margin-top:auto; }
.theme-label { display:flex; align-items:center; gap:8px; font-size:11px; color:rgba(255,255,255,0.42); cursor:pointer; }
.theme-label input { display:none; }
.theme-track { width:28px; height:16px; border-radius:8px; background:rgba(255,255,255,0.1); position:relative; }
.theme-label input:checked + .theme-track { background:rgba(21,154,255,0.6); }
.theme-thumb { position:absolute; top:2px; left:2px; width:12px; height:12px; border-radius:50%; background:#fff; transition:transform .2s; }
.theme-label input:checked + .theme-track .theme-thumb { transform:translateX(12px); }

.content { flex:1; padding:24px 32px; color:var(--text); display:flex; flex-direction:column; gap:16px; overflow:auto; }
.header-row { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; }
.greeting { font-size:22px; font-weight:700; letter-spacing:-.02em; }
.greeting-sub { font-size:12px; color:var(--text-muted); font-weight:500; }
.search-wrap { position:relative; max-width:280px; flex:1; }
.search-icon { position:absolute; left:12px; top:50%; transform:translateY(-50%); width:15px; height:15px; color:var(--text-faint); }
.search-wrap input { width:100%; padding:9px 13px 9px 36px; border-radius:10px; border:1px solid var(--border); background:var(--card); color:var(--text); font-size:13px; }

.stats-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:10px; }
.stat-card { background:var(--card); border-radius:13px; padding:14px 16px; border:1px solid var(--border); display:flex; align-items:center; gap:12px; box-shadow:var(--shadow-md); }
.sc-icon { width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.sc-blue  { background:rgba(21,154,255,0.1); color:#159aff; }
.sc-green { background:rgba(34,197,94,0.1); color:#16a34a; }
.sc-red   { background:rgba(220,38,38,0.1); color:#dc2626; }
.sc-slate { background:rgba(100,116,139,0.1); color:#64748b; }
.sc-navy  { background:rgba(12,107,184,0.1); color:#0c6bb8; }
.sc-label { font-size:9.5px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); font-weight:700; }
.sc-value { font-size:19px; font-weight:700; color:var(--text); }

.panel-card { background:var(--card); border-radius:16px; padding:20px 22px; border:1px solid var(--border); box-shadow:var(--shadow-md); }
.panel-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
.panel-title { font-size:14px; font-weight:700; }
.btn-ghost { padding:7px 13px; border-radius:9px; background:var(--card); border:1px solid var(--border); color:var(--text-muted); cursor:pointer; font-size:12px; font-weight:600; display:inline-flex; align-items:center; gap:5px; }
.btn-ghost:hover { border-color:var(--accent); color:var(--accent); }
.btn-ghost.btn-xs { padding:4px 9px; font-size:11px; }

.table-wrap { overflow-x:auto; }
.admin-table { width:100%; border-collapse:collapse; }
.admin-table th { font-size:10.5px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); font-weight:700; padding:10px 12px; border-bottom:1px solid var(--border); text-align:left; white-space:nowrap; }
.admin-table td { padding:11px 12px; font-size:12.5px; border-bottom:1px solid var(--border); vertical-align:middle; }
.admin-table tbody tr:hover { background:rgba(21,154,255,0.03); }
.row-suspended { opacity:.6; }
.company-cell { display:flex; align-items:center; gap:9px; }
.company-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.dot-ok  { background:#22c55e; }
.dot-off { background:#dc2626; }
.company-owner { display:block; font-size:11px; color:var(--text-faint); margin-top:1px; }
.count-pill { background:var(--bg); border:1px solid var(--border); border-radius:8px; padding:2px 9px; font-size:11.5px; font-weight:600; }
.plan-select { padding:5px 8px; border-radius:7px; border:1px solid var(--border); background:var(--bg); color:var(--text); font-size:11.5px; font-weight:600; }
.status-pill { font-size:10.5px; font-weight:700; padding:3px 10px; border-radius:16px; }
.pill-active     { background:rgba(34,197,94,0.1); color:#16a34a; }
.pill-suspended  { background:rgba(220,38,38,0.1); color:#dc2626; }
.muted { color:var(--text-faint); font-size:11.5px; }
.role-tag { background:var(--bg); border:1px solid var(--border); color:var(--text-muted); border-radius:6px; padding:2px 8px; font-size:11px; font-weight:600; text-transform:capitalize; }
.actions-cell { display:flex; gap:6px; }
.btn-xs { padding:5px 10px; font-size:11px; border-radius:7px; border:none; cursor:pointer; font-weight:600; }
.btn-danger { background:#dc2626; color:#fff; }
.btn-accent { background:var(--accent-deep); color:#fff; }
.empty-state { text-align:center; padding:36px; color:var(--text-muted); font-size:13px; }

.modal-overlay { position:fixed; inset:0; background:rgba(4,8,16,0.55); display:flex; justify-content:center; align-items:center; z-index:100; backdrop-filter:blur(5px); }
.modal-box { background:var(--card); border-radius:16px; box-shadow:var(--shadow-lg); border:1px solid var(--border); }
.detail-modal { width:520px; max-width:92vw; max-height:80vh; overflow-y:auto; padding:22px 24px; }
.detail-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
.detail-header h3 { font-size:16px; font-weight:700; }

@media (max-width:768px) {
  .sidebar { display:none; }
  .content { padding:60px 16px 24px; }
}
</style>

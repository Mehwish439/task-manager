<template>
  <div class="container">
    <div class="card">
      <!-- Left Panel -->
      <div class="left-panel">
        <h2>Welcome Back!</h2>
        <p>Already have an account? Sign in to manage your tasks.</p>
        <button class="btn-outline" @click="goToLogin">SIGN IN</button>
      </div>

      <!-- Right Panel (Signup Form) -->
      <div class="right-panel">
        <h2>Create Account</h2>

        <!-- Mode switcher -->
        <div class="mode-tabs">
          <button
            class="mode-tab"
            :class="{ active: mode === 'company' }"
            @click="mode = 'company'; message = ''"
          >
            Start a New Company
          </button>
          <button
            class="mode-tab"
            :class="{ active: mode === 'invite' }"
            @click="mode = 'invite'; message = ''"
          >
            Join with Invite Code
          </button>
        </div>

        <!-- ===== CREATE COMPANY (first user = Team Lead / owner) ===== -->
        <form v-if="mode === 'company'" @submit.prevent="registerCompany">
          <input v-model="company.company_name" type="text" placeholder="Company Name" />
          <input v-model="company.username" type="text" placeholder="Your Username" />
          <input v-model="company.email" type="email" placeholder="Your Email" />
          <input v-model="company.password" type="password" placeholder="Password" />

          <p class="hint-text">
            You'll become the <strong>Team Lead</strong> for this company. You can invite
            employees afterward from your dashboard.
          </p>

          <button class="btn-primary" :disabled="!isCompanyFormValid || loading">
            {{ loading ? 'Creating…' : 'CREATE COMPANY' }}
          </button>
        </form>

        <!-- ===== JOIN VIA INVITE CODE ===== -->
        <form v-else @submit.prevent="registerViaInvite">
          <input v-model="invite.invite_code" type="text" placeholder="Invite Code" class="invite-code-input" />
          <input v-model="invite.username" type="text" placeholder="Username" />
          <input v-model="invite.email" type="email" placeholder="Email" />
          <input v-model="invite.password" type="password" placeholder="Password" />

          <p class="hint-text">
            Ask your Team Lead for an invite code — it links your account to
            their company automatically.
          </p>

          <button class="btn-primary" :disabled="!isInviteFormValid || loading">
            {{ loading ? 'Joining…' : 'JOIN COMPANY' }}
          </button>
        </form>

        <p class="message" :class="{ 'is-error': isError }">{{ message }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { signupCompany, joinViaInvite } from "@/api"

export default {
  data() {
    return {
      mode: 'company', // 'company' | 'invite'
      loading: false,
      message: '',
      isError: false,
      company: { company_name: '', username: '', email: '', password: '' },
      invite:  { invite_code: '', username: '', email: '', password: '' },
    }
  },
  computed: {
    isCompanyFormValid() {
      return this.company.company_name && this.company.username && this.company.email && this.company.password
    },
    isInviteFormValid() {
      return this.invite.invite_code && this.invite.username && this.invite.email && this.invite.password
    },
  },
  methods: {
    async registerCompany() {
      this.loading = true
      this.message = ''
      this.isError = false
      try {
        const res = await signupCompany({ ...this.company })
        this.message = res.data.message + ' Redirecting to login…'
        setTimeout(() => this.$router.push('/login'), 1400)
      } catch (error) {
        this.isError = true
        this.message = this._extractError(error, 'Could not create company. Please try again.')
      } finally {
        this.loading = false
      }
    },
    async registerViaInvite() {
      this.loading = true
      this.message = ''
      this.isError = false
      try {
        const payload = { ...this.invite, invite_code: this.invite.invite_code.trim().toUpperCase() }
        const res = await joinViaInvite(payload)
        this.message = res.data.message + ' Redirecting to login…'
        setTimeout(() => this.$router.push('/login'), 1400)
      } catch (error) {
        this.isError = true
        this.message = this._extractError(error, 'Could not join with that invite code.')
      } finally {
        this.loading = false
      }
    },
    _extractError(error, fallback) {
      const data = error?.response?.data
      if (!data) return fallback
      const firstKey = Object.keys(data)[0]
      const val = data[firstKey]
      return Array.isArray(val) ? val[0] : (val || fallback)
    },
    goToLogin() {
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
* {
  font-family: 'Poppins', sans-serif;
}
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #edf0f5, #f6f8fb);
}
.card {
  display: flex;
  width: 880px;
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 48px rgba(16,24,40,0.10), 0 6px 16px rgba(16,24,40,0.05);
  border: 1px solid rgba(15,23,42,0.06);
}
.left-panel {
  flex: 1;
  background: linear-gradient(175deg, #0a1525 0%, #0f1e34 50%, #0b1828 100%);
  color: white;
  padding: 50px 30px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}
.left-panel h2 { font-weight: 700; margin-bottom: 10px; }
.left-panel p { color: rgba(255,255,255,0.55); font-size: 13.5px; line-height: 1.6; margin-bottom: 26px; }
.btn-outline {
  border: 1.5px solid rgba(21,154,255,0.55);
  background: rgba(21,154,255,0.1);
  color: white;
  padding: 12px 28px;
  font-weight: 600;
  border-radius: 25px;
  cursor: pointer;
  transition: 0.2s;
  align-self: center;
}
.btn-outline:hover { background: #159aff; border-color: #159aff; }

.right-panel {
  flex: 1.25;
  padding: 44px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.right-panel h2 { color: #121c2d; font-weight: 700; margin-bottom: 16px; }

.mode-tabs {
  display: flex;
  gap: 3px;
  background: #f0f3f8;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 20px;
  border: 1px solid rgba(15,23,42,0.06);
}
.mode-tab {
  flex: 1;
  padding: 9px 10px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  border-radius: 9px;
  transition: all .18s;
}
.mode-tab.active { color: #fff; background: #159aff; box-shadow: 0 3px 10px rgba(21,154,255,0.3); }

form { display: flex; flex-direction: column; gap: 14px; }
form input {
  padding: 12px 14px;
  border: 1px solid rgba(15,23,42,0.11);
  border-radius: 8px;
  font-size: 1rem;
  color: #121c2d;
  background: #f6f8fb;
  transition: border-color .15s, box-shadow .15s;
}
form input:focus {
  outline: none;
  border-color: rgba(21,154,255,0.45);
  box-shadow: 0 0 0 3px rgba(21,154,255,0.1);
  background: #fff;
}
.invite-code-input { letter-spacing: 0.12em; font-weight: 700; text-transform: uppercase; }

.hint-text { font-size: 12px; color: #94a3b8; line-height: 1.5; margin: -4px 0 2px; }
.hint-text strong { color: #159aff; }

.btn-primary {
  background: #159aff;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-primary:hover { background: #0c6bb8; }
.btn-primary:disabled { background: #cbd5e1; cursor: not-allowed; }

.message {
  margin-top: 14px;
  text-align: center;
  font-size: 0.9rem;
  color: #16a34a;
  font-weight: 500;
}
.message.is-error { color: #dc2626; }
</style>
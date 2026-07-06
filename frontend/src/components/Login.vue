<template>
  <div class="container">
    <div class="card">
      <!-- Left Panel -->
      <div class="left-panel">
        <h2>New Here?</h2>
        <p>Don't have an account? Create one and join the team.</p>
        <button class="btn-outline" @click="goToRegister">SIGN UP</button>
      </div>

      <!-- Right Panel (Login Form) -->
      <div class="right-panel">
        <h2>Login</h2>
        <form @submit.prevent="login">
          <input v-model="username" type="text" placeholder="Username" />
          <input v-model="password" type="password" placeholder="Password" />
          <button class="btn-primary" :disabled="!isFormValid || loading">
            {{ loading ? 'Signing in…' : 'LOGIN' }}
          </button>
          <p class="error-message" v-if="error">{{ error }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api, { loginUser } from "@/api"

export default {
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false,
    }
  },
  computed: {
    isFormValid() {
      return this.username && this.password
    }
  },
  methods: {
    async login() {
      this.error = ''
      this.loading = true
      try {
        const res = await loginUser({
          username: this.username,
          password: this.password
        })

        localStorage.setItem('access', res.data.access)
        localStorage.setItem('refresh', res.data.refresh)

        const me = await api.get('me/')
        const role = me.data.role

        if (role === 'super_admin') {
          this.$router.push({ name: 'SuperAdminDashboard' })
        } else if (role === 'team_member') {
          this.$router.push({ name: 'AssignedTasks' })
        } else {
          this.$router.push({ name: 'TaskList' })
        }

      } catch (err) {
        console.error(err)
        // Company-suspension / not-linked errors come back as
        // { non_field_errors: ["..."] } from MyTokenObtainPairSerializer.validate()
        const data = err?.response?.data
        const backendMsg = data?.non_field_errors?.[0] || data?.detail
        this.error = backendMsg || 'Invalid username or password.'
      } finally {
        this.loading = false
      }
    },
    goToRegister() {
      this.$router.push({ name: 'Signup' })
    }
  }
}
</script>

<style scoped>
* {
  font-family: 'Poppins', sans-serif;
  box-sizing: border-box;
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
  width: 850px;
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 48px rgba(16,24,40,0.10), 0 6px 16px rgba(16,24,40,0.05);
  border: 1px solid rgba(15,23,42,0.06);
}

.left-panel {
  flex: 1;
  background: linear-gradient(175deg, #0a1525 0%, #0f1e34 50%, #0b1828 100%);
  color: #fff;
  padding: 50px 30px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
  position: relative;
}

.left-panel h2 {
  font-weight: 700;
  letter-spacing: -0.01em;
  margin-bottom: 10px;
}

.left-panel p {
  color: rgba(255,255,255,0.55);
  font-size: 13.5px;
  line-height: 1.6;
  margin-bottom: 26px;
}

.btn-outline {
  border: 1.5px solid rgba(21,154,255,0.55);
  background: rgba(21,154,255,0.1);
  color: #fff;
  padding: 12px 28px;
  font-weight: 600;
  border-radius: 25px;
  cursor: pointer;
  transition: 0.2s;
  align-self: center;
}

.btn-outline:hover {
  background: #159aff;
  border-color: #159aff;
  color: #fff;
}

.right-panel {
  flex: 1.2;
  padding: 50px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.right-panel h2 {
  color: #121c2d;
  font-weight: 700;
  margin-bottom: 22px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

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

.btn-primary {
  background: #159aff;
  color: #fff;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #0c6bb8;
}

.btn-primary:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.error-message {
  margin-top: 10px;
  text-align: center;
  color: #dc2626;
  font-size: 0.95rem;
  font-weight: 500;
}
</style>
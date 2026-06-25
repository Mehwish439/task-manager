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
          <button class="btn-primary" :disabled="!isFormValid">LOGIN</button>
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
      error: ''
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
      try {
        const res = await loginUser({
          username: this.username,
          password: this.password
        })

        localStorage.setItem('access', res.data.access)
        localStorage.setItem('refresh', res.data.refresh)

        const me = await api.get('me/')
        const role = me.data.role

        if (role === 'team_member') {
          this.$router.push({ name: 'AssignedTasks' })
        } else {
          this.$router.push({ name: 'TaskList' }) // 
        }

      } catch (err) {
        console.error(err)
        this.error = 'Invalid username or password.'
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
}
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(to right, #dfe9f3, #ffffff);
}
.card {
  display: flex;
  width: 850px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}
.left-panel {
  flex: 1;
  background: linear-gradient(to right, #159aff,#159aff);
  color: white;
  padding: 50px 30px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}
.btn-outline {
  border: 2px solid white;
  background: transparent;
  color: white;
  padding: 12px 28px;
  font-weight: 600;
  border-radius: 25px;
  cursor: pointer;
  transition: 0.3s;
}
.btn-outline:hover {
  background: white;
  color: #159aff;
}
.right-panel {
  flex: 1.2;
  padding: 50px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
form input {
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}
.btn-primary {
  background: #159aff;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}
.btn-primary:hover {
  background:#159aff;
}
.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.error-message {
  margin-top: 10px;
  text-align: center;
  color: #159aff;
  font-size: 0.95rem;
}
</style>

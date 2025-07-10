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

       

        <form @submit.prevent="register">
          <input v-model="username" type="text" placeholder="Username" />
          <input v-model="email" type="email" placeholder="Email" />
          <input v-model="password" type="password" placeholder="Password" />

          <select v-model="role">
            <option disabled value="">Select Role</option>
            <option value="team_lead">Team Lead</option>
            <option value="team_member">Team Member</option>
          </select>

          <button class="btn-primary" :disabled="!isFormValid">SIGN UP</button>
        </form>

        <p class="message">{{ message }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      username: '',
      email: '',
      password: '',
      role: '',
      message: ''
    }
  },
  computed: {
    isFormValid() {
      return this.username && this.email && this.password && this.role
    }
  },
  methods: {
    async register() {
      try {
        const payload = {
          username: this.username,
          email: this.email,
          password: this.password,
          role: this.role
        }

        await axios.post('http://localhost:8000/api/register/', payload)

        this.message = 'Account created successfully.'
        this.username = ''
        this.email = ''
        this.password = ''
        this.role = ''
      } catch (error) {
        this.message = 'Registration failed. Please try again.'
        console.error(error)
      }
    },
    goToLogin() {
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
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
  background: linear-gradient(to right, #5f2c82, #49a09d);
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
  color: #5f2c82;
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
form input,
form select {
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}
.btn-primary {
  background: #5f2c82;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}
.btn-primary:hover {
  background: #45205f;
}
.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.divider-text {
  text-align: center;
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 20px;
}
.message {
  margin-top: 15px;
  text-align: center;
  font-size: 0.9rem;
  color: #198754;
}
</style>

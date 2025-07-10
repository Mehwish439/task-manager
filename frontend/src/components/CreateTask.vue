<template>
  <div class="container">
    <div class="form-box">
      <div class="header">
        <h2>Create Task</h2>
        <button class="btn-outline small" @click="goToTaskList">Task List</button>
      </div>

      <form @submit.prevent="createTask">
        <input v-model="title" type="text" placeholder="Task Title" />
        <input v-model="description" type="text" placeholder="Task Description" />
        <input v-model="startDate" type="date" />
        <input v-model="endDate" type="date" />
        <button class="btn-primary" type="submit" :disabled="!isFormValid">Create Task</button>
      </form>

      <p class="error-message" v-if="error">{{ error }}</p>
      <p class="success-message" v-if="message">{{ message }}</p>

      <div v-if="createdTaskId" class="assign-section">
        <h3>Assign Team Members</h3>
        <select v-model="assignedTo" multiple>
          <option v-for="member in teamMembers" :key="member.id" :value="member.id">
            {{ member.username }}
          </option>
        </select>
        <button class="btn-outline" @click="assignUsers" :disabled="assignedTo.length === 0">Assign</button>
        <p class="success-message" v-if="assignMessage">{{ assignMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CreateTask',
  data() {
    return {
      title: '',
      description: '',
      assignedTo: [],
      startDate: '',
      endDate: '',
      message: '',
      assignMessage: '',
      error: '',
      teamMembers: [],
      createdTaskId: null
    }
  },
  computed: {
    isFormValid() {
      return this.title && this.description && this.startDate && this.endDate
    }
  },
  async created() {
    await this.fetchTeamMembers()
  },
  methods: {
    async fetchTeamMembers() {
      let token = localStorage.getItem('access')
      if (!token) return this.redirectToLogin("Authentication token missing. Please log in.")

      try {
        const res = await axios.get('http://localhost:8000/api/team-members/', {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.teamMembers = res.data
      } catch (err) {
        if (err.response?.status === 401) {
          const newToken = await this.refreshToken()
          if (newToken) return this.fetchTeamMembers()
        }
        this.error = "Failed to load team members. Please log in again."
      }
    },

    async createTask() {
      this.message = ''
      this.error = ''
      this.createdTaskId = null
      let token = localStorage.getItem('access')
      if (!token) return this.redirectToLogin("Please login to create a task.")

      try {
        const res = await axios.post('http://localhost:8000/api/create-task/', {
          title: this.title,
          description: this.description,
          start_date: this.startDate,
          end_date: this.endDate
        }, {
          headers: { Authorization: `Bearer ${token}` }
        })

        this.message = `✅ Task created successfully (ID: ${res.data.task_id})`
        this.createdTaskId = res.data.task_id
        this.resetForm()

      } catch (err) {
        if (err.response?.status === 401) {
          const newToken = await this.refreshToken()
          if (newToken) return this.createTask()
        }
        this.error = err.response?.data?.error || "Failed to create task."
      }
    },

    async assignUsers() {
      let token = localStorage.getItem('access')
      if (!token) return this.redirectToLogin("Please log in to assign users.")

      try {
        await axios.post(`http://localhost:8000/api/assign-task/${this.createdTaskId}/`, {
          assigned_to: this.assignedTo
        }, {
          headers: { Authorization: `Bearer ${token}` }
        })

        this.assignMessage = "✅ Users successfully assigned to the task!"
      } catch (err) {
        if (err.response?.status === 401) {
          const newToken = await this.refreshToken()
          if (newToken) return this.assignUsers()
        }
        this.error = err.response?.data?.error || "Failed to assign users."
      }
    },

    async refreshToken() {
      const refresh = localStorage.getItem('refresh')
      if (!refresh) return this.redirectToLogin("Session expired. Please log in again.")

      try {
        const res = await axios.post('http://localhost:8000/api/refresh-token/', {
          refresh: refresh
        })
        const newAccess = res.data.access
        localStorage.setItem('access', newAccess)
        return newAccess
      } catch (err) {
        return this.redirectToLogin("Session expired. Please log in again.")
      }
    },

    redirectToLogin(msg) {
      this.error = msg
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      setTimeout(() => {
        this.$router.push({ name: 'Login' })
      }, 1500)
    },

    resetForm() {
      this.title = ''
      this.description = ''
      this.startDate = ''
      this.endDate = ''
    },

    goToTaskList() {
      this.$router.push({ name: 'TaskList' })
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

.form-box {
  background: #fff;
  padding: 40px;
  width: 550px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

select[multiple] {
  height: 120px;
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

.btn-outline {
  border: 2px solid #5f2c82;
  background: transparent;
  color: #5f2c82;
  padding: 10px 20px;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.3s;
}

.btn-outline:hover {
  background: #5f2c82;
  color: white;
}

.btn-outline.small {
  padding: 6px 14px;
  font-size: 0.9rem;
  border-width: 1.5px;
}

.success-message {
  color: #198754;
  font-size: 0.95rem;
  margin-top: 10px;
}

.error-message {
  color: #dc3545;
  font-size: 0.95rem;
  margin-top: 10px;
}

.assign-section {
  margin-top: 25px;
}
</style>

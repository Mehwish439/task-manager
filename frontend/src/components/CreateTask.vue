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

        <!-- File Upload -->
        <input type="file" @change="handleFile" />

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
import api from "@/api" // ✅ updated to use api.js

export default {
  name: 'CreateTask',
  data() {
    return {
      title: '',
      description: '',
      assignedTo: [],
      startDate: '',
      endDate: '',
      attachment: null, // ✅ new for file upload
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
      try {
        const res = await api.get('team-members/')
        this.teamMembers = res.data
      } catch (err) {
        this.handleApiError(err, "Failed to load team members. Please log in again.")
      }
    },

    // ✅ handle file selection
    handleFile(e) {
      this.attachment = e.target.files[0]
    },

    async createTask() {
      this.message = ''
      this.error = ''
      this.createdTaskId = null

      try {
        const formData = new FormData()
        formData.append('title', this.title)
        formData.append('description', this.description)
        formData.append('start_date', this.startDate)
        formData.append('end_date', this.endDate)
        if (this.attachment) formData.append('attachment', this.attachment)

        const res = await api.post('create-task/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        this.message = `✅ Task created successfully (ID: ${res.data.task_id})`
        this.createdTaskId = res.data.task_id
        this.resetForm()
      } catch (err) {
        this.handleApiError(err, "Failed to create task.")
      }
    },

    async assignUsers() {
      if (!this.createdTaskId) return
      try {
        await api.post(`assign-task/${this.createdTaskId}/`, { assigned_to: this.assignedTo })
        this.assignMessage = "✅ Users successfully assigned to the task!"
      } catch (err) {
        this.handleApiError(err, "Failed to assign users.")
      }
    },

    handleApiError(err, fallbackMsg) {
      if (err.response?.status === 401) {
        this.redirectToLogin("Session expired. Please log in again.")
      } else {
        this.error = err.response?.data?.error || fallbackMsg
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
      this.attachment = null
    },

    goToTaskList() {
      this.$router.push({ name: 'TaskList' })
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
  background: #159aff;
}

.btn-outline {
  border: 2px solid #159aff;
  background: transparent;
  color: #159aff;
  padding: 10px 20px;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.3s;
}

.btn-outline:hover {
  background: #159aff;
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

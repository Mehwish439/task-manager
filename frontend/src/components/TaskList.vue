<template>
  <div class="task-page">
    <h2>📋 Task List</h2>

    <ul v-if="tasks.length">
      <li v-for="task in tasks" :key="task.id" class="task-card">
        <strong>{{ task.title }}</strong><br /> 
        Description: {{ task.description }}<br />

        <div v-if="task.user_statuses && task.user_statuses.status_breakdown && task.user_statuses.status_breakdown.length">
          <strong>Status Overview:</strong>
          <ul>
            <li v-for="(entry, index) in task.user_statuses.status_breakdown" :key="index">
              {{ entry.user }} ({{ entry.email }}): {{ entry.status }}
            </li>
          </ul>
        </div>
        <div v-else>
          <em>No user status updates yet.</em>
        </div>

        Status: {{ task.status }}<br />
        Dates: {{ task.start_date }} → {{ task.end_date }}<br />

        <div v-if="task.assigned_to.length">
          <strong>Assigned To:</strong>
          <ul>
            <li v-for="user in task.assigned_to" :key="user.id">
              {{ user.username }} ({{ user.email }})
            </li>
          </ul>
        </div>
        <div v-else><em>No one assigned yet.</em></div>

        <div class="assign-section">
          <label>Assign to another member:</label>
          <select v-model="selectedUser[task.id]">
            <option disabled value="">Select team member</option>
            <option v-for="member in teamMembers" :key="member.id" :value="member.id">
              {{ member.username }}
            </option>
          </select>
          <button class="btn-primary" @click="assignUser(task.id)">Assign</button>
        </div>

        <div class="delete-section">
          <button class="btn-danger" @click="showModal(task.id)">🗑️ Delete Task</button>
        </div>
      </li>
    </ul>

    <p v-else>No tasks created yet.</p>
    <p v-if="error" class="error-message">{{ error }}</p>

    <!-- Delete Confirmation Modal -->
    <div class="modal-overlay" v-if="showDeleteModal">
      <div class="modal-box">
        <h3>⚠️ Confirm Deletion</h3>
        <p>Are you sure you want to delete this task?</p>
        <button @click="confirmDelete" class="btn-danger">Yes, Delete</button>
        <button @click="cancelDelete" class="btn-outline">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'TaskList',
  data() {
    return {
      tasks: [],
      teamMembers: [],
      selectedUser: {},
      error: '',
      showDeleteModal: false,
      taskToDelete: null
    }
  },
  mounted() {
    this.fetchCreatedTasks()
    this.fetchTeamMembers()
  },
  methods: {
    async fetchCreatedTasks() {
      const token = localStorage.getItem('access')
      if (!token) return this.$router.push('/login')
      try {
        const res = await axios.get('http://localhost:8000/api/created-tasks/', {
          headers: { Authorization: `Bearer ${token}` }
        })
        const tasksWithStatuses = await Promise.all(
          res.data.map(async (task) => {
            const statusRes = await axios.get(`http://localhost:8000/api/task-status/${task.id}/breakdown/`, {
              headers: { Authorization: `Bearer ${token}` }
            })
            return { ...task, user_statuses: statusRes.data }
          })
        )
        this.tasks = tasksWithStatuses
      } catch (err) {
        this.error = 'Failed to load your task list.'
      }
    },
    async fetchTeamMembers() {
      const token = localStorage.getItem('access')
      try {
        const res = await axios.get('http://localhost:8000/api/team-members/', {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.teamMembers = res.data
      } catch (err) {
        console.error(err)
      }
    },
    async assignUser(taskId) {
      const userId = this.selectedUser[taskId]
      if (!userId) return alert('Please select a team member to assign.')
      const token = localStorage.getItem('access')
      try {
        await axios.post(`http://localhost:8000/api/assign-task/${taskId}/`, {
          assigned_to: [userId]
        }, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.fetchCreatedTasks()
      } catch (err) {
        alert('Could not assign user.')
      }
    },
    showModal(taskId) {
      this.taskToDelete = taskId
      this.showDeleteModal = true
    },
    cancelDelete() {
      this.showDeleteModal = false
      this.taskToDelete = null
    },
    async confirmDelete() {
      const token = localStorage.getItem('access')
      try {
        await axios.delete(`http://localhost:8000/api/delete-task/${this.taskToDelete}/`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.showDeleteModal = false
        this.taskToDelete = null
        this.fetchCreatedTasks()
      } catch (err) {
        alert('You can only delete tasks you created.')
        this.showDeleteModal = false
      }
    }
  }
}
</script>

<style scoped>
.task-page {
  max-width: 900px;
  margin: 40px auto;
  padding: 30px;
  background: linear-gradient(to right, #dfe9f3, #ffffff);
  border-radius: 12px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.task-page h2 {
  font-size: 28px;
  margin-bottom: 24px;
  color: #5f2c82;
  border-bottom: 2px solid #ccc;
  padding-bottom: 12px;
}

.task-card {
  background: #fff;
  padding: 20px;
  margin-bottom: 20px;
  border-left: 5px solid #5f2c82;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.task-card strong {
  font-size: 20px;
  color: #333;
}

.task-card em {
  color: #777;
}

.assign-section,
.delete-section {
  margin-top: 14px;
}

.assign-section label {
  font-weight: 600;
  margin-bottom: 6px;
  display: block;
  color: #5f2c82;
}

.assign-section select {
  padding: 8px;
  font-size: 14px;
  border-radius: 6px;
  border: 1px solid #ccc;
  margin-right: 10px;
}

.btn-primary {
  background: #5f2c82;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.3s;
}
.btn-primary:hover {
  background: #45205f;
}

.btn-danger {
  background: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.3s;
}
.btn-danger:hover {
  background: #c82333;
}

.btn-outline {
  background: transparent;
  border: 2px solid #5f2c82;
  color: #5f2c82;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
}
.btn-outline:hover {
  background: #5f2c82;
  color: white;
}

.error-message {
  color: #dc3545;
  margin-top: 16px;
  font-weight: bold;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-box {
  background: #fff;
  padding: 30px;
  border-radius: 10px;
  width: 90%;
  max-width: 400px;
  text-align: center;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
}

.modal-box h3 {
  margin-bottom: 12px;
  font-size: 20px;
  color: #5f2c82;
}

.modal-box p {
  color: #666;
  margin-bottom: 20px;
}
</style>

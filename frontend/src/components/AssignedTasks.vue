<template>
  <div class="container">
    <div class="task-box">
      <h2 v-if="role === 'team_member'">Your Assigned Tasks</h2>

      <ul v-if="role === 'team_member' && tasks.length">
        <li v-for="task in tasks" :key="task.id" class="task-card">
          <div class="task-header">
            <strong>{{ task.title }}</strong>
          </div>
          <div class="task-body">
            <p><strong>Description:</strong> {{ task.description }}</p>
            <p><strong>Status:</strong> {{ task.status }}</p>
            <p><strong>Start:</strong> {{ task.start_date }} | <strong>End:</strong> {{ task.end_date }}</p>
          </div>

          <div class="status-update">
            <select v-model="task.status">
              <option value="in_progress">In Progress</option>
              <option value="testing">Testing</option>
              <option value="complete">Complete</option>
            </select>
            <button class="btn-primary" @click="updateTask(task)">Update</button>
          </div>

          <!-- Comments section -->
          <div class="comments">
            <CommentListCreate :taskId="task.id" />
          </div>
        </li>
      </ul>

      <p v-else-if="role === 'team_member'" class="message">You have no assigned tasks.</p>
      <p v-else class="error-message">❌ Only team members can view assigned tasks.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import CommentListCreate from './CommentListCreate.vue'

export default {
  components: {
    CommentListCreate
  },
  data() {
    return {
      tasks: [],
      role: null
    }
  },
  mounted() {
    this.fetchTasks()
  },
  methods: {
    async fetchTasks() {
      const token = localStorage.getItem('access')
      if (!token) {
        alert('Please log in to view your tasks.')
        return this.$router.push({ name: 'Login' })
      }

      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        this.role = payload.role

        if (this.role === 'team_member') {
          const res = await axios.get('http://localhost:8000/api/assigned-tasks/', {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.tasks = res.data
        }

      } catch (error) {
        console.error('Failed to fetch tasks:', error)
        alert('Something went wrong while fetching tasks.')
      }
    },

    async updateTask(task) {
      const token = localStorage.getItem('access')
      if (!token) {
        alert('Login required to update task.')
        return
      }

      try {
        await axios.patch(`http://localhost:8000/api/update-task/${task.id}/`, {
          status: task.status
        }, {
          headers: { Authorization: `Bearer ${token}` }
        })
        alert('✅ Task status updated successfully.')
      } catch (error) {
        console.error('Failed to update task status:', error)
        alert('❌ Failed to update task status.')
      }
    }
  }
}
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  background: linear-gradient(to right, #dfe9f3, #ffffff);
  min-height: 100vh;
  padding: 50px 20px;
}

.task-box {
  width: 800px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  padding: 30px 40px;
}

h2 {
  text-align: center;
  color: #5f2c82;
  margin-bottom: 30px;
}

.task-card {
  background-color: #f9f9f9;
  border: 1px solid #ccc;
  border-left: 4px solid #5f2c82;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}

.task-header {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 8px;
}

.task-body p {
  margin: 4px 0;
  font-size: 0.95rem;
  color: #444;
}

.status-update {
  margin-top: 10px;
  display: flex;
  gap: 10px;
  align-items: center;
}

select {
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

button.btn-primary {
  background: #5f2c82;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
}

button.btn-primary:hover {
  background: #45205f;
}

.message {
  text-align: center;
  margin-top: 20px;
  font-size: 1rem;
  color: #666;
}

.error-message {
  text-align: center;
  color: #dc3545;
  font-weight: bold;
}
</style>

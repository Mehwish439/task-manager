<template>
  <div class="comment-section">
    <h4>Comments</h4>

    <div v-if="comments.length">
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        :task-id="taskId"
        :current-user="currentUser"
        @refresh="fetchComments"
      />
    </div>

    <!-- New root comment -->
    <form @submit.prevent="postComment" class="comment-form">
      <textarea v-model="newComment" placeholder="Write a comment..."></textarea>
      <button class="btn-primary" :disabled="!newComment">Post</button>
    </form>

    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<script>
import api from "@/api" // ✅ use api.js
import CommentItem from './CommentItem.vue'

export default {
  components: { CommentItem },
  props: ['taskId'],
  data() {
    return {
      comments: [],
      newComment: '',
      error: '',
      currentUser: null
    }
  },
  mounted() {
    this.getCurrentUser()
    this.fetchComments()
  },
  methods: {
    async getCurrentUser() {
      try {
        const res = await api.get('me/')
        this.currentUser = res.data.username
      } catch (err) {
        console.error('Could not fetch current user.')
      }
    },

    async fetchComments() {
      try {
        const res = await api.get(`tasks/${this.taskId}/comments/`)
        this.comments = res.data
      } catch (err) {
        console.error('Error fetching comments:', err)
        this.error = 'Failed to load comments.'
      }
    },

    async postComment() {
      if (!this.newComment.trim()) return
      try {
        await api.post(`tasks/${this.taskId}/comments/`, { content: this.newComment })
        this.newComment = ''
        this.fetchComments()
      } catch (err) {
        console.error('Error posting comment:', err)
        this.error = 'Could not post comment.'
      }
    }
  }
}
</script>

<style scoped>
* {
  font-family: 'Poppins', sans-serif;
}
.comment-section {
  margin-top: 20px;
  background: #f4f5f7;
  padding: 15px;
  border-radius: 8px;
}

.comment-form {
  display: flex;
  flex-direction: column;
  margin-top: 12px;
  gap: 8px;
}

.comment-form textarea {
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
  resize: vertical;
  min-height: 60px;
}

.btn-primary {
  background: #159aff;
  color: white;
  border: none;
  padding: 8px 14px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
}

.btn-primary:hover {
  background: #159aff;
}

.error-message {
  color: #dc3545;
  font-size: 0.9rem;
  margin-top: 8px;
}
</style>

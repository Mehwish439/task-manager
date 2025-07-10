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
import axios from 'axios'
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
      const token = localStorage.getItem('access')
      try {
        const res = await axios.get('http://localhost:8000/api/me/', {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.currentUser = res.data.username
      } catch (err) {
        console.error('Could not fetch current user.')
      }
    },

    async fetchComments() {
      const token = localStorage.getItem('access')
      try {
        const res = await axios.get(
          `http://localhost:8000/api/tasks/${this.taskId}/comments/`,
          { headers: { Authorization: `Bearer ${token}` } }
        )
        this.comments = res.data
      } catch (err) {
        console.error('Error fetching comments:', err)
        this.error = 'Failed to load comments.'
      }
    },

    async postComment() {
      const token = localStorage.getItem('access')
      if (!token || !this.newComment.trim()) return

      try {
        await axios.post(
          `http://localhost:8000/api/tasks/${this.taskId}/comments/`,
          { content: this.newComment },
          { headers: { Authorization: `Bearer ${token}` } }
        )
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

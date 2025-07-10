<template>
  <div class="comment-block">
    <div class="comment">
      <strong>{{ comment.author_username }}</strong>: {{ comment.content }}
      <small class="timestamp">({{ formatDate(comment.created_at) }})</small>

      <!-- 🔥 Delete button only if it's your comment -->
      <button
        v-if="comment.author_username === currentUser"
        class="btn-delete"
        @click="deleteComment(comment.id)"
        title="Delete comment"
      >
        Delete
      </button>
    </div>

    <!-- Reply Form -->
    <form @submit.prevent="submitReply" class="reply-form">
      <input
        v-model="replyText"
        placeholder="Write a reply..."
      />
      <button class="btn-primary" :disabled="!replyText">Reply</button>
    </form>

    <!-- Recursive replies -->
    <div class="replies" v-if="comment.replies.length">
      <CommentItem
        v-for="child in comment.replies"
        :key="child.id"
        :comment="child"
        :task-id="taskId"
        :current-user="currentUser"
        @refresh="$emit('refresh')"
      />
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CommentItem',
  props: ['comment', 'taskId', 'currentUser'],
  data() {
    return {
      replyText: ''
    }
  },
  methods: {
    async submitReply() {
      const token = localStorage.getItem('access')
      if (!this.replyText.trim()) return

      try {
        await axios.post(
          `http://localhost:8000/api/tasks/${this.taskId}/comments/`,
          {
            content: this.replyText,
            parent: this.comment.id
          },
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        )
        this.replyText = ''
        this.$emit('refresh')
      } catch (err) {
        console.error('Reply failed:', err)
      }
    },

    async deleteComment(id) {
      const token = localStorage.getItem('access')
      if (!confirm("Are you sure you want to delete this comment?")) return

      try {
        await axios.delete(`http://localhost:8000/api/comments/${id}/`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.$emit('refresh')
      } catch (err) {
        console.error('Delete failed:', err)
        alert("❌ You can only delete your own comments.")
      }
    },

    formatDate(datetime) {
      return new Date(datetime).toLocaleString()
    }
  }
}
</script>

<style scoped>
.comment {
  position: relative;
}
.btn-delete {
  position: absolute;
  top: 4px;
  right: 8px;
  background: none;
  border: none;
  color: #dc3545;
  font-size: 0.8rem;
  cursor: pointer;
}
.btn-delete:hover {
  text-decoration: underline;
}
</style>

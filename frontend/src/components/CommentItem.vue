<template>
  <div class="comment-block">
    <div class="comment">
      <div class="comment-header">
        <strong class="comment-author">{{ comment.author_username }}</strong>
        <button
          v-if="comment.author_username === currentUser"
          class="btn-delete"
          @click="deleteComment(comment.id)"
          title="Delete comment"
        >
          Delete
        </button>
      </div>
      <p class="comment-content">{{ comment.content }}</p>
      <small class="timestamp">({{ formatDate(comment.created_at) }})</small>

      <!-- Reply Form -->
      <form @submit.prevent="submitReply" class="reply-form">
        <input v-model="replyText" placeholder="Write a reply..." />
        <button class="btn-primary" :disabled="!replyText">Reply</button>
      </form>

      <!-- Recursive replies -->
      <div class="replies" v-if="comment.replies && comment.replies.length">
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
  </div>
</template>



<script>
import axios from 'axios'

export default {
  name: 'CommentItem',
  props: ['comment', 'taskId', 'currentUser'],
  data() { return { replyText: '' } },
  methods: {
    async submitReply() {
      if (!this.replyText.trim()) return
      try {
        const token = localStorage.getItem('access')
        await axios.post(
          `${import.meta.env.VITE_API_URL}/tasks/${this.taskId}/comments/`,
          { content: this.replyText, parent: this.comment.id },
          { headers: { Authorization: `Bearer ${token}` } }
        )
        this.replyText = ''
        this.$emit('refresh')
      } catch (err) {
        console.error('Reply failed:', err)
      }
    },

    async deleteComment(id) {
      if (!confirm("Are you sure you want to delete this comment?")) return
      try {
        const token = localStorage.getItem('access')
        await axios.delete(`${import.meta.env.VITE_API_URL}/comments/${id}/`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.$emit('refresh')
      } catch (err) {
        console.error('Delete failed:', err)
        alert(" You can only delete your own comments.")
      }
    },

    formatDate(dt) { return new Date(dt).toLocaleString() }
  }
}
</script>

<style scoped>
* {
  font-family: 'Poppins', sans-serif;
}
.comment-block { margin-top: 10px; }

.comment { padding: 10px 14px; background:#f9f9f9; border-radius:8px; margin-bottom:6px; box-shadow:0 1px 3px rgba(0,0,0,0.05); }

.comment-header { display: flex; justify-content: space-between; align-items: center; }

.comment-author { color:#159aff; font-weight:600; }

.comment-content { margin:4px 0; }

.btn-delete { background:none; border:none; color:#159aff; cursor:pointer; font-size:0.8rem; }
.btn-delete:hover { text-decoration:underline; }

.reply-form { display:flex; gap:8px; margin-top:6px; }
.reply-form input { flex:1; padding:6px 8px; border-radius:6px; border:1px solid #ccc; }

.replies { margin-left:20px; margin-top:6px; border-left:1px solid #e0e0e0; padding-left:10px; }

.btn-primary { background:#159aff; color:#fff; border:none; padding:6px 10px; border-radius:6px; cursor:pointer; }
.btn-primary:hover { background:#159aff; }
</style>

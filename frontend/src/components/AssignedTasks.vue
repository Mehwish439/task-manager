<template>
  <div class="dashboard">

    <!-- ===== SIDEBAR ===== -->
    <aside :class="['sidebar', { 'sidebar-open': sidebarOpen }]">
      <div class="sidebar-header">
        <h2 class="brand">QRM Task Manager</h2>
        <button class="hamburger-btn" @click="sidebarOpen = !sidebarOpen">
          <svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24" width="24" height="24">
            <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <nav class="sidebar-nav">
        <button class="sidebar-btn" :class="{ active: selectedTab === 'attendance' }" @click="selectedTab = 'attendance'; sidebarOpen=false">
          <svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24" width="20" height="20">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>Attendance</span>
        </button>

        <button class="sidebar-btn" :class="{ active: selectedTab === 'tasks' }" @click="selectedTab = 'tasks'; sidebarOpen=false">
          <svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24" width="20" height="20">
            <path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M9 2h6v4H9zM5 6h14v16H5z"/>
          </svg>
          <span>Tasks</span>
        </button>

        <button class="sidebar-btn" :class="{ active: selectedTab === 'taskCalendar' }" @click="selectedTab = 'taskCalendar'; sidebarOpen=false">
          <svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24" width="20" height="20">
            <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M16 2v4M8 2v4M3 10h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>Task Calendar</span>
        </button>

        <button class="sidebar-btn" :class="{ active: selectedTab === 'activity' }" @click="selectedTab = 'activity'; sidebarOpen=false">
          <svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24" width="20" height="20">
            <path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M3 12h4l3-9 4 18 3-9h4"/>
          </svg>
          <span>My Activity</span>
        </button>

        <button class="sidebar-btn" :class="{ active: selectedTab === 'globalChat' }" @click="selectedTab = 'globalChat'; sidebarOpen=false">
          <svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24" width="20" height="20">
            <path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z"/>
          </svg>
          <span>Group Chat</span>
          <span v-if="unreadCount > 0" class="chat-badge">{{ unreadCount }}</span>
        </button>

        <button class="sidebar-btn" :class="{ active: selectedTab === 'profile' }" @click="selectedTab = 'profile'; sidebarOpen=false">
          <svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24" width="20" height="20">
            <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="2" fill="none"/>
            <path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M6 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
          </svg>
          <span>Profile</span>
        </button>

        <button class="sidebar-btn logout-btn" @click="handleLogout">
          <svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24" width="20" height="20">
            <rect x="5" y="11" width="14" height="10" stroke="currentColor" stroke-width="2" fill="none"/>
            <path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          <span>Logout</span>
        </button>
      </nav>
    </aside>

    <!-- ===== OVERLAY FOR MOBILE ===== -->
    <div v-if="sidebarOpen" class="overlay" @click="sidebarOpen = false"></div>

    <!-- ===== MAIN CONTENT ===== -->
    <main class="main-content">

      <!-- HEADER -->
      <header class="top-header" @click="showNotifications=false">
        <h1>Dashboard</h1>
        <div class="header-right" @click.stop>
          <div class="avatar-circle">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
              <circle cx="12" cy="8" r="4" stroke="#000" stroke-width="2" fill="none"/>
              <path stroke="#000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M6 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
            </svg>
          </div>
          <div class="header-user-info">
            <span class="user-name">{{ userProfile.username }}</span>
            <span class="user-email">{{ userProfile.email }}</span>
          </div>

          <!-- Live tracking indicator -->
          <div class="tracking-indicator" :class="{ idle: isIdle, stopped: !trackingEnabled }">
            <span class="tracking-dot"></span>
            <span class="tracking-label">{{ trackingStatus }}</span>
          </div>

          <!-- START / STOP TRACKING BUTTON -->
          <button
            class="track-toggle-btn"
            :class="trackingEnabled ? 'btn-stop-track' : 'btn-start-track'"
            @click="toggleTracking"
          >
            <svg v-if="trackingEnabled" xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="6" width="12" height="12" rx="2"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5,3 19,12 5,21"/>
            </svg>
            {{ trackingEnabled ? 'Stop' : 'Start' }}
          </button>

          <div class="notification-bell" @click="toggleNotifications">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
              <path stroke="#000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-5-5.917V4a1 1 0 10-2 0v1.083A6 6 0 006 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1h6z"/>
            </svg>
            <span v-if="notifications.length > 0" class="notif-count blink">{{ notifications.length }}</span>
          </div>

          <div v-if="showNotifications" class="notification-panel">
            <p v-if="notifications.length === 0" class="empty-notif">No new notifications</p>
            <div v-for="(notif, index) in notifications" :key="index" class="notification-item">{{ notif }}</div>
          </div>
        </div>
      </header>

      <!-- ===== STATS CARDS ===== -->
      <div v-if="selectedTab === 'attendance' || selectedTab === 'tasks'" class="dashboard-cards">
        <div class="card gradient">
          <p class="card-title">Total Hours This Week</p>
          <p class="card-value">32.5</p>
        </div>
        <div class="card gradient">
          <p class="card-title">Avg Login</p>
          <p class="card-value">8:45 AM</p>
        </div>
        <div class="card gradient">
          <p class="card-title">Leave Days</p>
          <p class="card-value">15</p>
        </div>
      </div>

      <!-- ===== PANELS ===== -->
      <div class="main-panels">

        <!-- ATTENDANCE -->
        <section v-if="selectedTab === 'attendance'" class="panel">
          <h2 class="panel-title">Daily Attendance</h2>
          <div class="attendance-card">
            <div class="attendance-field">
              <label>Check-In</label>
              <input type="time" v-model="daily.manualCheckIn" :disabled="!canClockIn"/>
              <button class="btn-gradient" @click="dailyClockIn" :disabled="!canClockIn">Check In</button>
            </div>
            <div class="attendance-field">
              <label>Check-Out</label>
              <input type="time" v-model="daily.manualCheckOut" :disabled="!canClockOut"/>
              <button class="btn-gradient" @click="dailyClockOut" :disabled="!canClockOut">Check Out</button>
              <div class="break-controls">
                <button class="btn-gradient pause-btn" @click="pauseWork" :disabled="isPaused">Pause</button>
                <button class="btn-gradient resume-btn" @click="resumeWork" :disabled="!isPaused">Resume</button>
              </div>
            </div>
          </div>
          <div class="status-container">
            <span v-if="daily.clockedIn && !daily.systemCheckOut" class="status working">Working Today</span>
            <span v-if="daily.systemCheckOut" class="status done">Attendance Completed</span>
          </div>
        </section>

        <!-- TASKS -->
        <section v-if="selectedTab === 'tasks'" class="panel">
          <h2 class="panel-title gradient-text">Your Assigned Tasks</h2>
          <ul v-if="tasks.length" class="task-grid">
            <li v-for="task in tasks" :key="task.id" class="task-card">
              <div class="task-header">
                <strong class="task-title gradient-text">{{ task.title }}</strong>
                <span class="badge" :class="task.status">{{ task.status }}</span>
              </div>
              <p class="task-desc">{{ task.description }}</p>
              <p><strong>Start Date:</strong> {{ formatDate(task.start_date) }}</p>
              <p><strong>End Date:</strong> {{ formatDate(task.end_date) }}</p>
              <div v-if="task.attachment_url" class="task-attachment" style="margin:10px 0;display:flex;align-items:center;gap:6px;">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 12v6m0 0l3-3m-3 3l-3-3m6-6v6a2 2 0 01-2 2h-4a2 2 0 01-2-2v-6a2 2 0 012-2h4a2 2 0 012 2z"/>
                </svg>
                <a :href="task.attachment_url" target="_blank" download style="color:#159aff;text-decoration:underline;">Download Attachment</a>
              </div>
              <select v-model="task.status" @change="updateTaskStatus(task)" class="status-select">
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="complete">Complete</option>
              </select>
              <div class="comment-box">
                <CommentListCreate :taskId="task.id" :current-user="userProfile.username" @refresh="fetchTasks"/>
              </div>
            </li>
          </ul>
          <p v-else class="empty">No assigned tasks.</p>
        </section>

        <!-- TASK CALENDAR -->
        <section v-if="selectedTab === 'taskCalendar'" class="panel">
          <h2 class="panel-title gradient-text">Task Calendar</h2>
          <div class="calendar-controls">
            <label for="calendar-date">Select Date:</label>
            <input type="date" id="calendar-date" v-model="selectedDate" @change="filterTasksByDate"/>
          </div>
          <div class="calendar-grid">
            <div class="calendar-day header" v-for="day in weekdays" :key="day">{{ day }}</div>
            <div class="calendar-day blank" v-for="n in firstDayOffset" :key="'blank-'+n"></div>
            <div v-for="day in daysInMonth" :key="day" class="calendar-day" :class="{ today: isToday(day), selected: isSelected(day) }">
              <div class="day-number">{{ day }}</div>
              <div class="events">
                <div v-for="task in tasksByDate(day)" :key="task.id" class="event" :class="task.status" :title="`Assigned to: ${task.assignee || 'N/A'}`">
                  {{ task.title }}
                  <small v-if="task.assignee">({{ task.assignee }})</small>
                </div>
              </div>
            </div>
          </div>
          <ul class="task-list">
            <li v-for="task in filteredTasks" :key="task.id">
              <h3>{{ task.title }} <span>({{ task.status }})</span></h3>
              <p>{{ task.description }}</p>
              <p>
                <strong>Assignee:</strong> {{ task.assignee || 'N/A' }} |
                <strong>Start:</strong> {{ formatDate(task.start_date) }} |
                <strong>End:</strong> {{ formatDate(task.end_date) }}
              </p>
            </li>
          </ul>
        </section>

        <!-- ===== MY ACTIVITY TAB ===== -->
        <section v-if="selectedTab === 'activity'" class="panel">
          <h2 class="panel-title gradient-text">My Activity</h2>

          <!-- Tracking control banner -->
          <div class="tracking-control-banner" :class="trackingEnabled ? (isIdle ? 'banner-idle' : 'banner-active') : 'banner-stopped'">
            <div class="banner-left">
              <span class="banner-dot"></span>
              <span class="banner-text">
                {{ trackingEnabled ? (isIdle ? 'Currently idle — no input detected for 3 minutes' : 'Tracking active — recording your activity') : 'Tracking is stopped. Click Start to begin recording.' }}
              </span>
            </div>
            <div class="banner-right">
              <button
                class="track-toggle-btn"
                :class="trackingEnabled ? 'btn-stop-track' : 'btn-start-track'"
                @click="toggleTracking"
              >
                <svg v-if="trackingEnabled" xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21"/></svg>
                {{ trackingEnabled ? 'Stop Tracking' : 'Start Tracking' }}
              </button>
            </div>
          </div>

          <div class="activity-date-row">
            <label>Date:</label>
            <input type="date" v-model="activityDate" @change="fetchMyActivity"/>
            <button class="btn-gradient" @click="fetchMyActivity">Refresh</button>
            <button class="btn-gradient save-btn" @click="saveDailyActivity" :disabled="savingActivity" v-if="activityDate === todayDate">
              {{ savingActivity ? 'Saving…' : '💾 Save Today' }}
            </button>
            <span class="save-status" v-if="lastSaved">Saved {{ lastSaved }}</span>
          </div>

          <div v-if="activityLoading" class="act-loading">Loading…</div>

          <template v-else>

            <!-- Live note -->
            <div class="act-live-note" v-if="activityDate === todayDate">
              <span class="act-live-dot"></span> Live — updates every 30 s
            </div>

            <!-- TOTAL BANNER -->
            <div class="act-banner-row">
              <div class="act-banner-card active-card">
                <p class="act-banner-label">Total active</p>
                <p class="act-banner-value">{{ displayActiveFmt }}</p>
              </div>
              <div class="act-banner-card idle-card">
                <p class="act-banner-label">Total idle</p>
                <p class="act-banner-value">{{ displayIdleFmt }}</p>
              </div>
              <div class="act-banner-card total-card">
                <p class="act-banner-label">Tracked total</p>
                <p class="act-banner-value">{{ displayTotalFmt }}</p>
              </div>
              <div class="act-banner-card pct-card">
                <p class="act-banner-label">Active %</p>
                <p class="act-banner-value">{{ displayActivePct }}%</p>
                <div class="act-pct-bar-wrap">
                  <div class="act-pct-bar" :style="{ width: displayActivePct + '%' }"></div>
                </div>
              </div>
            </div>

            <!-- PERIOD TIMELINE -->
            <div class="act-timeline-section">
              <h3 class="act-section-label">Active / idle timeline</h3>

              <div v-if="activityDate === todayDate">
                <div v-if="localPeriods.length === 0" class="act-empty">
                  No periods recorded yet today. Start tracking above.
                </div>
                <div v-else class="act-period-list">
                  <div v-for="(p, i) in localPeriods" :key="i" class="act-period-row" :class="p.type">
                    <span class="act-period-badge" :class="p.type">
                      {{ p.type === 'active' ? 'Active' : 'Idle' }}
                    </span>
                    <span class="act-period-range">
                      {{ fmtTime(p.from) }} → {{ fmtTime(p.to) }}
                    </span>
                    <span class="act-period-dur">{{ fmtDuration(p.seconds) }}</span>
                  </div>
                </div>
              </div>

              <div v-else>
                <div v-if="activityPeriods.length === 0" class="act-empty">
                  No period data found for {{ activityDate }}.
                </div>
                <div v-else class="act-period-list">
                  <div v-for="(p, i) in activityPeriods" :key="i" class="act-period-row" :class="p.type">
                    <span class="act-period-badge" :class="p.type">
                      {{ p.type === 'active' ? 'Active' : 'Idle' }}
                    </span>
                    <span class="act-period-range">{{ p.from }} → {{ p.to }}</span>
                    <span class="act-period-dur">{{ p.duration }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 7-DAY HISTORY -->
            <div v-if="activityHistory.length" class="act-history-section">
              <h3 class="act-section-label">Last 7 days</h3>
              <table class="history-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Active</th>
                    <th>Idle</th>
                    <th>Active %</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in activityHistory" :key="row.date">
                    <td>{{ row.date }}</td>
                    <td><strong style="color:#27ae60;">{{ row.active_time_formatted }}</strong></td>
                    <td style="color:#e67e22;">{{ row.idle_time_formatted }}</td>
                    <td>
                      <div class="hist-pct-wrap">
                        <div class="hist-pct-bar" :style="{ width: row.active_percentage + '%' }"></div>
                        <span>{{ row.active_percentage }}%</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

          </template>
        </section>

        <!-- GLOBAL CHAT -->
        <section v-if="selectedTab === 'globalChat'" class="panel">
          <h2 class="panel-title gradient-text">Group Chat</h2>
          <div class="chat-container" style="max-height:500px;overflow-y:auto;border:1px solid #ccc;padding:10px;border-radius:12px;margin-bottom:12px;">
            <div v-for="msg in messages" :key="msg.id" style="margin-bottom:8px;">
              <strong>{{ msg.sender_username }}:</strong> {{ msg.message }}
              <span style="font-size:0.75rem;color:#000;">({{ formatDateTime(msg.created_at) }})</span>
            </div>
          </div>
          <div style="display:flex;gap:6px;">
            <input type="text" v-model="newMessage" placeholder="Type your message..." style="flex:1;padding:8px;border-radius:8px;border:1px solid #ccc;">
            <button class="btn-gradient" @click="sendMessage">Send</button>
            <button class="btn-gradient" @click="clearChat">Clear</button>
          </div>
        </section>

        <!-- PROFILE -->
        <section v-if="selectedTab === 'profile'" class="panel">
          <h2 class="panel-title">Profile</h2>
          <div class="profile-form">
            <div class="form-field">
              <label>Username</label>
              <input v-model="userProfile.username" type="text"/>
            </div>
            <div class="form-field">
              <label>Email</label>
              <input v-model="userProfile.email" type="email"/>
            </div>
            <div class="form-field">
              <label>Password</label>
              <input v-model="userProfile.password" type="password" placeholder="Leave blank to keep current password"/>
            </div>
            <div class="form-field" style="margin-top:20px;">
              <label>Destination</label>
              <input v-model="userProfile.destination" type="text" placeholder="Enter destination (frontend only)"/>
              <button class="btn-gradient" @click="saveDestination" style="margin-top:8px;">Save Destination</button>
            </div>
            <button class="btn-gradient" @click="updateUserProfile">Save Changes</button>
          </div>
        </section>

      </div>
    </main>
  </div>
</template>

<script>
import axios from "axios"
import CommentListCreate from "./CommentListCreate.vue"

const API_BASE = import.meta.env.VITE_API_URL

export default {
  name: "EmployeeDashboard",
  components: { CommentListCreate },

  data() {
    return {
      selectedTab: "attendance",
      sidebarOpen: false,
      tasks: [],
      isPaused: false,
      daily: {
        manualCheckIn: "",
        manualCheckOut: "",
        clockedIn: false,
        systemCheckIn: null,
        systemCheckOut: null
      },
      userProfile: { username: "", email: "", password: "", destination: "" },
      savedDestination: "",
      messages: [],
      newMessage: "",
      unreadCount: 0,
      notifications: [],
      showNotifications: false,

      // ===== Calendar =====
      selectedDate: new Date().toISOString().split("T")[0],
      weekdays: ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],
      daysInMonth: [],
      firstDayOffset: 0,
      filteredTasks: [],

      // ===== Activity Tab =====
      activityDate: new Date().toISOString().split("T")[0],
      activitySummary: null,
      activityPeriods: [],
      activityHistory: [],
      activityLoading: false,

      // ===== Tracking state =====
      trackingEnabled: false,
      savingActivity: false,
      lastSaved: null,

      // ===== Intervals =====
      trackingInterval:  null,
      idleCheckInterval: null,
      chatInterval:      null,
      reminderInterval:  null,
      saveInterval:      null,

      lastActivityTime: Date.now(),
      isIdle: false,

      IDLE_THRESHOLD_MS: 180000,
      PING_INTERVAL_MS:  30000,
      IDLE_CHECK_MS:     10000,

      localPeriods: [],
      currentPeriodType: 'active',
      currentPeriodStart: new Date(),
    }
  },

  computed: {
    currentTime() { return new Date() },
    isBefore6PM() { return this.currentTime.getHours() < 18 },
    canClockIn()  { return !(this.daily.clockedIn || this.daily.systemCheckIn) },
    canClockOut() {
      return (
        (this.daily.clockedIn || this.daily.systemCheckIn) &&
        !this.daily.systemCheckOut
      ) || this.isBefore6PM
    },

    todayDate() {
      return new Date().toISOString().split("T")[0]
    },

    trackingStatus() {
      if (!this.trackingEnabled) return 'Stopped'
      return this.isIdle ? 'Idle' : 'Active'
    },

    displayActiveSeconds() {
      if (this.activityDate === this.todayDate) {
        return this.localPeriods
          .filter(p => p.type === 'active')
          .reduce((s, p) => s + p.seconds, 0)
      }
      return this.activitySummary ? this.activitySummary.total_active_seconds : 0
    },
    displayIdleSeconds() {
      if (this.activityDate === this.todayDate) {
        return this.localPeriods
          .filter(p => p.type === 'idle')
          .reduce((s, p) => s + p.seconds, 0)
      }
      return this.activitySummary ? this.activitySummary.total_idle_seconds : 0
    },
    displayTotalSeconds() {
      return this.displayActiveSeconds + this.displayIdleSeconds
    },
    displayActiveFmt()  { return this._fmtSec(this.displayActiveSeconds) },
    displayIdleFmt()    { return this._fmtSec(this.displayIdleSeconds) },
    displayTotalFmt()   { return this._fmtSec(this.displayTotalSeconds) },
    displayActivePct() {
      if (!this.displayTotalSeconds) return 0
      return Math.round((this.displayActiveSeconds / this.displayTotalSeconds) * 100)
    }
  },

  mounted() {
    this.initDashboard()
    this.generateCalendar()
    // Do NOT auto-start tracking — employee must click Start
  },

  beforeUnmount() {
    this._stopAllIntervals()
    this._removeActivityListeners()
    document.removeEventListener("click", this.hideNotifications)
  },

  methods: {

    // ─────────────────────────────────────────
    // BOOTSTRAP
    // ─────────────────────────────────────────
    async initDashboard() {
      await this.fetchUserProfile()
      this.fetchTasks()
      this.fetchDailyAttendance()
      this.fetchChatMessages()
      this.fetchMyActivity()
      this.fetchActivityHistory()
      this.chatInterval     = setInterval(this.fetchChatMessages, 3000)
      this.reminderInterval = setInterval(this.checkReminders, 60000)
      document.addEventListener("click", this.hideNotifications)
    },

    // ─────────────────────────────────────────
    // GENERIC API HELPER
    // ─────────────────────────────────────────
    async apiCall(method, url, data = null) {
      try {
        const token = localStorage.getItem("access")
        const config = {
          method,
          url: `${API_BASE}${url}`,
          headers: { Authorization: token ? `Bearer ${token}` : "" }
        }
        if (data && method.toLowerCase() !== "get") {
          config.headers["Content-Type"] = "application/json"
          config.data = data
        }
        const res = await axios(config)
        return res.data
      } catch (err) {
        console.error("API error:", err.response || err)
        throw err
      }
    },

    // ─────────────────────────────────────────
    // TRACKING — START / STOP
    // ─────────────────────────────────────────
    toggleTracking() {
      if (this.trackingEnabled) {
        this.stopTracking()
      } else {
        this.startTracking()
      }
    },

    startTracking() {
      if (this.trackingEnabled) return
      this.trackingEnabled    = true
      this.currentPeriodStart = new Date()
      this.currentPeriodType  = 'active'
      this.lastActivityTime   = Date.now()
      this.isIdle             = false

      const opts = { passive: true }
      window.addEventListener("mousemove",  this.onActivity, opts)
      window.addEventListener("keydown",    this.onActivity, opts)
      window.addEventListener("mousedown",  this.onActivity, opts)
      window.addEventListener("touchstart", this.onActivity, opts)
      window.addEventListener("scroll",     this.onActivity, opts)

      this.trackingInterval  = setInterval(this.sendHeartbeat,   this.PING_INTERVAL_MS)
      this.idleCheckInterval = setInterval(this.checkIdleFlip,   this.IDLE_CHECK_MS)
      // Auto-save every 10 minutes
      this.saveInterval      = setInterval(this.saveDailyActivity, 10 * 60 * 1000)

      // Notify backend
      this.apiCall("post", "track-activity/", {
        event_type: "active", active_window: "Tracking started", seconds: 0
      }).catch(() => {})
    },

    stopTracking() {
      if (!this.trackingEnabled) return

      // Close current open period
      this._closePeriod(this.currentPeriodType)

      this.trackingEnabled = false
      this.isIdle          = false

      this._stopAllIntervals()
      this._removeActivityListeners()

      // Final save
      this.saveDailyActivity()

      // Notify backend
      this.apiCall("post", "track-activity/", {
        event_type: "idle", active_window: "Tracking stopped", seconds: 0
      }).catch(() => {})
    },

    _stopAllIntervals() {
      clearInterval(this.trackingInterval)
      clearInterval(this.idleCheckInterval)
      clearInterval(this.saveInterval)
      this.trackingInterval  = null
      this.idleCheckInterval = null
      this.saveInterval      = null
    },

    _removeActivityListeners() {
      window.removeEventListener("mousemove",  this.onActivity)
      window.removeEventListener("keydown",    this.onActivity)
      window.removeEventListener("mousedown",  this.onActivity)
      window.removeEventListener("touchstart", this.onActivity)
      window.removeEventListener("scroll",     this.onActivity)
    },

    // ─────────────────────────────────────────
    // ACTIVITY RECORDING
    // ─────────────────────────────────────────
    onActivity() {
      if (!this.trackingEnabled) return
      const wasIdle     = this.isIdle
      this.lastActivityTime = Date.now()
      this.isIdle           = false

      if (wasIdle) {
        this._closePeriod('idle')
        this.currentPeriodType  = 'active'
        this.currentPeriodStart = new Date()
      }
    },

    checkIdleFlip() {
      if (!this.trackingEnabled) return
      const idleNow = (Date.now() - this.lastActivityTime) > this.IDLE_THRESHOLD_MS
      if (idleNow && !this.isIdle) {
        this.isIdle = true
        this._closePeriod('active')
        this.currentPeriodType  = 'idle'
        this.currentPeriodStart = new Date()
      }
    },

    _closePeriod(type) {
      const now     = new Date()
      const seconds = Math.round((now - this.currentPeriodStart) / 1000)
      if (seconds < 1) return
      this.localPeriods.push({
        type,
        from:    new Date(this.currentPeriodStart),
        to:      now,
        seconds
      })
    },

    async sendHeartbeat() {
      if (!this.trackingEnabled || !localStorage.getItem("access")) return
      const idleNow = (Date.now() - this.lastActivityTime) > this.IDLE_THRESHOLD_MS
      this.isIdle   = idleNow
      try {
        await this.apiCall("post", "track-activity/", {
          event_type:    idleNow ? "idle" : "active",
          seconds:       30,
          active_window: "browser"
        })
      } catch (err) {
        console.warn("Heartbeat failed:", err)
      }
    },

    // Explicitly save today's activity to backend
    async saveDailyActivity() {
      if (this.savingActivity) return
      this.savingActivity = true
      try {
        const activeSeconds = this.localPeriods
          .filter(p => p.type === 'active')
          .reduce((s, p) => s + p.seconds, 0)
        const idleSeconds = this.localPeriods
          .filter(p => p.type === 'idle')
          .reduce((s, p) => s + p.seconds, 0)

        await this.apiCall("post", "activity/save-daily/", {
          date:                 this.todayDate,
          total_active_seconds: activeSeconds,
          total_idle_seconds:   idleSeconds,
          periods: this.localPeriods.map(p => ({
            type:    p.type,
            from:    p.from instanceof Date ? p.from.toISOString() : p.from,
            to:      p.to instanceof Date   ? p.to.toISOString()   : p.to,
            seconds: p.seconds
          }))
        })

        const now    = new Date()
        this.lastSaved = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      } catch (err) {
        console.error("Save daily failed:", err)
      } finally {
        this.savingActivity = false
      }
    },

    // ─────────────────────────────────────────
    // ACTIVITY TAB — fetch from backend
    // ─────────────────────────────────────────
    async fetchMyActivity() {
      this.activityLoading = true
      this.activitySummary = null
      this.activityPeriods = []
      try {
        const data = await this.apiCall("get", `activity/summary/?date=${this.activityDate}`)
        this.activitySummary = data.summary || null

        if (this.activityDate !== this.todayDate && data.summary) {
          const logs = await this.apiCall("get", `activity/logs/?date=${this.activityDate}`)
          this.activityPeriods = this._buildPeriodsFromLogs(logs)
        }
      } catch (err) {
        console.error("Activity fetch error:", err)
      } finally {
        this.activityLoading = false
      }
    },

    async fetchActivityHistory() {
      try {
        const data         = await this.apiCall("get", "activity/history/?days=7")
        this.activityHistory = data.history || []
      } catch (err) {
        console.error("History fetch error:", err)
      }
    },

    // ─────────────────────────────────────────
    // PERIOD HELPERS
    // ─────────────────────────────────────────
    _buildPeriodsFromLogs(logsData) {
      const logs = Array.isArray(logsData) ? logsData : (logsData.results || [])
      if (!logs.length) return []

      const sorted  = [...logs].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
      const periods = []
      let current   = null

      sorted.forEach(log => {
        const type = log.event_type === 'idle' ? 'idle' : 'active'
        const ts   = new Date(log.timestamp)

        if (!current || current.type !== type) {
          if (current) {
            current.to       = ts
            current.seconds  = Math.round((ts - new Date(current._fromRaw)) / 1000)
            current.duration = this._fmtSec(current.seconds)
            periods.push(current)
          }
          current = {
            type,
            from:     this.fmtTime(ts),
            _fromRaw: ts,
            to:       null,
            seconds:  0,
            duration: ''
          }
        }
      })

      if (current) {
        const last       = new Date(sorted[sorted.length - 1].timestamp)
        current.to       = last
        current.seconds  = Math.round((last - new Date(current._fromRaw)) / 1000)
        current.duration = this._fmtSec(current.seconds)
        current.to       = this.fmtTime(last)
        periods.push(current)
      }
      return periods
    },

    fmtTime(date) {
      if (!date) return ''
      const d = date instanceof Date ? date : new Date(date)
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },

    fmtDuration(seconds) { return this._fmtSec(seconds) },

    _fmtSec(s) {
      if (!s || s < 60) return (s || 0) + 's'
      const h = Math.floor(s / 3600)
      const m = Math.floor((s % 3600) / 60)
      return h > 0 ? `${h}h ${m}m` : `${m}m`
    },

    // ─────────────────────────────────────────
    // TASKS
    // ─────────────────────────────────────────
    async fetchTasks() {
      this.tasks = await this.apiCall("get", "assigned-tasks/")
      this.taskReminder()
      this.filterTasksByDate()
    },

    async updateTaskStatus(task) {
      await this.apiCall("patch", `task-status/${task.id}/breakdown/`, { status: task.status })
      alert("Task updated")
      this.taskReminder()
      this.filterTasksByDate()
    },

    // ─────────────────────────────────────────
    // ATTENDANCE
    // ─────────────────────────────────────────
    async fetchDailyAttendance() {
      try {
        const res   = await this.apiCall("get", "attendance/")
        const today = new Date().toISOString().split("T")[0]
        const record = Array.isArray(res)
          ? res.find(r => r.date === today)
          : null
        if (record) {
          this.daily.systemCheckIn  = record.system_check_in
          this.daily.systemCheckOut = record.system_check_out
          this.daily.clockedIn      = true
        }
        this.checkAttendanceReminder()
      } catch (err) {
        console.error("Attendance fetch error:", err)
      }
    },

    async dailyClockIn() {
      await this.apiCall("post", "attendance/check-in/", {
        manual_check_in: this.daily.manualCheckIn + ":00"
      })
      alert("Checked in")
      this.fetchDailyAttendance()
    },

    async dailyClockOut() {
      await this.apiCall("post", "attendance/check-out/", {
        manual_check_out: this.daily.manualCheckOut + ":00"
      })
      alert("Checked out")
      this.fetchDailyAttendance()
    },

    async pauseWork() {
      try {
        await this.apiCall("post", "attendance/pause/")
        this.isPaused = true
        alert("Break started")
      } catch (err) {
        alert("Cannot start break")
      }
    },

    async resumeWork() {
      try {
        await this.apiCall("post", "attendance/resume/")
        this.isPaused = false
        alert("Work resumed")
      } catch (err) {
        alert("Cannot resume work")
      }
    },

    // ─────────────────────────────────────────
    // CHAT
    // ─────────────────────────────────────────
    async fetchChatMessages() {
      try {
        const data     = await this.apiCall("get", "group-chat/")
        this.messages  = Array.isArray(data) ? data : (data.results || [])
        this.unreadCount = this.messages.filter(
          m => !m.read && m.sender_username !== this.userProfile.username
        ).length
      } catch (err) {
        console.error("Chat fetch error:", err)
        this.messages = []
      }
    },

    async sendMessage() {
      if (!this.newMessage.trim()) return
      await this.apiCall("post", "group-chat/", { message: this.newMessage })
      this.newMessage = ""
      await this.fetchChatMessages()
    },

    async clearChat() {
      if (!confirm("Clear all messages?")) return
      await this.apiCall("post", "group-chat-clear/")
      await this.fetchChatMessages()
    },

    // ─────────────────────────────────────────
    // PROFILE
    // ─────────────────────────────────────────
    async fetchUserProfile() {
      try {
        const data                    = await this.apiCall("get", "me/")
        this.userProfile.username     = data.username || ""
        this.userProfile.email        = data.email    || ""
        this.userProfile.password     = ""
      } catch (err) {
        console.error("Profile fetch error:", err)
      }
    },

    async updateUserProfile() {
      try {
        const payload = {
          username: this.userProfile.username,
          email:    this.userProfile.email
        }
        if (this.userProfile.password) payload.password = this.userProfile.password
        await this.apiCall("patch", "me/update/", payload)
        alert("Profile updated successfully")
        this.userProfile.password = ""
        await this.fetchUserProfile()
      } catch (err) {
        const errMsg = err.response?.data?.error || "Failed to update profile"
        alert(errMsg)
      }
    },

    // ─────────────────────────────────────────
    // CALENDAR
    // ─────────────────────────────────────────
    generateCalendar() {
      const date  = new Date(this.selectedDate)
      const year  = date.getFullYear()
      const month = date.getMonth()
      const days  = new Date(year, month + 1, 0).getDate()
      this.daysInMonth    = Array.from({ length: days }, (_, i) => i + 1)
      this.firstDayOffset = new Date(year, month, 1).getDay()
    },

    filterTasksByDate() {
      const d          = this.selectedDate
      this.filteredTasks = this.tasks.filter(t => t.start_date <= d && t.end_date >= d)
    },

    isToday(day) {
      const today = new Date()
      const d     = new Date(this.selectedDate)
      return (
        today.getDate()     === day &&
        today.getMonth()    === d.getMonth() &&
        today.getFullYear() === d.getFullYear()
      )
    },

    isSelected(day) {
      return new Date(this.selectedDate).getDate() === day
    },

    tasksByDate(day) {
      const d      = new Date(this.selectedDate)
      const target = new Date(d.getFullYear(), d.getMonth(), day)
        .toISOString().split("T")[0]
      return this.tasks.filter(t => t.start_date <= target && t.end_date >= target)
    },

    // ─────────────────────────────────────────
    // MISC
    // ─────────────────────────────────────────
    handleLogout() {
      if (this.trackingEnabled) this.stopTracking()
      localStorage.clear()
      this.$router.push("/login")
    },

    formatDate(dateStr)     { return dateStr ? new Date(dateStr).toLocaleDateString() : "-" },
    formatDateTime(dateStr) { return dateStr ? new Date(dateStr).toLocaleString()     : "-" },

    toggleNotifications()  { this.showNotifications = !this.showNotifications },
    hideNotifications()    { this.showNotifications = false },
    saveDestination()      { this.savedDestination = this.userProfile.destination },
    taskReminder()         {},
    checkReminders()       {},
    checkAttendanceReminder() {}
  }
}
</script>

<style scoped>
* { font-family: 'Poppins', sans-serif; }
.dashboard { display:flex; height:100vh; background:#f0f2f5; }

/* ===== SIDEBAR ===== */
.sidebar { width:220px; background:#1a1a2e; color:#fff; padding:20px; transition:.3s; flex-shrink:0; overflow-y:auto; }
.sidebar-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; }
.hamburger-btn { display:none; font-size:1.5rem; background:none; border:none; color:black; cursor:pointer; position:fixed; top:10px; left:10px; z-index:20; }
.sidebar-btn { display:flex; align-items:center; gap:10px; padding:12px; border:none; border-radius:10px; background:none; color:#fff; cursor:pointer; margin-bottom:8px; transition:.3s; width:100%; text-align:left; }
.sidebar-btn.active { background:#159aff; }
.logout-btn { margin-top:20px; background:#ff4d6d; }
.chat-badge { display:flex; align-items:center; justify-content:center; background:red; color:#fff; font-size:0.7rem; padding:1px 6px; border-radius:50%; margin-left:4px; }

/* ===== MAIN ===== */
.main-content { flex:1; padding:30px; overflow:auto; }
.top-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; position:relative; }
.header-right { display:flex; align-items:center; gap:8px; position:relative; flex-wrap:wrap; }
.avatar-circle { width:40px; height:40px; border-radius:50%; background:#ddd; display:flex; align-items:center; justify-content:center; margin-right:8px; }
.header-user-info { display:flex; flex-direction:column; line-height:1.2; margin-right:8px; }
.user-name { font-weight:600; }
.user-email { font-size:.85rem; color:#888; }

/* ===== TRACKING INDICATOR ===== */
.tracking-indicator { display:flex; align-items:center; gap:5px; font-size:12px; padding:4px 10px; border-radius:20px; background:#e8f5e9; color:#2e7d32; }
.tracking-indicator.idle    { background:#fff3e0; color:#e65100; }
.tracking-indicator.stopped { background:#f5f5f5; color:#999; }
.tracking-dot { width:8px; height:8px; border-radius:50%; background:#4caf50; animation:pulse 1.5s infinite; }
.tracking-indicator.idle    .tracking-dot { background:#ff9800; animation:none; }
.tracking-indicator.stopped .tracking-dot { background:#bbb; animation:none; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.8)} }

/* ===== START / STOP BUTTON ===== */
.track-toggle-btn {
  display:flex; align-items:center; gap:5px;
  padding:6px 12px; border:none; border-radius:20px;
  font-size:12px; font-weight:600; cursor:pointer; transition:all .2s;
}
.btn-start-track { background:linear-gradient(135deg,#27ae60,#2ecc71); color:#fff; }
.btn-stop-track  { background:linear-gradient(135deg,#e74c3c,#c0392b); color:#fff; }
.track-toggle-btn:hover { opacity:.88; transform:translateY(-1px); }

/* ===== NOTIFICATIONS ===== */
.notification-bell { position:relative; cursor:pointer; font-size:1.5rem; margin-left:8px; }
.notif-count { position:absolute; top:-5px; right:-5px; background:red; color:white; font-size:.7rem; padding:2px 6px; border-radius:50%; }
.blink { animation:blink 1s infinite; }
@keyframes blink { 0%,50%,100%{opacity:1} 25%,75%{opacity:0} }
.notification-panel { position:absolute; right:0; top:40px; background:#fff; color:#000; border-radius:10px; width:250px; max-height:300px; overflow-y:auto; box-shadow:0 4px 8px rgba(0,0,0,0.15); z-index:10; }
.notification-item { padding:10px; border-bottom:1px solid #eee; font-size:0.9rem; }
.empty-notif { text-align:center; color:#888; padding:12px; font-size:0.85rem; }

/* ===== CARDS ===== */
.dashboard-cards { display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; }
.gradient { background:linear-gradient(135deg,#159aff,#00a6ff); color:#fff; border-radius:12px; padding:20px; margin-right:12px; flex:1; min-width:150px; text-align:center; }
.card-title { font-size:0.85rem; margin-bottom:6px; }
.card-value { font-size:1.4rem; font-weight:700; }

/* ===== PANELS ===== */
.main-panels { display:flex; flex-direction:column; gap:20px; }
.panel { background:#fff; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08); }
.panel-title { font-size:1.2rem; margin-bottom:12px; }
.gradient-text { background:linear-gradient(135deg,#159aff,#00a6ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:700; }

/* ===== ATTENDANCE ===== */
.attendance-card { display:flex; gap:12px; flex-wrap:wrap; }
.attendance-field { display:flex; flex-direction:column; gap:6px; flex:1; }
.btn-gradient { background:linear-gradient(135deg,#159aff,#00a6ff); color:#fff; border:none; padding:8px 12px; border-radius:8px; cursor:pointer; transition:.3s; }
.btn-gradient:hover { opacity:0.9; }
.btn-gradient:disabled { opacity:.4; cursor:not-allowed; }
.break-controls { margin-top:12px; display:flex; gap:10px; }
.pause-btn  { background:linear-gradient(135deg,#ff9f43,#ff6b6b); }
.resume-btn { background:linear-gradient(135deg,#28c76f,#00b894); }
.status-container { margin-top:10px; }
.status { padding:6px 12px; border-radius:10px; font-size:0.85rem; display:inline-block; }
.status.working { background:#d1f2eb; color:#027a5f; }
.status.done    { background:#d4edda; color:#155724; }

/* ===== TASKS ===== */
.task-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:12px; }
.task-card { background:#f9f9f9; padding:12px; border-radius:10px; box-shadow:0 1px 4px rgba(0,0,0,0.08); display:flex; flex-direction:column; gap:6px; }
.task-header { display:flex; justify-content:space-between; align-items:center; }
.task-title { font-size:1rem; }
.badge { padding:2px 6px; border-radius:8px; font-size:0.75rem; text-transform:capitalize; }
.badge.pending    { background:#ffeeba; color:#856404; }
.badge.in_progress { background:#cce5ff; color:#004085; }
.badge.complete   { background:#d4edda; color:#155724; }
.status-select { padding:6px; border-radius:8px; border:1px solid #ccc; margin-top:6px; }
.comment-box { margin-top:10px; }

/* ===== ACTIVITY TAB ===== */
.tracking-control-banner {
  display:flex; align-items:center; justify-content:space-between;
  padding:12px 16px; border-radius:10px; margin-bottom:16px; gap:10px; flex-wrap:wrap;
}
.banner-active  { background:#e8f5e9; border-left:4px solid #27ae60; }
.banner-idle    { background:#fff3e0; border-left:4px solid #ff9800; }
.banner-stopped { background:#f5f5f5; border-left:4px solid #bbb; }
.banner-left  { display:flex; align-items:center; gap:8px; flex:1; }
.banner-right { display:flex; align-items:center; }
.banner-dot {
  width:10px; height:10px; border-radius:50%; flex-shrink:0;
  background:#4caf50;
}
.banner-idle    .banner-dot { background:#ff9800; }
.banner-stopped .banner-dot { background:#bbb; }
.banner-text { font-size:13px; color:#555; }

.activity-date-row { display:flex; align-items:center; gap:10px; margin-bottom:20px; flex-wrap:wrap; }
.activity-date-row label { font-weight:500; font-size:14px; }
.activity-date-row input { padding:6px 10px; border-radius:8px; border:1px solid #ccc; }
.save-btn { background:linear-gradient(135deg,#27ae60,#2ecc71) !important; }
.save-status { font-size:12px; color:#27ae60; font-weight:500; }
.act-loading { color:#888; font-size:14px; padding:16px 0; }
.act-empty   { color:#aaa; font-size:13px; padding:10px 0; }

.act-live-note { display:flex; align-items:center; gap:6px; font-size:12px; color:#27ae60; margin-bottom:14px; }
.act-live-dot  { width:8px; height:8px; border-radius:50%; background:#27ae60; animation:pulse 1.5s infinite; }

.act-banner-row { display:grid; grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:12px; margin-bottom:24px; }
.act-banner-card { border-radius:12px; padding:16px 18px; }
.active-card { background:#e8f5e9; }
.idle-card   { background:#fff3e0; }
.total-card  { background:#e3f2fd; }
.pct-card    { background:#f3e5f5; }
.act-banner-label { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.05em; color:#555; margin-bottom:6px; }
.act-banner-value { font-size:28px; font-weight:700; color:#1a1a2e; line-height:1; }
.act-pct-bar-wrap { margin-top:8px; height:4px; background:rgba(0,0,0,0.1); border-radius:2px; overflow:hidden; }
.act-pct-bar { height:100%; background:#9c27b0; border-radius:2px; transition:width .5s; }

.act-section-label { font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.05em; color:#999; margin-bottom:12px; }
.act-timeline-section { margin-bottom:24px; }
.act-period-list { display:flex; flex-direction:column; gap:6px; }
.act-period-row  { display:grid; grid-template-columns:80px 1fr 80px; align-items:center; gap:12px; padding:10px 14px; border-radius:8px; }
.act-period-row.active { background:#f0fdf4; border-left:3px solid #27ae60; }
.act-period-row.idle   { background:#fffbf0; border-left:3px solid #e67e22; }
.act-period-badge { font-size:11px; font-weight:700; text-transform:uppercase; padding:3px 8px; border-radius:20px; text-align:center; }
.act-period-badge.active { background:#d4edda; color:#155724; }
.act-period-badge.idle   { background:#ffeeba; color:#856404; }
.act-period-range { font-size:13px; color:#444; font-variant-numeric:tabular-nums; }
.act-period-dur   { font-size:13px; font-weight:600; color:#333; text-align:right; }

.act-history-section { }
.history-table { width:100%; border-collapse:collapse; font-size:13px; }
.history-table th { padding:8px 10px; text-align:left; border-bottom:2px solid #e0e0e0; font-weight:600; color:#666; }
.history-table td { padding:8px 10px; border-bottom:1px solid #f0f0f0; }
.history-table tr:hover td { background:#fafafa; }
.hist-pct-wrap { display:flex; align-items:center; gap:6px; }
.hist-pct-bar  { height:5px; background:#159aff; border-radius:3px; min-width:3px; }
.hist-pct-wrap span { font-size:12px; }

/* ===== CALENDAR ===== */
.calendar-controls { margin-bottom:16px; display:flex; align-items:center; gap:12px; }
.calendar-controls label { font-weight:500; }
.calendar-controls input[type="date"] { padding:6px 10px; border-radius:8px; border:1px solid #ccc; }
.calendar-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; margin-bottom:16px; }
.calendar-day { background:#f9f9f9; border-radius:8px; min-height:70px; display:flex; flex-direction:column; padding:4px; font-size:.85rem; }
.calendar-day.header { font-weight:600; text-align:center; background:#159aff; color:#fff; min-height:auto; padding:6px; }
.calendar-day.blank  { background:transparent; border:none; }
.day-number { font-weight:600; margin-bottom:4px; }
.calendar-day.today    { border:2px solid #159aff; }
.calendar-day.selected { background:#d4edda; }
.events { display:flex; flex-direction:column; gap:2px; }
.event { font-size:.75rem; padding:2px 4px; border-radius:4px; color:#fff; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.event.pending     { background:#ffeeba; color:#856404; }
.event.in_progress { background:#cce5ff; color:#004085; }
.event.complete    { background:#d4edda; color:#155724; }
.task-list { margin-top:12px; list-style:none; padding:0; }
.task-list li { background:#f9f9f9; padding:12px; border-radius:8px; margin-bottom:8px; box-shadow:0 1px 4px rgba(0,0,0,0.08); }
.task-list h3 { margin:0 0 4px; font-size:1rem; }
.task-list span { font-size:.75rem; font-weight:500; text-transform:capitalize; }

/* ===== PROFILE ===== */
.profile-form { display:flex; flex-direction:column; gap:12px; max-width:400px; }
.form-field { display:flex; flex-direction:column; gap:4px; }
input[type=text], input[type=email], input[type=password], input[type=time] {
  padding:8px; border-radius:8px; border:1px solid #ccc;
}
.chat-container::-webkit-scrollbar { width:6px; }
.chat-container::-webkit-scrollbar-thumb { background:#888; border-radius:3px; }

/* ===== OVERLAY ===== */
.overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.4); z-index:9; }

@media (max-width:768px) {
  .sidebar { position:fixed; left:-240px; top:0; height:100%; z-index:10; }
  .sidebar.sidebar-open { left:0; }
  .hamburger-btn { display:block; }
}
</style>
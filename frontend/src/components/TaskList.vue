<template>
  <div :class="['dashboard-layout', darkMode ? 'dark' : 'light']">

    <!-- ===== SIDEBAR ===== -->
    <aside :class="['sidebar', sidebarCollapsed ? 'collapsed' : '', sidebarMobileOpen ? 'show' : '']">
      <div class="user-info">
        <img src="@/assets/s.png" alt="company logo" class="avatar">
        <span class="username" v-if="!sidebarCollapsed">{{ currentUser }}</span>
        <span class="user-role" v-if="!sidebarCollapsed">Team Lead</span>
      </div>

      <div class="nav-group" v-if="!sidebarCollapsed">
        <span class="nav-group-label">Workspace</span>
      </div>

      <button class="nav-btn" :class="{ active: activeSection === 'tasks' }" @click="activeSection='tasks'">
        <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m-6-8h6M5 6h14M5 18h14"/></svg>
        <span v-if="!sidebarCollapsed">Task List</span>
      </button>

      <button class="nav-btn" :class="{ active: activeSection === 'attendance' }" @click="activeSection='attendance'">
        <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
        <span v-if="!sidebarCollapsed">Attendance</span>
      </button>

      <button class="nav-btn" :class="{ active: activeSection === 'activity' }" @click="activeSection='activity'; loadActivitySection()">
        <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12h4l3-9 4 18 3-9h4"/></svg>
        <span v-if="!sidebarCollapsed">Activity Tracking</span>
      </button>

      <button class="nav-btn" :class="{ active: activeSection === 'users' }" @click="activeSection='users'">
        <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87M12 12a4 4 0 100-8 4 4 0 000 8z"/></svg>
        <span v-if="!sidebarCollapsed">Users</span>
      </button>

      <button class="nav-btn" :class="{ active: activeSection === 'groupChat' }" @click="activeSection='groupChat'">
        <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8-1.64 0-3.173-.4-4.5-1.1L3 21l1.1-4.5C3.4 15.173 3 13.64 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
        <span v-if="!sidebarCollapsed">Group Chat</span>
      </button>

      <div class="sidebar-divider" v-if="!sidebarCollapsed"></div>

      <button class="nav-btn create-btn" @click="goToCreateTask">
        <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        <span v-if="!sidebarCollapsed">New Task</span>
      </button>

      <div class="theme-toggle" v-if="!sidebarCollapsed">
        <label class="theme-label">
          <input type="checkbox" v-model="darkMode"/>
          <span class="theme-track"><span class="theme-thumb"></span></span>
          {{ darkMode ? 'Dark' : 'Light' }}
        </label>
      </div>

      <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" :d="sidebarCollapsed ? 'M9 5l7 7-7 7' : 'M15 19l-7-7 7-7'"/>
        </svg>
      </button>
    </aside>

    <button class="mobile-toggle" @click="sidebarMobileOpen = !sidebarMobileOpen">
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
    </button>

    <main class="content">
      <!-- Greeting + Search -->
      <div class="header-search" v-if="activeSection !== 'groupChat' && activeSection !== 'activity'">
        <div class="greeting-block">
          <h2 class="greeting">Hello, <span class="greeting-name">{{ currentUser }}</span></h2>
          <span class="greeting-sub">{{ new Date().toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric' }) }}</span>
        </div>
        <div class="search-wrap">
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <input type="text" v-model="headerSearch" placeholder="Search tasks, users…"/>
        </div>
      </div>

      <!-- ===== TASKS ===== -->
      <section v-if="activeSection === 'tasks'">
        <div class="tasks-layout">

          <!-- LEFT: TASK LIST -->
          <div class="tasks-list-col">
            <div class="tasks-col-header">
              <h2 class="section-heading" style="border:none;padding-bottom:0;margin-bottom:0;">
                Tasks
                <span class="tasks-count-badge">{{ filteredTasks.length }}</span>
              </h2>
              <button v-if="taskCalendarFilterDate" class="chip-clear" @click="taskCalendarFilterDate = null">
                {{ formatChipDate(taskCalendarFilterDate) }}
                <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>

            <ul v-if="filteredTasks.length" class="task-list task-list-compact">
              <li v-for="task in filteredTasks" :key="task.id" class="task-card task-card-compact" :id="'task-' + task.id">
                <div class="task-header task-header-compact">
                  <strong class="task-title">{{ task.title }}</strong>
                  <span class="status" :class="task.status">{{ task.status.replace('_',' ') }}</span>
                </div>
                <p class="desc desc-compact">{{ task.description }}</p>
                <div class="task-meta-row">
                  <span class="meta-pill"><svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>{{ task.start_date || '—' }} → {{ task.end_date || '—' }}</span>
                </div>

                <div v-if="task.comments && task.comments.length" class="task-comments task-comments-compact">
                  <span class="comments-toggle" @click="toggleTaskComments(task.id)">
                    {{ task.comments.length }} comment{{ task.comments.length > 1 ? 's' : '' }}
                    <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" fill="none" viewBox="0 0 24 24" stroke="currentColor" :class="{ rotated: expandedComments === task.id }"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                  </span>
                  <ul v-if="expandedComments === task.id" class="comments-list">
                    <li v-for="c in task.comments" :key="c.id"><em>{{ c.author_username }}:</em> {{ c.content }}</li>
                  </ul>
                </div>

                <div class="assigned-row">
                  <div v-if="task.assigned_to && task.assigned_to.length" class="assigned-pills">
                    <span v-for="u in task.assigned_to" :key="u.id" class="assigned-pill">{{ u.username }}</span>
                  </div>
                  <em v-else class="unassigned-note">Unassigned</em>
                </div>

                <div class="task-card-footer">
                  <div class="assign-section assign-section-compact">
                    <select v-model="selectedUser[task.id]">
                      <option disabled value="">Assign…</option>
                      <option v-for="member in teamMembers" :key="member.id" :value="member.id">{{ member.username }}</option>
                    </select>
                    <button class="btn-primary btn-xs" @click="assignUser(task.id)">Assign</button>
                  </div>
                  <button class="btn-danger btn-xs" @click="showModal(task.id)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M9 7V4a1 1 0 011-1h4a1 1 0 011 1v3M4 7h16"/></svg>
                  </button>
                </div>
              </li>
            </ul>
            <div class="empty-state" v-else>
              <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="opacity:.3"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m-6-8h6M5 6h14M5 18h14"/></svg>
              <p>{{ taskCalendarFilterDate ? 'No tasks starting on this date.' : 'No tasks created yet.' }}</p>
            </div>
          </div>

          <!-- RIGHT: MINI CALENDAR -->
          <aside class="tasks-calendar-col">
            <div class="mini-cal-card">
              <div class="mini-cal-header">
                <span class="panel-title">{{ monthNames[calendarMonth-1] }} {{ calendarYear }}</span>
                <div class="mini-cal-nav">
                  <button class="mini-cal-nav-btn" @click="shiftTaskCalendar(-1)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
                  </button>
                  <button class="mini-cal-nav-btn" @click="shiftTaskCalendar(1)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>
                  </button>
                </div>
              </div>
              <div class="mini-cal-grid">
                <div class="mini-cal-day mini-cal-dow" v-for="d in weekDays" :key="d">{{ d.charAt(0) }}</div>
                <div v-for="blank in startDay" :key="'mb'+blank" class="mini-cal-day mini-cal-blank"></div>
                <div
                  v-for="day in daysInMonth"
                  :key="day"
                  class="mini-cal-day"
                  :class="{
                    'has-tasks': tasksForDay(day).length,
                    'is-selected': isTaskCalendarDaySelected(day),
                    'is-today': isTaskCalendarDayToday(day)
                  }"
                  @click="selectTaskCalendarDay(day)"
                >
                  <span class="mini-cal-daynum">{{ day }}</span>
                  <span v-if="tasksForDay(day).length" class="mini-cal-dot-row">
                    <span v-for="n in Math.min(tasksForDay(day).length, 3)" :key="n" class="mini-cal-dot"
                      :style="{ background: tasksForDay(day)[n-1].status === 'complete' ? '#22c55e' : (tasksForDay(day)[n-1].status === 'in_progress' ? '#159aff' : '#eab308') }"></span>
                  </span>
                </div>
              </div>
              <div class="mini-cal-legend">
                <span><i class="dot-pending"></i>Pending</span>
                <span><i class="dot-progress"></i>In progress</span>
                <span><i class="dot-complete"></i>Complete</span>
              </div>
            </div>

            <div class="mini-cal-card" v-if="taskCalendarFilterDate">
              <div class="mini-cal-header">
                <span class="panel-title">{{ formatChipDate(taskCalendarFilterDate) }}</span>
                <span class="tasks-count-badge">{{ filteredTasks.length }}</span>
              </div>
              <div class="day-task-mini-list">
                <a v-for="task in filteredTasks" :key="'mini-'+task.id" class="day-task-mini-item" :href="'#task-' + task.id">
                  <span class="dtm-dot" :class="task.status"></span>
                  <span class="dtm-title">{{ task.title }}</span>
                </a>
                <div v-if="!filteredTasks.length" class="act-empty" style="padding:4px 0;">No tasks.</div>
              </div>
            </div>
          </aside>

        </div>
      </section>

      <!-- ===== ATTENDANCE ===== -->
      <section v-if="activeSection === 'attendance'">
        <div class="section-topbar">
          <h2 class="section-heading">Attendance — {{ selectedDate }}</h2>
          <div class="section-actions">
            <input type="date" v-model="selectedDate" class="date-input"/>
            <button class="btn-outline-accent" @click="downloadCSV">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              Export CSV
            </button>
          </div>
        </div>
        <div class="attendance-card">
          <table class="attendance-table" v-if="filteredAttendance.length">
            <thead>
              <tr>
                <th>Date</th><th>User</th><th>Role</th>
                <th>System In</th><th>System Out</th>
                <th>Manual In</th><th>Manual Out</th>
                <th>Breaks</th><th>Break hrs</th><th>Net worked</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in filteredAttendance" :key="a.date + a.user">
                <td>{{ a.date.split('T')[0] }}</td>
                <td><span class="user-chip">{{ a.user }}</span></td>
                <td><span class="role-tag">{{ a.role }}</span></td>
                <td>{{ a.system_check_in || '—' }}</td>
                <td>{{ a.system_check_out || '—' }}</td>
                <td>{{ a.manual_check_in || '—' }}</td>
                <td>{{ a.manual_check_out || '—' }}</td>
                <td>
                  <div v-if="a.breaks && a.breaks.length">
                    <div v-for="(b,i) in a.breaks" :key="i" class="break-entry">{{ b.start }} – {{ b.end || 'ongoing' }}</div>
                  </div>
                  <span v-else style="color:var(--text-muted)">—</span>
                </td>
                <td><span class="time-chip">{{ calculateBreakHours(a.breaks) }}</span></td>
                <td><span class="time-chip time-chip-accent">{{ calculateWorkedAfterBreak(a) }}</span></td>
              </tr>
            </tbody>
          </table>
          <div class="empty-state" v-else>
            <p>No attendance for {{ selectedDate }}.</p>
          </div>
        </div>
      </section>

      <!-- ===== USERS ===== -->
      <section v-if="activeSection === 'users'">
        <h2 class="section-heading">User Overview</h2>
        <div class="user-search-wrap">
          <div class="search-wrap" style="max-width:260px">
            <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            <input type="text" v-model="userSearch" placeholder="Find user…"/>
          </div>
          <select v-model="selectedMember" class="user-select">
            <option value="">Select a user</option>
            <option v-for="member in filteredUsers" :key="member.id" :value="member.username">{{ member.username }}</option>
          </select>
        </div>
        <div v-if="selectedMember">
          <h3 class="sub-heading">Tasks</h3>
          <div class="user-task-cards" v-if="userTasks.length">
            <div v-for="task in userTasks" :key="task.id" class="task-card">
              <div class="task-header">
                <strong class="task-title">{{ task.title }}</strong>
                <span class="status" :class="task.status">{{ task.status.replace('_',' ') }}</span>
              </div>
              <div class="task-desc-card">
                <p class="desc">{{ task.description }}</p>
                <p class="task-meta"><strong>Start:</strong> {{ task.start_date || '—' }} &nbsp;·&nbsp; <strong>End:</strong> {{ task.end_date || '—' }}</p>
              </div>
            </div>
          </div>
          <p v-else class="act-empty">No tasks assigned.</p>
          <h3 class="sub-heading">Attendance</h3>
          <div class="attendance-card">
            <table class="attendance-table">
              <thead>
                <tr>
                  <th>Date</th><th>System In</th><th>System Out</th>
                  <th>Manual In</th><th>Manual Out</th>
                  <th>Breaks</th><th>Break hrs</th><th>Net worked</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in userAttendance" :key="a.date">
                  <td>{{ a.date.split('T')[0] }}</td>
                  <td>{{ a.system_check_in || '—' }}</td>
                  <td>{{ a.system_check_out || '—' }}</td>
                  <td>{{ a.manual_check_in || '—' }}</td>
                  <td>{{ a.manual_check_out || '—' }}</td>
                  <td>
                    <div v-if="a.breaks && a.breaks.length">
                      <div v-for="(b,i) in a.breaks" :key="i">{{ b.start }} – {{ b.end || 'ongoing' }}</div>
                    </div>
                    <span v-else style="color:var(--text-muted)">—</span>
                  </td>
                  <td>{{ calculateBreakHours(a.breaks) }}</td>
                  <td>{{ calculateWorkedAfterBreak(a) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ===== GROUP CHAT ===== -->
      <section v-if="activeSection === 'groupChat'">
        <div class="chat-page-header">
          <h2 class="section-heading" style="margin-bottom:0;border:none;padding-bottom:0;">Group Chat</h2>
          <button class="btn-danger btn-sm" @click="clearChat">Clear</button>
        </div>
        <div class="chat-container">
          <div class="chat-messages" ref="chatMessages">
            <div v-for="(msg,i) in chatMessages" :key="i" :class="['chat-msg', msg.sender_username === currentUser ? 'self' : 'other']">
              <span class="chat-sender">{{ msg.sender_username }}</span>
              <span class="chat-bubble">{{ msg.message }}</span>
              <span class="chat-time">{{ formatDateTime(msg.created_at) }}</span>
            </div>
          </div>
          <div class="chat-input-wrap">
            <input type="text" v-model="newMessage" placeholder="Type a message…" @keyup.enter="sendMessage"/>
            <button class="btn-primary" @click="sendMessage">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
            </button>
          </div>
        </div>
      </section>


      <!-- ===== ACTIVITY TRACKING ===== -->
      <section v-if="activeSection === 'activity'" class="activity-section">
        <div class="act-page-header">
          <div class="act-header-left">
            <h2 class="page-title">Activity Tracking</h2>
            <div class="act-context-bar">
              <span class="ctx-chip">
                <svg class="ctx-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                <strong>{{ activityMemberId ? (teamMembers.find(m => m.id == activityMemberId) || {}).username || '—' : 'All Members' }}</strong>
              </span>
              <span class="ctx-sep">·</span>
              <span class="ctx-chip">
                <svg class="ctx-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                <strong>{{ activityDate }}</strong>
              </span>
              <template v-if="activityMemberId && memberDetail">
                <span class="ctx-sep">·</span>
                <span class="ctx-chip ctx-time">
                  <svg class="ctx-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  <span class="ctx-from">{{ _getTimelineStart() }}</span>
                  <span class="ctx-arrow">→</span>
                  <span class="ctx-to">{{ activityDate === todayDate ? currentTimeStr : _getTimelineEnd() }}</span>
                </span>
              </template>
            </div>
          </div>
          <div class="act-filters">
            <input type="date" v-model="activityDate" @change="loadActivitySection"/>
            <select v-model="activityMemberId" @change="loadMemberDetail">
              <option value=""> All members </option>
              <option v-for="m in teamMembers" :key="m.id" :value="m.id">{{ m.username }}</option>
            </select>
            <button class="btn-ghost" @click="loadActivitySection">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              Refresh
            </button>
            <button class="btn-accent" @click="downloadWeeklyReport">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              Weekly PDF
            </button>
          </div>
        </div>

        <!-- LIVE STATUS BADGES -->
        <div class="live-status-row" v-if="activityDate === todayDate && !activityMemberId">
          <h3 class="section-label">Live Status</h3>
          <div class="live-badges">
            <div
              v-for="row in teamActivity"
              :key="row.user_id"
              class="live-badge"
              :class="row.is_tracking ? (row.is_idle ? 'lb-idle' : 'lb-active') : 'lb-stopped'"
              @click="selectMember(row.user_id)"
            >
              <span class="live-dot"></span>
              <span class="live-name">{{ row.username }}</span>
              <span class="live-state">{{ row.is_tracking ? (row.is_idle ? 'Idle' : 'Active') : 'Offline' }}</span>
            </div>
          </div>
        </div>

        <!-- TEAM OVERVIEW -->
        <div v-if="!activityMemberId">
          <!-- TOP APPS DONUT -->
          <div v-if="topApps.length" class="panel-card">
            <div class="panel-header">
              <div>
                <span class="panel-title">Top Apps Today</span>
                <span class="panel-sub">Whole team · {{ activityDate }}</span>
              </div>
            </div>
            <div class="top-apps-donut-layout">
              <div class="donut-center-wrap">
                <svg class="donut-svg" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="110" cy="110" r="80" fill="none" stroke="rgba(0,0,0,0.05)" stroke-width="28"/>
                  <circle
                    v-for="(app, i) in topApps.slice(0,6)"
                    :key="app.app_name + '_seg'"
                    cx="110" cy="110" r="80"
                    fill="none"
                    :stroke="donutShade(i)"
                    stroke-width="28"
                    stroke-linecap="butt"
                    :stroke-dasharray="_donutDash(app.total_seconds, i)"
                    :stroke-dashoffset="_donutOffset(i)"
                    style="transition:all 0.7s ease;"
                  />
                  <circle cx="110" cy="110" r="66" fill="var(--card)"/>
                  <text x="110" y="104" text-anchor="middle" font-size="28" font-weight="700" fill="var(--text)" font-family="Poppins,sans-serif">{{ topApps.length }}</text>
                  <text x="110" y="122" text-anchor="middle" font-size="10" fill="var(--text-muted)" font-family="Poppins,sans-serif" letter-spacing="0.08em">APPS USED</text>
                </svg>
              </div>
              <div class="donut-legend">
                <div v-for="(app, i) in topApps.slice(0, 8)" :key="app.app_name" class="donut-legend-row">
                  <span class="donut-legend-dot" :style="{ background: donutShade(i) }"></span>
                  <span class="donut-legend-name">{{ app.app_name }}</span>
                  <span class="donut-legend-time">{{ app.time_formatted }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- TEAM MEMBERS GRID -->
          <div v-if="teamActivity.length" class="panel-card">
            <div class="panel-header">
              <div>
                <span class="panel-title">Member Breakdown</span>
                <span class="panel-sub">{{ activityDate }}</span>
              </div>
            </div>
            <div class="act-loading" v-if="activityLoading">Loading…</div>
            <div v-else class="member-card-grid">
              <div v-for="row in teamActivity" :key="row.user_id" class="member-card" @click="selectMember(row.user_id)">
                <div class="mc-header">
                  <div class="mc-avatar">{{ row.username.charAt(0).toUpperCase() }}</div>
                  <div class="mc-name-block">
                    <span class="mc-name">{{ row.username }}</span>
                    <span class="track-status-badge" :class="row.is_tracking ? (row.is_idle ? 'lb-idle' : 'lb-active') : 'lb-stopped'">
                      <span class="live-dot" style="width:5px;height:5px;"></span>
                      {{ row.is_tracking ? (row.is_idle ? 'Idle' : 'Active') : 'Offline' }}
                    </span>
                  </div>
                  <button class="mc-view-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                  </button>
                </div>
                <div class="mc-stats">
                  <div class="mc-stat">
                    <span class="mc-stat-label">Active</span>
                    <span class="mc-stat-value mc-active-val">{{ row.active_time_formatted }}</span>
                  </div>
                  <div class="mc-stat">
                    <span class="mc-stat-label">Idle</span>
                    <span class="mc-stat-value mc-idle-val">{{ fmtSeconds(row.total_idle_seconds) }}</span>
                  </div>
                  <div class="mc-stat">
                    <span class="mc-stat-label">Top App</span>
                    <span class="mc-stat-value" style="font-size:11px;">{{ row.top_app || '—' }}</span>
                  </div>
                </div>
                <div class="mc-pct-row">
                  <div class="mc-pct-track">
                    <div class="mc-pct-fill" :style="{ width: row.active_percentage + '%' }"></div>
                  </div>
                  <span class="mc-pct-label">{{ row.active_percentage }}%</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="!activityLoading" class="empty-state">No activity data for {{ activityDate }}.</div>
        </div>

        <!-- SINGLE MEMBER DETAIL -->
        <div v-else>
          <div class="member-detail-topbar">
            <button class="btn-back" @click="activityMemberId = ''; loadActivitySection()">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
              Back to team
            </button>
            <button class="btn-accent btn-sm" @click="downloadMemberReport(activityMemberId)">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              Download Report
            </button>
          </div>

          <div v-if="memberDetail" class="member-detail-wrap">
            <h3 class="member-detail-title">{{ memberDetail.username }} <span>/ {{ activityDate }}</span></h3>

            <!-- 3-Tab switcher -->
            <div class="act-type-tabs">
              <button class="act-type-tab" :class="{ active: activityTab === 'desktop' }" @click="activityTab = 'desktop'">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                Desktop
              </button>
              <button class="act-type-tab" :class="{ active: activityTab === 'browser' }" @click="activityTab = 'browser'; fetchBrowserActivity()">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/></svg>
                Browser
              </button>
              <button class="act-type-tab" :class="{ active: activityTab === 'screenshots' }" @click="activityTab = 'screenshots'; fetchScreenshots()">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                Screenshots
                <span v-if="screenshotData && screenshotData.count > 0" class="ss-tab-badge">{{ screenshotData.count }}</span>
              </button>
            </div>

            <!-- BROWSER PANEL -->
            <div v-if="activityTab === 'browser'">
              <div v-if="browserLoading" class="act-loading">Loading browser activity…</div>
              <div v-else-if="browserActivity">
                <div class="stat-cards-row" style="margin-bottom:20px;">
                  <div class="stat-card">
                    <div class="sc-icon sc-blue">
                      <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    </div>
                    <div>
                      <p class="sc-label">Total Browsing</p>
                      <p class="sc-value">{{ browserActivity.total_browser || '0m' }}</p>
                    </div>
                  </div>
                  <div class="stat-card">
                    <div class="sc-icon sc-slate">
                      <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/></svg>
                    </div>
                    <div>
                      <p class="sc-label">Sites Visited</p>
                      <p class="sc-value">{{ browserActivity.domain_breakdown ? browserActivity.domain_breakdown.length : 0 }}</p>
                    </div>
                  </div>
                </div>
                <div v-if="browserActivity.domain_breakdown && browserActivity.domain_breakdown.length">
                  <h4 class="section-label" style="margin-bottom:8px;">Time per Website</h4>
                  <p class="domain-hint">Click a site to view visited pages</p>
                  <div class="domain-grid">
                    <template v-for="site in browserActivity.domain_breakdown" :key="site.domain">
                      <div class="domain-card" :class="{ 'is-expanded': expandedDomain === site.domain }" @click="toggleDomain(site.domain)">
                        <div class="domain-card-header">
                          <div class="domain-favicon-wrap">
                            <img :src="`https://www.google.com/s2/favicons?sz=32&domain=${site.domain}`" width="18" height="18" class="domain-favicon" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'"/>
                            <div class="domain-favicon-fallback" style="display:none;">{{ site.domain.charAt(0).toUpperCase() }}</div>
                          </div>
                          <div class="domain-name-block">
                            <span class="domain-name">{{ site.domain }}</span>
                            <span class="domain-visits-count">{{ domainVisitCount(site.domain) }} visits</span>
                          </div>
                          <div class="domain-time-pill">{{ site.duration }}</div>
                          <svg class="domain-expand-chevron" :class="{ rotated: expandedDomain === site.domain }" xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                        </div>
                        <div v-if="expandedDomain === site.domain" class="domain-url-list" @click.stop>
                          <div v-if="domainVisits(site.domain).length" class="domain-url-table">
                            <div class="domain-url-row domain-url-header">
                              <span>Path</span><span>Title</span><span>Time</span>
                            </div>
                            <a v-for="v in domainVisits(site.domain)" :key="v.id" :href="v.url || '#'" target="_blank" rel="noopener" class="domain-url-row" :title="v.title || v.url">
                              <span class="domain-url-path">{{ v.sub_path || '/' }}</span>
                              <span class="domain-url-title">{{ v.title || '—' }}</span>
                              <span class="domain-url-time">{{ v.time_formatted }}</span>
                            </a>
                          </div>
                          <div v-else class="domain-url-empty">No page-level data recorded.</div>
                        </div>
                      </div>
                    </template>
                  </div>
                </div>
                <div v-else class="empty-state">No browser visits recorded for this day.</div>
              </div>
              <div v-else class="empty-state">No browser data for {{ activityDate }}.</div>
            </div>

            <!-- SCREENSHOTS PANEL -->
            <div v-if="activityTab === 'screenshots'">
              <div class="ss-status-bar" :class="ssStatusClass">
                <div class="ss-status-icon-wrap">
                  <svg v-if="ssStatusClass === 'ss-status-ok'" xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  <svg v-else-if="ssStatusClass === 'ss-status-warn'" xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                </div>
                <div class="ss-status-text">
                  <strong>{{ ssStatusTitle }}</strong>
                  <span>{{ ssStatusDetail }}</span>
                </div>
                <div class="ss-status-pills" v-if="electronStatus">
                  <span class="ss-pill" :class="electronStatus.electron_active ? 'pill-ok' : 'pill-off'">Electron {{ electronStatus.electron_active ? 'Online' : 'Offline' }}</span>
                  <span class="ss-pill" :class="electronStatus.extension_active ? 'pill-ok' : 'pill-off'">Extension {{ electronStatus.extension_active ? 'Online' : 'Offline' }}</span>
                </div>
              </div>
              <div v-if="screenshotLoading" class="act-loading">Loading screenshots…</div>
              <div v-else-if="screenshotData">
                <div class="ss-meta-strip">
                  <div class="ss-meta-card">
                    <div class="ss-meta-icon-wrap ss-meta-blue"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg></div>
                    <div class="ss-meta-body">
                      <span class="ss-meta-label">Screenshots</span>
                      <span class="ss-meta-value">{{ screenshotData.count }}<span class="ss-meta-total"> / 8</span></span>
                      <div class="ss-meta-prog-track"><div class="ss-meta-prog-fill" :style="{ width: (screenshotData.count / 8 * 100) + '%' }"></div></div>
                    </div>
                  </div>
                  <div class="ss-meta-card">
                    <div class="ss-meta-icon-wrap ss-meta-slate"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg></div>
                    <div class="ss-meta-body"><span class="ss-meta-label">Date</span><span class="ss-meta-value" style="font-size:15px;">{{ screenshotData.date }}</span></div>
                  </div>
                  <div class="ss-meta-card">
                    <div class="ss-meta-icon-wrap ss-meta-navy"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg></div>
                    <div class="ss-meta-body"><span class="ss-meta-label">Member</span><span class="ss-meta-value" style="font-size:15px;">{{ screenshotData.username }}</span></div>
                  </div>
                </div>
                <div v-if="screenshotData.screenshots && screenshotData.screenshots.length">
                  <h4 class="section-label" style="margin-bottom:14px;">Screenshots — click to enlarge</h4>
                  <div class="ss-premium-grid">
                    <div v-for="(ss, idx) in screenshotData.screenshots" :key="ss.id" class="ss-premium-card" @click="openLightbox(ss, idx)">
                      <div class="ss-thumb-wrap">
                        <img :src="ss.image" class="ss-thumb" :alt="`Screenshot ${idx + 1}`" loading="lazy"/>
                        <div class="ss-thumb-overlay"><svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="white" class="ss-expand-icon"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"/></svg></div>
                        <div class="ss-badge-num">#{{ idx + 1 }}</div>
                      </div>
                      <div class="ss-premium-footer">
                        <span class="ss-premium-time">{{ formatSSTime(ss.timestamp) }}</span>
                        <span class="ss-premium-hint">Enlarge</span>
                      </div>
                    </div>
                    <div v-for="n in (8 - screenshotData.count)" :key="'placeholder-' + n" class="ss-premium-card ss-placeholder">
                      <div class="ss-thumb-wrap ss-placeholder-inner">
                        <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="ss-placeholder-icon"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/></svg>
                        <span class="ss-placeholder-label">Pending</span>
                      </div>
                      <div class="ss-premium-footer">
                        <span class="ss-num">#{{ screenshotData.count + n }}</span>
                        <span class="ss-time" style="color:var(--text-muted)">not yet taken</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="ss-empty-state">
                  <svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="opacity:.25;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/></svg>
                  <div class="ss-empty-title">No screenshots yet for {{ activityDate }}</div>
                </div>
              </div>
            </div>

            <!-- DESKTOP PANEL -->
            <div v-if="activityTab === 'desktop'">
              <!-- 7-day sparkline -->
              <div class="panel-card" v-if="memberWeekHistory.length">
                <div class="panel-header"><span class="panel-title">7-Day Overview</span></div>
                <div class="sparkline-row">
                  <div v-for="day in memberWeekHistory" :key="day.date" class="spark-bar-col" :title="`${day.date}: ${day.active_time_formatted} active`">
                    <div class="spark-bar-track">
                      <div class="spark-bar-fill" :style="{ height: sparkHeight(day.total_active_seconds) + '%' }"></div>
                    </div>
                    <span class="spark-label">{{ day.date.slice(5) }}</span>
                  </div>
                </div>
              </div>

              <!-- Active / Idle stat cards -->
              <div class="desktop-stat-grid" v-if="memberDetail.summary">
                <div class="dsg-card dsg-active">
                  <div class="dsg-icon"><svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg></div>
                  <div class="dsg-body">
                    <span class="dsg-label">Total Active</span>
                    <span class="dsg-value">{{ memberDetail.summary.active_time_formatted }}</span>
                  </div>
                </div>
                <div class="dsg-card dsg-idle">
                  <div class="dsg-icon"><svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg></div>
                  <div class="dsg-body">
                    <span class="dsg-label">Total Idle</span>
                    <span class="dsg-value">{{ memberDetail.summary.idle_time_formatted }}</span>
                  </div>
                </div>
                <div class="dsg-card dsg-pct" style="grid-column:1/-1;">
                  <div class="dsg-icon"><svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg></div>
                  <div class="dsg-body" style="flex:1;">
                    <span class="dsg-label">Active %</span>
                    <div class="dsg-pct-row">
                      <span class="dsg-value">{{ memberDetail.summary.active_percentage }}%</span>
                      <div class="dsg-pct-bar-wrap"><div class="dsg-pct-bar" :style="{ width: memberDetail.summary.active_percentage + '%' }"></div></div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">No summary data for this date.</div>

              <!-- App donut + Timeline side by side -->
              <div v-if="(memberDetail.app_breakdown && memberDetail.app_breakdown.length) || memberPeriods.length" class="desktop-bottom-grid">

                <!-- App usage donut -->
                <div v-if="memberDetail.app_breakdown && memberDetail.app_breakdown.length" class="panel-card">
                  <div class="panel-header"><span class="panel-title">App Usage</span></div>
                  <div class="app-donut-layout">
                    <svg class="app-donut-svg" viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="80" cy="80" r="55" fill="none" stroke="rgba(0,0,0,0.05)" stroke-width="20"/>
                      <circle
                        v-for="(app, i) in memberDetail.app_breakdown.slice(0, 6)"
                        :key="app.app + '_aseg'"
                        cx="80" cy="80" r="55"
                        fill="none"
                        :stroke="donutShade(i)"
                        stroke-width="20"
                        stroke-linecap="butt"
                        :stroke-dasharray="_appDonutDash(app.seconds, i)"
                        :stroke-dashoffset="_appDonutOffset(i)"
                        style="transition:all 0.7s ease;"
                      />
                      <circle cx="80" cy="80" r="45" fill="var(--card)"/>
                      <text x="80" y="76" text-anchor="middle" font-size="18" font-weight="700" fill="var(--text)" font-family="Poppins,sans-serif">{{ memberDetail.app_breakdown.length }}</text>
                      <text x="80" y="90" text-anchor="middle" font-size="8" fill="var(--text-muted)" font-family="Poppins,sans-serif">APPS</text>
                    </svg>
                    <div class="app-donut-legend">
                      <div v-for="(app, i) in memberDetail.app_breakdown" :key="app.app" class="donut-legend-row">
                        <span class="donut-legend-dot" :style="{ background: donutShade(i) }"></span>
                        <span class="donut-legend-name">{{ app.app }}</span>
                        <span class="donut-legend-time">{{ app.duration }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- ===== ACTIVE / IDLE TIMELINE — SIDE BY SIDE SEPARATE PANELS ===== -->
                <div v-if="memberPeriods.length" class="timeline-split-wrap">

                  <!-- ACTIVE LANE -->
                  <div class="panel-card timeline-lane-panel timeline-lane-active-panel">
                    <div class="panel-header">
                      <div class="panel-title-row">
                        <span class="tl-lane-dot tl-dot-active"></span>
                        <span class="panel-title">Active Periods</span>
                      </div>
                      <span class="tl-count-badge tl-count-active">{{ memberPeriods.filter(p => p.type === 'active').length }}</span>
                    </div>
                    <div class="tl-gantt-mini">
                      <div class="tl-gantt-track">
                        <div
                          v-for="(p, i) in memberPeriods.filter(p => p.type === 'active')"
                          :key="'active-bar-'+i"
                          class="tl-gantt-bar tl-bar-active"
                          :style="{ left: periodPct(p.from) + '%', width: periodWidthPct(p.from, p.to) + '%' }"
                          :title="`${p.from} → ${p.to} (${_durationFromTimes(p.from, p.to)})`"
                        ></div>
                        <span v-if="nowLinePct !== null" class="tl-now-line" :style="{ left: nowLinePct + '%' }"></span>
                      </div>
                      <div class="tl-ruler">
                        <span v-for="tick in simpleTicks" :key="'at'+tick.h" :style="{ left: tick.pct + '%' }">{{ tick.label }}</span>
                      </div>
                    </div>
                    <div class="tl-entries">
                      <div v-for="(p, i) in memberPeriods.filter(p => p.type === 'active')" :key="'ae-'+i" class="tl-entry tl-entry-active">
                        <div class="tl-entry-times">
                          <span class="tl-t">{{ p.from }}</span>
                          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="tl-arrow-icon"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                          <span class="tl-t">{{ p.to }}</span>
                        </div>
                        <span class="tl-dur">{{ _durationFromTimes(p.from, p.to) }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- IDLE LANE -->
                  <div class="panel-card timeline-lane-panel timeline-lane-idle-panel">
                    <div class="panel-header">
                      <div class="panel-title-row">
                        <span class="tl-lane-dot tl-dot-idle"></span>
                        <span class="panel-title">Idle Periods</span>
                      </div>
                      <span class="tl-count-badge tl-count-idle">{{ memberPeriods.filter(p => p.type === 'idle').length }}</span>
                    </div>
                    <div class="tl-gantt-mini">
                      <div class="tl-gantt-track">
                        <div
                          v-for="(p, i) in memberPeriods.filter(p => p.type === 'idle')"
                          :key="'idle-bar-'+i"
                          class="tl-gantt-bar tl-bar-idle"
                          :style="{ left: periodPct(p.from) + '%', width: periodWidthPct(p.from, p.to) + '%' }"
                          :title="`${p.from} → ${p.to} (${_durationFromTimes(p.from, p.to)})`"
                        ></div>
                        <span v-if="nowLinePct !== null" class="tl-now-line" :style="{ left: nowLinePct + '%' }"></span>
                      </div>
                      <div class="tl-ruler">
                        <span v-for="tick in simpleTicks" :key="'it'+tick.h" :style="{ left: tick.pct + '%' }">{{ tick.label }}</span>
                      </div>
                    </div>
                    <div class="tl-entries">
                      <div v-for="(p, i) in memberPeriods.filter(p => p.type === 'idle')" :key="'ie-'+i" class="tl-entry tl-entry-idle">
                        <div class="tl-entry-times">
                          <span class="tl-t">{{ p.from }}</span>
                          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="tl-arrow-icon"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                          <span class="tl-t">{{ p.to }}</span>
                        </div>
                        <span class="tl-dur">{{ _durationFromTimes(p.from, p.to) }}</span>
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>
          <div v-else-if="activityLoading" class="act-loading">Loading member data…</div>
          <div v-else class="empty-state">No data found for this member on {{ activityDate }}.</div>
        </div>
      </section>

      <!-- DELETE MODAL -->
      <div class="modal-overlay" v-if="showDeleteModal">
        <div class="modal-box">
          <h3>Confirm Delete</h3>
          <p style="font-size:13px;color:var(--text-muted);margin-bottom:4px;">This action cannot be undone.</p>
          <div class="modal-actions">
            <button class="btn-outline" @click="cancelDelete">Cancel</button>
            <button class="btn-danger" @click="confirmDelete">Delete</button>
          </div>
        </div>
      </div>

      <!-- SCREENSHOT LIGHTBOX -->
      <div class="ss-lightbox-overlay" v-if="screenshotLightbox" @click.self="screenshotLightbox = null">
        <div class="ss-lightbox-box">
          <div class="ss-lightbox-header">
            <div class="ss-lightbox-meta">
              <span class="ss-lightbox-title">{{ screenshotLightbox.username }} — #{{ screenshotLightbox.idx + 1 }}</span>
              <span class="ss-lightbox-sub">{{ screenshotLightbox.time }}</span>
            </div>
            <button class="ss-lightbox-close" @click="screenshotLightbox = null">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="ss-lightbox-img-wrap">
            <img :src="screenshotLightbox.image" class="ss-lightbox-img" alt="Screenshot"/>
          </div>
          <button class="ss-nav-btn ss-nav-prev" v-if="screenshotLightbox.idx > 0" @click="navigateLightbox(-1)">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
          </button>
          <button class="ss-nav-btn ss-nav-next" v-if="screenshotData && screenshotLightbox.idx < screenshotData.screenshots.length - 1" @click="navigateLightbox(1)">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>

    </main>
  </div>
</template>

<script>
import axios from "axios"

const API_BASE = import.meta.env.VITE_API_URL

const DONUT_SHADES = [
  "#159aff","#0c6bb8","#5fb6ff","#3c4a5e","#9aa5b1","#1a2a3a","#bcd9f5","#6b7280",
]
function donutShade(i) { return DONUT_SHADES[i % DONUT_SHADES.length] }

export default {
  name: "LeadDashboard",

  data() {
    return {
      currentUser: "",
      sidebarCollapsed: false,
      sidebarMobileOpen: false,
      darkMode: false,
      activeSection: "tasks",
      headerSearch: "",
      userSearch: "",
      selectedMember: "",
      calendarMonth: new Date().getMonth() + 1,
      calendarYear:  new Date().getFullYear(),
      monthNames: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
      weekDays: ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],
      calendarYears: Array.from({ length:10 }, (_,i) => new Date().getFullYear() - 5 + i),
      selectedDate: new Date().toISOString().split("T")[0],
      tasks:       [],
      teamMembers: [],
      attendance:  [],
      chatMessages: [],
      newMessage: "",
      selectedUser: {},
      showDeleteModal: false,
      deleteTaskId: null,
      taskCalendarFilterDate: null,
      expandedComments: null,
      activityDate:     new Date().toISOString().split("T")[0],
      activityMemberId: "",
      teamActivity:     [],
      topApps:          [],
      memberDetail:     null,
      memberPeriods:    [],
      memberWeekHistory: [],
      activityLoading:  false,
      activityTab:     'desktop',
      browserActivity: null,
      browserLoading:  false,
      expandedDomain:  null,
      screenshotData:     null,
      screenshotLoading:  false,
      screenshotLightbox: null,
      electronStatus:     null,
      currentTimeStr: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      chatInterval:        null,
      liveRefreshInterval: null,
      clockInterval:       null,
    }
  },

  computed: {
    todayDate() { return new Date().toISOString().split("T")[0] },

    ssStatusClass() {
      if (!this.electronStatus) return 'ss-status-unknown'
      const { electron_active, extension_active } = this.electronStatus
      if (electron_active && extension_active) return 'ss-status-ok'
      if (electron_active && !extension_active) return 'ss-status-warn'
      return 'ss-status-error'
    },
    ssStatusTitle() {
      if (!this.electronStatus) return 'Status unknown'
      const { electron_active, extension_active } = this.electronStatus
      if (electron_active && extension_active) return 'Screenshot system active'
      if (electron_active && !extension_active) return 'Chrome extension offline'
      return 'Electron app offline'
    },
    ssStatusDetail() {
      if (!this.electronStatus) return 'Could not reach the local Electron server.'
      const { electron_active, extension_active } = this.electronStatus
      if (electron_active && extension_active) return 'Screenshots taken automatically during work hours (9 AM – 6 PM).'
      if (electron_active && !extension_active) return 'Electron running but Chrome extension has not checked in.'
      return 'Electron app is not running — screenshots paused.'
    },

    filteredTasks() {
      let list = this.tasks
      if (this.taskCalendarFilterDate) {
        list = list.filter(t => t.start_date === this.taskCalendarFilterDate)
      }
      if (this.headerSearch) {
        const t = this.headerSearch.toLowerCase()
        list = list.filter(task =>
          task.title.toLowerCase().includes(t) || task.description.toLowerCase().includes(t)
        )
      }
      return list
    },
    filteredUsers() {
      if (!this.userSearch) return this.teamMembers
      const t = this.userSearch.toLowerCase()
      return this.teamMembers.filter(u => u.username.toLowerCase().includes(t))
    },
    userTasks() {
      if (!this.selectedMember) return []
      return this.tasks.filter(t => t.assigned_to && t.assigned_to.some(u => u.username === this.selectedMember))
    },
    userAttendance() {
      if (!this.selectedMember) return []
      return this.attendance.filter(a => a.user === this.selectedMember)
    },
    filteredAttendance() {
      return this.attendance.filter(a => a.date.split("T")[0] === this.selectedDate)
    },
    daysInMonth() { return new Date(this.calendarYear, this.calendarMonth, 0).getDate() },
    startDay()    { return new Date(this.calendarYear, this.calendarMonth - 1, 1).getDay() },

    // Simple tick marks for the mini gantt (every 4h)
    simpleTicks() {
      const ticks = []
      for (let h = 0; h <= 24; h += 4) {
        ticks.push({ h, pct: (h / 24) * 100, label: h === 24 ? '' : `${String(h).padStart(2,'0')}:00` })
      }
      return ticks
    },
    nowLinePct() {
      if (this.activityDate !== this.todayDate) return null
      const now = new Date()
      return ((now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds()) / 86400) * 100
    },
  },

  mounted() {
    this.fetchCurrentUser()
    this.fetchTasks()
    this.fetchUsers()
    this.fetchAttendance()
    this.fetchChat()
    this.chatInterval        = setInterval(this.fetchChat, 5000)
    this.liveRefreshInterval = setInterval(this.refreshLiveStatus, 30000)
    this.clockInterval = setInterval(() => {
      this.currentTimeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }, 60000)
  },

  beforeUnmount() {
    clearInterval(this.chatInterval)
    clearInterval(this.liveRefreshInterval)
    clearInterval(this.clockInterval)
  },

  methods: {
    donutShade(i) { return donutShade(i) },

    toggleTaskComments(taskId) { this.expandedComments = this.expandedComments === taskId ? null : taskId },

    shiftTaskCalendar(dir) {
      let m = this.calendarMonth + dir
      let y = this.calendarYear
      if (m < 1) { m = 12; y-- }
      if (m > 12) { m = 1; y++ }
      this.calendarMonth = m
      this.calendarYear = y
    },
    _padDate(day) {
      return `${this.calendarYear}-${String(this.calendarMonth).padStart(2,'0')}-${String(day).padStart(2,'0')}`
    },
    selectTaskCalendarDay(day) {
      const dateStr = this._padDate(day)
      this.taskCalendarFilterDate = this.taskCalendarFilterDate === dateStr ? null : dateStr
    },
    isTaskCalendarDaySelected(day) { return this.taskCalendarFilterDate === this._padDate(day) },
    isTaskCalendarDayToday(day) { return this._padDate(day) === this.todayDate },
    formatChipDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr + 'T00:00:00')
      return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
    },

    _donutCircumference() { return 2 * Math.PI * 80 },
    _donutTotalSeconds()  { return this.topApps.slice(0,6).reduce((s, a) => s + a.total_seconds, 0) },
    _donutDash(seconds, index) {
      const circ  = this._donutCircumference()
      const total = this._donutTotalSeconds()
      if (!total) return `0 ${circ}`
      return `${(seconds / total) * circ} ${circ - (seconds / total) * circ}`
    },
    _donutOffset(index) {
      const circ = this._donutCircumference()
      let offset = -(circ / 4)
      for (let i = 0; i < index; i++) {
        const total = this._donutTotalSeconds()
        offset -= total ? (this.topApps[i].total_seconds / total) * circ : 0
      }
      return offset
    },

    _appDonutCircumference() { return 2 * Math.PI * 55 },
    _appDonutTotalSeconds()  {
      if (!this.memberDetail?.app_breakdown) return 0
      return this.memberDetail.app_breakdown.slice(0,6).reduce((s, a) => s + a.seconds, 0)
    },
    _appDonutDash(seconds, index) {
      const circ  = this._appDonutCircumference()
      const total = this._appDonutTotalSeconds()
      if (!total) return `0 ${circ}`
      return `${(seconds / total) * circ} ${circ - (seconds / total) * circ}`
    },
    _appDonutOffset(index) {
      const circ = this._appDonutCircumference()
      let offset = -(circ / 4)
      if (!this.memberDetail?.app_breakdown) return offset
      for (let i = 0; i < index; i++) {
        const total = this._appDonutTotalSeconds()
        offset -= total ? (this.memberDetail.app_breakdown[i].seconds / total) * circ : 0
      }
      return offset
    },

    _timeToSeconds(t) {
      if (!t) return 0
      const [h=0, m=0, s=0] = t.split(':').map(Number)
      return h * 3600 + m * 60 + s
    },
    periodPct(fromTime)               { return (this._timeToSeconds(fromTime) / 86400) * 100 },
    periodWidthPct(fromTime, toTime)  {
      let from = this._timeToSeconds(fromTime)
      let to   = toTime ? this._timeToSeconds(toTime) : this._timeToSeconds(this.currentTimeStr + ':00')
      if (to < from) to = 86400
      return Math.max(((to - from) / 86400) * 100, 0.3)
    },

    _durationFromTimes(fromTime, toTime) {
      if (!fromTime) return '—'
      try {
        const base = '1970-01-01T'
        const from = new Date(base + fromTime)
        let to = toTime ? new Date(base + toTime) : new Date()
        if (to < from) to = new Date(to.getTime() + 86400000)
        const diffS = Math.round((to - from) / 1000)
        if (diffS <= 0) return '0s'
        const h = Math.floor(diffS / 3600)
        const m = Math.floor((diffS % 3600) / 60)
        const s = diffS % 60
        if (h > 0) return `${h}h ${m}m`
        if (m > 0) return `${m}m ${s}s`
        return `${s}s`
      } catch { return '—' }
    },

    _getTimelineStart() {
      if (this.memberPeriods?.length) return this.memberPeriods[0].from || '—'
      if (this.memberDetail?.summary) {
        const s = this.memberDetail.summary
        return s.first_active || s.tracking_start || s.start_time || '—'
      }
      return '—'
    },
    _getTimelineEnd() {
      if (this.memberPeriods?.length) return this.memberPeriods[this.memberPeriods.length - 1].to || '—'
      if (this.memberDetail?.summary) {
        const s = this.memberDetail.summary
        return s.last_active || s.tracking_end || '—'
      }
      return '—'
    },

    domainVisitCount(domain) {
      if (!this.browserActivity?.visits) return 0
      return this.browserActivity.visits.filter(v => v.domain === domain).length
    },
    domainVisits(domain) {
      if (!this.browserActivity?.visits) return []
      return this.browserActivity.visits.filter(v => v.domain === domain)
    },
    toggleDomain(domain) { this.expandedDomain = this.expandedDomain === domain ? null : domain },

    async apiCall(method, url, data = null) {
      const token  = localStorage.getItem("access")
      const config = { method, url: `${API_BASE}${url}`, headers: { Authorization: token ? `Bearer ${token}` : "" } }
      if (data && method.toLowerCase() !== "get") {
        config.headers["Content-Type"] = "application/json"
        config.data = data
      }
      const res = await axios(config)
      return res.data
    },

    async fetchCurrentUser() {
      try { const data = await this.apiCall("get", "me/"); this.currentUser = data.username || "Lead" }
      catch (err) { console.error("Me fetch failed:", err) }
    },
    async fetchTasks() {
      try { this.tasks = await this.apiCall("get", "created-tasks/") }
      catch (err) { console.error("Tasks fetch failed:", err) }
    },
    async fetchUsers() {
      try { this.teamMembers = await this.apiCall("get", "team-members/") }
      catch (err) { console.error("Users fetch failed:", err) }
    },
    async assignUser(taskId) {
      const userId = this.selectedUser[taskId]
      if (!userId) return alert("Select a member first")
      await this.apiCall("post", `assign-task/${taskId}/`, { assigned_to: [userId] })
      alert("Assigned successfully")
      this.fetchTasks()
      this.selectedUser[taskId] = ""
    },
    showModal(taskId) { this.deleteTaskId = taskId; this.showDeleteModal = true },
    async confirmDelete() {
      await this.apiCall("delete", `delete-task/${this.deleteTaskId}/`)
      this.fetchTasks()
      this.showDeleteModal = false
    },
    cancelDelete() { this.showDeleteModal = false; this.deleteTaskId = null },
    goToCreateTask() { this.$router.push("/create-task") },
    async fetchAttendance() {
      try { this.attendance = await this.apiCall("get", "attendance/") }
      catch (err) { console.error("Attendance fetch failed:", err) }
    },
    calculateBreakHours(breaks) {
      if (!breaks?.length) return "0h"
      let mins = 0
      breaks.forEach(b => { if (b.start && b.end) mins += (new Date(`1970-01-01T${b.end}`) - new Date(`1970-01-01T${b.start}`)) / 60000 })
      return (mins / 60).toFixed(2) + "h"
    },
    calculateWorkedAfterBreak(a) {
      const start = a.system_check_in; const end = a.system_check_out
      if (!start || !end) return "—"
      const totalMs = new Date(end) - new Date(start)
      let breakMs = 0
      if (a.breaks) a.breaks.forEach(b => { if (b.start && b.end) breakMs += new Date(`1970-01-01T${b.end}`) - new Date(`1970-01-01T${b.start}`) })
      return ((totalMs - breakMs) / 3600000).toFixed(2) + "h"
    },
    downloadCSV() {
      const headers = ["Date","User","Role","System In","System Out","Manual In","Manual Out","Breaks","Break hrs","Net worked"]
      const rows = this.attendance.map(a => [
        a.date.split("T")[0], a.user, a.role,
        a.system_check_in || "", a.system_check_out || "",
        a.manual_check_in || "", a.manual_check_out || "",
        a.breaks?.map(b => `${b.start}-${b.end || 'ongoing'}`).join(";") || "",
        this.calculateBreakHours(a.breaks), this.calculateWorkedAfterBreak(a)
      ])
      const csv = [headers, ...rows].map(r => r.join(",")).join("\n")
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" })
      const link = document.createElement("a")
      link.href = URL.createObjectURL(blob)
      link.setAttribute("download", "attendance.csv")
      link.click()
    },
    async fetchChat() {
      try {
        const data = await this.apiCall("get", "group-chat/")
        this.chatMessages = Array.isArray(data) ? data : (data.results || [])
      } catch (err) { console.error("Chat fetch failed:", err) }
    },
    async sendMessage() {
      if (!this.newMessage.trim()) return
      await this.apiCall("post", "group-chat/", { message: this.newMessage })
      this.newMessage = ""
      await this.fetchChat()
    },
    async clearChat() {
      if (!confirm("Clear all messages?")) return
      await this.apiCall("post", "group-chat-clear/")
      this.chatMessages = []
    },
    tasksForDay(day) {
      return this.tasks.filter(t => {
        if (!t.start_date) return false
        const d = new Date(t.start_date)
        return d.getDate() === day && d.getMonth() + 1 === this.calendarMonth && d.getFullYear() === this.calendarYear
      })
    },
    async refreshLiveStatus() {
      if (this.activeSection === 'activity' && !this.activityMemberId && this.activityDate === this.todayDate)
        await this.fetchTeamActivity()
    },
    async loadActivitySection() {
      this.activityLoading = true
      try {
        await Promise.all([this.fetchTeamActivity(), this.fetchLeaderboard()])
        if (this.activityMemberId) await this.loadMemberDetail()
      } finally { this.activityLoading = false }
    },
    async fetchTeamActivity() {
      try { const data = await this.apiCall("get", `activity/team/?date=${this.activityDate}`); this.teamActivity = data.team || [] }
      catch (err) { console.error("Team activity fetch failed:", err); this.teamActivity = [] }
    },
    async fetchLeaderboard() {
      try { const data = await this.apiCall("get", `activity/leaderboard/?date=${this.activityDate}`); this.topApps = data.top_apps || [] }
      catch (err) { console.error("Leaderboard fetch failed:", err); this.topApps = [] }
    },
    selectMember(userId) {
      this.activityMemberId = userId
      this.activityTab = 'desktop'
      this.browserActivity = null
      this.screenshotData = null
      this.screenshotLightbox = null
      this.expandedDomain = null
      this.loadMemberDetail()
    },
    async loadMemberDetail() {
      if (!this.activityMemberId) return
      this.activityLoading = true
      this.memberDetail = null
      this.memberPeriods = []
      this.memberWeekHistory = []
      try {
        const [detail, history] = await Promise.all([
          this.apiCall("get", `activity/member/${this.activityMemberId}/?date=${this.activityDate}`),
          this.apiCall("get", `activity/history/?days=7&user_id=${this.activityMemberId}`)
        ])
        this.memberDetail = detail
        this.memberWeekHistory = (history.history || []).slice().reverse()
        this.memberPeriods = this._buildPeriods(detail.timeline || [])
      } catch (err) { console.error("Member detail fetch failed:", err) }
      finally { this.activityLoading = false }
    },
    async fetchBrowserActivity() {
      if (!this.activityMemberId) return
      this.browserLoading = true; this.browserActivity = null; this.expandedDomain = null
      try {
        const data = await this.apiCall("get", `browser-activity/list/?user_id=${this.activityMemberId}&date=${this.activityDate}`)
        this.browserActivity = data
      } catch (err) { this.browserActivity = { total_browser: '0m', domain_breakdown: [], visits: [] } }
      finally { this.browserLoading = false }
    },
    async fetchScreenshots() {
      if (!this.activityMemberId) return
      this.screenshotLoading = true; this.screenshotData = null
      await this.fetchElectronStatus()
      try {
        const data = await this.apiCall("get", `browser-screenshot/?user_id=${this.activityMemberId}&date=${this.activityDate}`)
        this.screenshotData = data
      } catch (err) { this.screenshotData = { count: 0, screenshots: [], date: this.activityDate, username: '' } }
      finally { this.screenshotLoading = false }
    },
    async fetchElectronStatus() {
      try {
        const res = await fetch('http://localhost:3001/screenshot-status', { cache: 'no-store', signal: AbortSignal.timeout(3000) })
        this.electronStatus = res.ok ? await res.json() : null
      } catch { this.electronStatus = null }
    },
    openLightbox(ss, idx) {
      const member = this.teamMembers.find(m => m.id == this.activityMemberId)
      this.screenshotLightbox = { image: ss.image, time: this.formatSSTime(ss.timestamp), username: member?.username || 'Member', idx }
    },
    navigateLightbox(direction) {
      const newIdx = this.screenshotLightbox.idx + direction
      if (!this.screenshotData || newIdx < 0 || newIdx >= this.screenshotData.screenshots.length) return
      const ss = this.screenshotData.screenshots[newIdx]
      const member = this.teamMembers.find(m => m.id == this.activityMemberId)
      this.screenshotLightbox = { image: ss.image, time: this.formatSSTime(ss.timestamp), username: member?.username || 'Member', idx: newIdx }
    },
    formatSSTime(timestamp) { if (!timestamp) return '—'; return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) },
    async downloadWeeklyReport() {
      try {
        const token = localStorage.getItem("access")
        const res = await fetch(`${API_BASE}activity/weekly-report/`, { headers: { Authorization: `Bearer ${token}` } })
        if (!res.ok) throw new Error("Report generation failed")
        const blob = await res.blob()
        const link = document.createElement("a")
        link.href = URL.createObjectURL(blob)
        link.download = `weekly-activity-report-${new Date().toISOString().slice(0,10)}.pdf`
        link.click()
        URL.revokeObjectURL(link.href)
      } catch (err) { alert("Could not generate report: " + err.message) }
    },
    async downloadMemberReport(userId) {
      try {
        const token = localStorage.getItem("access")
        const res = await fetch(`${API_BASE}activity/weekly-report/?user_id=${userId}`, { headers: { Authorization: `Bearer ${token}` } })
        if (!res.ok) throw new Error("Report generation failed")
        const blob = await res.blob()
        const link = document.createElement("a")
        const member = this.teamMembers.find(m => m.id == userId)
        link.href = URL.createObjectURL(blob)
        link.download = `report-${member?.username || userId}-${new Date().toISOString().slice(0,10)}.pdf`
        link.click()
        URL.revokeObjectURL(link.href)
      } catch (err) { alert("Could not generate report: " + err.message) }
    },
    sparkHeight(seconds) {
      if (!this.memberWeekHistory.length) return 0
      const max = Math.max(...this.memberWeekHistory.map(d => d.total_active_seconds || 0))
      if (!max) return 0
      return Math.round((seconds / max) * 100)
    },
    _buildPeriods(timeline) {
      if (!timeline?.length) return []
      const periods = []
      let current = null
      timeline.forEach(row => {
        const type = row.type === 'idle' ? 'idle' : 'active'
        if (!current || current.type !== type) {
          if (current) periods.push(current)
          current = { type, from: row.from_time, to: row.to_time, seconds: row.seconds, duration: row.duration }
        } else {
          current.to = row.to_time
          current.seconds += row.seconds
          current.duration = this._fmtSec(current.seconds)
        }
      })
      if (current) periods.push(current)
      return periods
    },
    _fmtSec(s) {
      if (!s || s < 60) return (s || 0) + 's'
      const h = Math.floor(s / 3600)
      const m = Math.floor((s % 3600) / 60)
      return h > 0 ? `${h}h ${m}m` : `${m}m`
    },
    fmtSeconds(s) {
      const h = Math.floor(s / 3600); const m = Math.floor((s % 3600) / 60)
      return h > 0 ? `${h}h ${m}m` : `${m}m`
    },
    formatDateTime(dateStr) { return dateStr ? new Date(dateStr).toLocaleString() : "—" },
    formatLogTime(ts) { if (!ts) return "—"; return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) }
  }
}
</script>

<style scoped>
/* ============================================================
   QRM LEAD DASHBOARD v3 — tasks + mini calendar, tighter cards
   ============================================================ */

* { font-family:'Poppins',sans-serif; box-sizing:border-box; margin:0; padding:0; }

/* ── Token system ── */
.light {
  --bg:#edf0f5;
  --surface:#f6f8fb;
  --card:#ffffff;
  --text:#121c2d;
  --text-muted:#64748b;
  --text-faint:#94a3b8;
  --border:rgba(15,23,42,0.07);
  --border-mid:rgba(15,23,42,0.11);
  --accent:#159aff;
  --accent-deep:#0c6bb8;
  --shadow-xs:0 1px 2px rgba(16,24,40,0.05);
  --shadow-sm:0 1px 3px rgba(16,24,40,0.06), 0 1px 2px rgba(16,24,40,0.04);
  --shadow-md:0 4px 16px rgba(16,24,40,0.07), 0 2px 4px rgba(16,24,40,0.04);
  --shadow-lg:0 20px 48px rgba(16,24,40,0.10), 0 6px 16px rgba(16,24,40,0.05);
  --sidebar-bg:linear-gradient(175deg,#0a1525 0%,#0f1e34 50%,#0b1828 100%);
}
.dark {
  --bg:#080d15;
  --surface:#0d1420;
  --card:#111825;
  --text:#e8edf5;
  --text-muted:#7b8fa8;
  --text-faint:#4a5568;
  --border:rgba(255,255,255,0.065);
  --border-mid:rgba(255,255,255,0.10);
  --accent:#159aff;
  --accent-deep:#0c6bb8;
  --shadow-xs:0 1px 2px rgba(0,0,0,0.35);
  --shadow-sm:0 1px 3px rgba(0,0,0,0.4);
  --shadow-md:0 6px 20px rgba(0,0,0,0.4);
  --shadow-lg:0 24px 64px rgba(0,0,0,0.55);
  --sidebar-bg:linear-gradient(175deg,#050a12 0%,#0a1220 50%,#060c18 100%);
}

.dashboard-layout { display:flex; min-height:100vh; background:var(--bg); transition:background .3s ease; }

/* ──────── SIDEBAR ──────── */
.sidebar {
  width:240px; margin:12px; border-radius:20px; padding:20px 14px 16px;
  color:#fff;
  background:var(--sidebar-bg);
  box-shadow:0 20px 60px rgba(5,12,24,0.5), inset 0 1px 0 rgba(255,255,255,0.05), inset -1px 0 0 rgba(255,255,255,0.03);
  border:1px solid rgba(255,255,255,0.045);
  display:flex; flex-direction:column; gap:4px; transition:all .28s ease; position:relative; z-index:2; flex-shrink:0;
}
.sidebar.collapsed { width:62px; padding:16px 8px 14px; }

.user-info { display:flex; flex-direction:column; align-items:center; padding-bottom:16px; margin-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.06); }
.avatar { width:42px; height:42px; border-radius:50%; margin-bottom:8px; border:2px solid rgba(21,154,255,0.5); box-shadow:0 0 0 4px rgba(21,154,255,0.1), 0 4px 14px rgba(0,0,0,0.3); }
.username { font-weight:700; font-size:12.5px; color:#f0f4fa; letter-spacing:.005em; }
.user-role { font-size:10.5px; color:rgba(255,255,255,0.38); margin-top:2px; font-weight:500; }

.nav-group { padding:4px 4px 2px; }
.nav-group-label { font-size:9.5px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:rgba(255,255,255,0.28); }

.nav-btn { border:none; background:transparent; color:rgba(255,255,255,0.55); padding:9px 10px; border-radius:10px; font-size:12.5px; font-weight:500; cursor:pointer; text-align:left; transition:all .16s ease; display:flex; align-items:center; gap:9px; letter-spacing:.01em; }
.nav-btn.active { background:rgba(21,154,255,0.14); color:#fff; box-shadow:inset 3px 0 0 #159aff; }
.nav-btn:hover:not(.active) { background:rgba(255,255,255,0.055); color:rgba(255,255,255,0.85); }
.icon { width:16px; height:16px; flex-shrink:0; }

.sidebar-divider { height:1px; background:rgba(255,255,255,0.06); margin:8px 0; }

.create-btn { background:rgba(21,154,255,0.13); color:rgba(100,180,255,0.9); border:1px solid rgba(21,154,255,0.22); font-weight:600; margin-top:4px; }
.create-btn:hover { background:rgba(21,154,255,0.24); color:#fff; }

.collapse-btn { margin-top:auto; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08); color:rgba(255,255,255,0.55); cursor:pointer; font-size:13px; border-radius:9px; padding:8px; display:flex; align-items:center; justify-content:center; transition:all .18s; }
.collapse-btn:hover { background:rgba(255,255,255,0.1); color:#fff; }

.theme-toggle { margin-top:10px; }
.theme-label { display:flex; align-items:center; gap:8px; font-size:11px; color:rgba(255,255,255,0.42); cursor:pointer; font-weight:500; }
.theme-label input { display:none; }
.theme-track { width:28px; height:16px; border-radius:8px; background:rgba(255,255,255,0.1); position:relative; transition:background .2s; flex-shrink:0; }
.theme-label input:checked + .theme-track { background:rgba(21,154,255,0.6); }
.theme-thumb { position:absolute; top:2px; left:2px; width:12px; height:12px; border-radius:50%; background:#fff; transition:transform .2s; }
.theme-label input:checked + .theme-track .theme-thumb { transform:translateX(12px); }

.sidebar.collapsed .nav-btn { justify-content:center; padding:9px; }
.sidebar.collapsed .nav-btn span { display:none; }
.sidebar.collapsed .icon { margin:0; }
.sidebar.collapsed .username, .sidebar.collapsed .user-role, .sidebar.collapsed .nav-group, .sidebar.collapsed .theme-toggle, .sidebar.collapsed .sidebar-divider { display:none; }

/* ──────── MAIN ──────── */
.content { flex:1; padding:24px 32px; color:var(--text); display:flex; flex-direction:column; gap:16px; overflow:auto; min-width:0; }

.mobile-toggle { display:none; position:fixed; top:14px; left:14px; z-index:200; background:var(--accent); color:#fff; border:none; padding:9px; border-radius:10px; cursor:pointer; box-shadow:0 4px 14px rgba(21,154,255,0.4); }

/* ──────── HEADER / SEARCH ──────── */
.header-search { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:8px; flex-wrap:wrap; }
.greeting-block { display:flex; flex-direction:column; gap:2px; }
.greeting { font-weight:700; font-size:22px; letter-spacing:-.02em; color:var(--text); }
.greeting-name { color:var(--accent); }
.greeting-sub { font-size:12px; color:var(--text-muted); font-weight:500; }
.search-wrap { position:relative; flex:1; max-width:320px; }
.search-icon { position:absolute; left:12px; top:50%; transform:translateY(-50%); width:15px; height:15px; color:var(--text-faint); pointer-events:none; }
.search-wrap input { width:100%; padding:9px 13px 9px 36px; border-radius:10px; border:1px solid var(--border); background:var(--card); color:var(--text); font-size:13px; box-shadow:var(--shadow-sm); transition:border-color .15s, box-shadow .15s; }
.search-wrap input:focus { outline:none; border-color:rgba(21,154,255,0.4); box-shadow:0 0 0 3px rgba(21,154,255,0.08); }

/* ──────── SECTION TOPBAR ──────── */
.section-topbar { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; gap:12px; flex-wrap:wrap; }
.section-heading { font-size:16px; font-weight:700; color:var(--text); letter-spacing:-.01em; border-bottom:1px solid var(--border); padding-bottom:10px; margin-bottom:12px; display:flex; align-items:center; gap:8px; }
.section-label { font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:.07em; color:var(--text-muted); }
.sub-heading { font-size:14px; font-weight:700; color:var(--text); margin:16px 0 10px; }
.section-actions { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.date-input { padding:7px 11px; border-radius:9px; border:1px solid var(--border); background:var(--card); color:var(--text); font-size:12.5px; box-shadow:var(--shadow-xs); }

/* ──────── BUTTONS ──────── */
.btn-primary { padding:7px 14px; border-radius:9px; background:var(--accent); color:#fff; border:none; cursor:pointer; font-weight:600; font-size:12.5px; transition:all .15s; display:inline-flex; align-items:center; gap:5px; }
.btn-primary:hover { background:#0c87e6; transform:translateY(-1px); }
.btn-primary.btn-xs { padding:5px 10px; font-size:11px; border-radius:7px; }
.btn-danger { padding:7px 14px; border-radius:9px; background:#dc2626; color:#fff; border:none; cursor:pointer; font-weight:600; font-size:12.5px; transition:all .15s; }
.btn-danger:hover { background:#b91c1c; }
.btn-danger.btn-sm { padding:5px 11px; font-size:11.5px; }
.btn-danger.btn-xs { padding:5px 8px; font-size:11px; border-radius:7px; display:inline-flex; align-items:center; justify-content:center; }
.btn-outline { padding:7px 14px; border-radius:9px; background:transparent; color:var(--text-muted); border:1px solid var(--border-mid); cursor:pointer; font-weight:600; font-size:12.5px; transition:all .15s; }
.btn-outline:hover { border-color:var(--accent); color:var(--accent); }
.btn-outline-accent { padding:7px 14px; border-radius:9px; background:transparent; color:var(--accent); border:1px solid rgba(21,154,255,0.3); cursor:pointer; font-weight:600; font-size:12.5px; transition:all .15s; display:inline-flex; align-items:center; gap:5px; }
.btn-outline-accent:hover { background:rgba(21,154,255,0.07); }
.btn-ghost { padding:7px 13px; border-radius:9px; background:var(--card); border:1px solid var(--border); color:var(--text-muted); cursor:pointer; font-size:12px; font-weight:600; display:inline-flex; align-items:center; gap:5px; transition:all .15s; box-shadow:var(--shadow-xs); }
.btn-ghost:hover { border-color:var(--accent); color:var(--accent); }
.btn-accent { padding:7px 14px; border-radius:9px; background:var(--accent-deep); color:#fff; border:none; cursor:pointer; font-size:12.5px; font-weight:600; display:inline-flex; align-items:center; gap:5px; transition:all .15s; box-shadow:0 3px 10px rgba(12,107,184,0.3); }
.btn-accent:hover { background:var(--accent); transform:translateY(-1px); }
.btn-accent.btn-sm { padding:5px 11px; font-size:11.5px; }
.btn-back { padding:7px 13px; border-radius:9px; background:transparent; border:1px solid var(--border-mid); color:var(--text-muted); cursor:pointer; font-size:12.5px; font-weight:600; display:inline-flex; align-items:center; gap:5px; transition:all .15s; }
.btn-back:hover { border-color:var(--accent); color:var(--accent); }

/* ──────── PANEL CARD (generic container) ──────── */
.panel-card { background:var(--card); border-radius:16px; padding:20px 22px; border:1px solid var(--border); box-shadow:var(--shadow-md); }
.panel-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; }
.panel-title { font-size:13.5px; font-weight:700; color:var(--text); letter-spacing:-.005em; display:block; }
.panel-sub { font-size:11px; color:var(--text-muted); display:block; margin-top:2px; }
.panel-title-row { display:flex; align-items:center; gap:8px; }

/* ──────── TASKS LAYOUT (list + calendar) ──────── */
.tasks-layout { display:grid; grid-template-columns:1fr 300px; gap:18px; align-items:start; }
.tasks-list-col { min-width:0; }
.tasks-calendar-col { display:flex; flex-direction:column; gap:14px; position:sticky; top:8px; }

.tasks-col-header { display:flex; align-items:center; justify-content:space-between; gap:10px; border-bottom:1px solid var(--border); padding-bottom:10px; margin-bottom:12px; flex-wrap:wrap; }
.tasks-count-badge { display:inline-flex; align-items:center; justify-content:center; min-width:20px; height:20px; padding:0 6px; background:rgba(21,154,255,0.1); color:var(--accent); border-radius:10px; font-size:11px; font-weight:700; }
.chip-clear { display:inline-flex; align-items:center; gap:6px; padding:5px 10px; border-radius:16px; background:rgba(21,154,255,0.09); color:var(--accent); border:1px solid rgba(21,154,255,0.22); font-size:11.5px; font-weight:600; cursor:pointer; transition:all .15s; }
.chip-clear:hover { background:rgba(21,154,255,0.18); }

/* Compact task list - single column, denser cards */
.task-list-compact { grid-template-columns:1fr; gap:10px; display:grid; }
.task-card-compact { padding:13px 15px; border-radius:13px; }
.task-card-compact:hover { transform:translateY(-1px); }

.task-header-compact { padding:7px 11px; margin-bottom:9px; border-radius:9px; }
.task-header-compact .task-title { font-size:12.5px; }

.desc-compact { font-size:12px; line-height:1.5; color:var(--text-muted); margin-bottom:8px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }

.task-meta-row { margin-bottom:8px; }
.meta-pill { display:inline-flex; align-items:center; gap:5px; font-size:10.5px; color:var(--text-faint); background:var(--surface); border:1px solid var(--border); padding:3px 9px; border-radius:8px; font-weight:600; }

.task-comments-compact { margin-bottom:8px; }
.comments-toggle { display:inline-flex; align-items:center; gap:5px; font-size:11px; font-weight:600; color:var(--accent); cursor:pointer; }
.comments-toggle svg { transition:transform .18s; }
.comments-toggle svg.rotated { transform:rotate(180deg); }

.assigned-row { margin-bottom:10px; }

.task-card-footer { display:flex; align-items:center; justify-content:space-between; gap:8px; padding-top:10px; border-top:1px solid var(--border); }
.assign-section-compact { display:flex; gap:6px; flex:1; min-width:0; }
.assign-section-compact select { flex:1; min-width:0; padding:6px 8px; font-size:11.5px; border-radius:7px; border:1px solid var(--border); background:var(--card); color:var(--text); }

/* ──────── MINI CALENDAR (tasks sidebar) ──────── */
.mini-cal-card { background:var(--card); border-radius:16px; padding:16px 17px; border:1px solid var(--border); box-shadow:var(--shadow-md); }
.mini-cal-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.mini-cal-nav { display:flex; gap:4px; }
.mini-cal-nav-btn { width:22px; height:22px; border-radius:7px; background:var(--surface); border:1px solid var(--border); color:var(--text-muted); cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all .15s; }
.mini-cal-nav-btn:hover { border-color:var(--accent); color:var(--accent); }

.mini-cal-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:3px; }
.mini-cal-day { aspect-ratio:1; display:flex; flex-direction:column; align-items:center; justify-content:center; border-radius:8px; font-size:11px; cursor:pointer; transition:all .15s; position:relative; gap:2px; }
.mini-cal-dow { font-size:9px; font-weight:700; color:var(--text-faint); text-transform:uppercase; cursor:default; aspect-ratio:auto; height:18px; }
.mini-cal-blank { cursor:default; }
.mini-cal-daynum { font-weight:600; color:var(--text); }
.mini-cal-day:hover:not(.mini-cal-blank):not(.mini-cal-dow) { background:rgba(21,154,255,0.08); }
.mini-cal-day.is-today .mini-cal-daynum { color:var(--accent); font-weight:800; }
.mini-cal-day.is-today { box-shadow:inset 0 0 0 1.5px rgba(21,154,255,0.35); }
.mini-cal-day.is-selected { background:linear-gradient(135deg,#0b5fa0,#159aff); }
.mini-cal-day.is-selected .mini-cal-daynum { color:#fff; }
.mini-cal-day.has-tasks:not(.is-selected) { background:rgba(21,154,255,0.04); }
.mini-cal-dot-row { display:flex; gap:2px; }
.mini-cal-dot { width:4px; height:4px; border-radius:50%; }
.mini-cal-day.is-selected .mini-cal-dot { background:#fff !important; opacity:.85; }

.mini-cal-legend { display:flex; flex-wrap:wrap; gap:10px; margin-top:12px; padding-top:11px; border-top:1px solid var(--border); }
.mini-cal-legend span { display:inline-flex; align-items:center; gap:5px; font-size:10px; color:var(--text-muted); font-weight:600; }
.mini-cal-legend i { width:6px; height:6px; border-radius:50%; display:inline-block; }
.dot-pending { background:#eab308; }
.dot-progress { background:#159aff; }
.dot-complete { background:#22c55e; }

.day-task-mini-list { display:flex; flex-direction:column; gap:6px; max-height:260px; overflow-y:auto; }
.day-task-mini-item { display:flex; align-items:center; gap:8px; padding:7px 9px; border-radius:9px; background:var(--surface); border:1px solid var(--border); text-decoration:none; transition:all .15s; }
.day-task-mini-item:hover { border-color:rgba(21,154,255,0.3); background:rgba(21,154,255,0.05); }
.dtm-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
.dtm-dot.complete { background:#22c55e; }
.dtm-dot.in_progress { background:#159aff; }
.dtm-dot.pending { background:#eab308; }
.dtm-title { font-size:11.5px; font-weight:600; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

/* ──────── TASKS (legacy / users section cards) ──────── */
.task-list { list-style:none; padding:0; display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }
.task-card { background:var(--card); border-radius:16px; padding:18px 20px; box-shadow:var(--shadow-md); border:1px solid var(--border); transition:transform .2s ease, box-shadow .2s ease; }
.task-card:hover { transform:translateY(-2px); box-shadow:var(--shadow-lg); }
.task-header { display:flex; justify-content:space-between; align-items:center; padding:9px 13px; border-radius:10px; background:linear-gradient(135deg,#0b5fa0,#159aff); color:#fff; margin-bottom:12px; box-shadow:0 4px 14px rgba(21,154,255,0.2); }
.task-title { font-weight:700; font-size:13.5px; }
.task-desc-card { background:rgba(21,154,255,0.04); border-radius:10px; padding:12px 14px; margin-bottom:11px; border:1px solid rgba(21,154,255,0.08); font-size:12.5px; }
.desc { color:var(--text-muted); line-height:1.55; margin-bottom:6px; }
.task-meta { font-size:12px; color:var(--text-faint); }
.task-comments { margin-top:8px; }
.comments-list { list-style:none; padding-left:8px; font-size:12px; margin-top:4px; display:flex; flex-direction:column; gap:3px; }
.assigned-section { margin:10px 0 4px; }
.assigned-label { font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; color:var(--text-muted); display:block; margin-bottom:5px; }
.assigned-pills { display:flex; flex-wrap:wrap; gap:4px; }
.assigned-pill { background:rgba(21,154,255,0.08); color:var(--accent); border:1px solid rgba(21,154,255,0.18); border-radius:16px; padding:2px 9px; font-size:11.5px; font-weight:600; }
.unassigned-note { font-size:11.5px; color:var(--text-faint); }
.assign-section { display:flex; gap:7px; margin-top:10px; }
.assign-section select { flex:1; padding:7px 10px; border-radius:8px; border:1px solid var(--border); background:var(--card); color:var(--text); font-size:12.5px; }
.assign-btn { flex-shrink:0; }

.status { padding:3px 9px; border-radius:6px; font-size:10px; font-weight:700; letter-spacing:.04em; text-transform:uppercase; flex-shrink:0; }
.status.in_progress { background:#dbeafe; color:#1d4ed8; }
.status.complete    { background:#dcfce7; color:#166534; }
.status.pending     { background:#fef9c3; color:#854d0e; }

.empty-state { display:flex; flex-direction:column; align-items:center; gap:10px; padding:36px 24px; color:var(--text-muted); font-size:13px; text-align:center; }

/* ──────── ATTENDANCE ──────── */
.attendance-card { background:var(--card); border-radius:16px; padding:20px; overflow-x:auto; border:1px solid var(--border); box-shadow:var(--shadow-md); }
.attendance-table { width:100%; border-collapse:collapse; }
.attendance-table th { font-size:10.5px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); font-weight:700; padding:10px 12px; border-bottom:1px solid var(--border); white-space:nowrap; }
.attendance-table td { padding:10px 12px; font-size:12.5px; border-bottom:1px solid var(--border); }
.attendance-table tbody tr:hover { background:rgba(21,154,255,0.03); }
.user-chip { background:rgba(21,154,255,0.07); color:var(--accent); border-radius:6px; padding:2px 8px; font-size:12px; font-weight:600; }
.role-tag { background:var(--surface); color:var(--text-muted); border:1px solid var(--border); border-radius:6px; padding:2px 8px; font-size:11px; font-weight:600; }
.break-entry { font-size:11.5px; color:var(--text-muted); }
.time-chip { background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:2px 9px; font-size:12px; font-weight:600; font-variant-numeric:tabular-nums; }
.time-chip-accent { background:rgba(21,154,255,0.07); border-color:rgba(21,154,255,0.15); color:var(--accent); }

/* ──────── USERS ──────── */
.user-search-wrap { display:flex; gap:10px; margin-bottom:16px; flex-wrap:wrap; align-items:center; }
.user-select { padding:9px 12px; border-radius:10px; border:1px solid var(--border); background:var(--card); color:var(--text); font-size:13px; box-shadow:var(--shadow-xs); }
.user-task-cards { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; }

/* ──────── CHAT ──────── */
.chat-page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.chat-container { background:var(--card); border-radius:16px; padding:20px; border:1px solid var(--border); box-shadow:var(--shadow-md); display:flex; flex-direction:column; gap:12px; }
.chat-messages { overflow-y:auto; display:flex; flex-direction:column; gap:8px; border:1px solid var(--border); border-radius:12px; min-height:200px; max-height:360px; padding:14px; background:var(--surface); }
.chat-msg { display:flex; flex-direction:column; max-width:72%; }
.chat-msg.self { align-self:flex-end; align-items:flex-end; }
.chat-msg.other { align-self:flex-start; }
.chat-sender { font-size:10px; font-weight:700; color:var(--text-muted); margin-bottom:3px; letter-spacing:.03em; text-transform:uppercase; }
.chat-bubble { padding:9px 13px; border-radius:12px; font-size:13px; line-height:1.5; }
.chat-msg.self  .chat-bubble { background:linear-gradient(135deg,#0b5fa0,#159aff); color:#fff; border-radius:12px 12px 2px 12px; box-shadow:0 3px 12px rgba(21,154,255,0.25); }
.chat-msg.other .chat-bubble { background:var(--card); color:var(--text); border:1px solid var(--border); border-radius:12px 12px 12px 2px; }
.chat-time { font-size:10px; color:var(--text-faint); margin-top:3px; }
.chat-input-wrap { display:flex; gap:8px; }
.chat-input-wrap input { flex:1; padding:10px 13px; border-radius:10px; border:1px solid var(--border); background:var(--surface); color:var(--text); font-size:13px; }
.chat-input-wrap input:focus { outline:none; border-color:rgba(21,154,255,0.4); }

/* ──────── ACTIVITY SECTION ──────── */
.activity-section { display:flex; flex-direction:column; gap:16px; }

.act-page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:16px; flex-wrap:wrap; }
.act-header-left { display:flex; flex-direction:column; gap:8px; }
.page-title { font-size:22px; font-weight:700; letter-spacing:-.02em; color:var(--text); }

.act-context-bar { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.ctx-chip { display:inline-flex; align-items:center; gap:5px; font-size:12px; color:var(--text-muted); font-weight:500; }
.ctx-chip strong { color:var(--text); font-weight:700; }
.ctx-icon { width:12px; height:12px; color:var(--text-faint); }
.ctx-sep { color:var(--text-faint); font-size:13px; }
.ctx-time .ctx-from { color:#22c55e; font-weight:700; }
.ctx-time .ctx-to   { color:var(--text); font-weight:700; }
.ctx-arrow { color:var(--text-faint); margin:0 2px; }

.act-filters { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.act-filters input, .act-filters select { padding:7px 10px; border-radius:9px; border:1px solid var(--border); font-size:12px; background:var(--card); color:var(--text); box-shadow:var(--shadow-xs); }

/* ──────── LIVE STATUS ──────── */
.live-status-row { margin-bottom:4px; }
.live-badges { display:flex; flex-wrap:wrap; gap:7px; margin-top:8px; }
.live-badge { display:inline-flex; align-items:center; gap:6px; padding:6px 12px; border-radius:20px; font-size:11.5px; border:1px solid transparent; cursor:pointer; transition:all .18s; }
.live-badge:hover { transform:translateY(-1px); box-shadow:var(--shadow-sm); }
.lb-active  { background:rgba(21,154,255,0.08); border-color:rgba(21,154,255,0.24); color:var(--accent); }
.lb-idle    { background:rgba(100,116,139,0.08); border-color:rgba(100,116,139,0.24); color:#64748b; }
.lb-stopped { background:rgba(0,0,0,0.03); border-color:var(--border); color:var(--text-faint); }
.live-dot { width:6px; height:6px; border-radius:50%; flex-shrink:0; }
.lb-active  .live-dot { background:var(--accent); animation:pulse 1.5s infinite; }
.lb-idle    .live-dot { background:#94a3b8; }
.lb-stopped .live-dot { background:#cbd5e1; }
.live-name  { font-weight:600; }
.live-state { opacity:.7; font-size:10.5px; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.75)} }
.track-status-badge { font-size:10px; font-weight:600; padding:2px 7px; border-radius:7px; display:inline-flex; align-items:center; gap:4px; width:fit-content; }

/* ──────── TOP APPS DONUT ──────── */
.top-apps-donut-layout { display:flex; align-items:center; gap:28px; flex-wrap:wrap; }
.donut-center-wrap { display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.donut-svg { width:190px; height:190px; filter:drop-shadow(0 8px 24px rgba(21,154,255,0.14)); }
.donut-legend { display:flex; flex-direction:column; gap:9px; flex:1; min-width:160px; }
.donut-legend-row { display:flex; align-items:center; gap:9px; }
.donut-legend-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.donut-legend-name { flex:1; font-size:13px; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-weight:500; }
.donut-legend-time { font-size:12px; font-weight:700; color:var(--text-muted); white-space:nowrap; font-variant-numeric:tabular-nums; }

/* ──────── MEMBER CARD GRID ──────── */
.member-card-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; }
.member-card { background:var(--surface); border:1px solid var(--border); border-radius:15px; padding:16px 18px; cursor:pointer; transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease; display:flex; flex-direction:column; gap:12px; }
.member-card:hover { transform:translateY(-2px); box-shadow:0 12px 28px rgba(21,154,255,0.12); border-color:rgba(21,154,255,0.25); }
.mc-header { display:flex; align-items:center; gap:10px; }
.mc-avatar { width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:700; color:#fff; flex-shrink:0; background:linear-gradient(135deg,#0b5fa0,#159aff); box-shadow:0 3px 10px rgba(21,154,255,0.3); }
.mc-name-block { flex:1; display:flex; flex-direction:column; gap:3px; min-width:0; }
.mc-name { font-size:13.5px; font-weight:700; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mc-view-btn { width:27px; height:27px; border-radius:50%; background:rgba(21,154,255,0.08); color:var(--accent); border:1px solid rgba(21,154,255,0.18); cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all .15s; flex-shrink:0; }
.mc-view-btn:hover { background:rgba(21,154,255,0.2); }
.mc-stats { display:grid; grid-template-columns:repeat(3,1fr); gap:7px; }
.mc-stat { display:flex; flex-direction:column; gap:2px; background:var(--card); border-radius:8px; padding:8px 10px; border:1px solid var(--border); }
.mc-stat-label { font-size:9px; text-transform:uppercase; letter-spacing:.06em; color:var(--text-faint); font-weight:700; }
.mc-stat-value { font-size:13.5px; font-weight:700; color:var(--text); font-variant-numeric:tabular-nums; }
.mc-active-val { color:var(--accent) !important; }
.mc-idle-val   { color:#64748b !important; }
.mc-pct-row { display:flex; align-items:center; gap:8px; }
.mc-pct-track { flex:1; height:4px; background:rgba(21,154,255,0.08); border-radius:2px; overflow:hidden; }
.mc-pct-fill { height:100%; border-radius:2px; background:linear-gradient(90deg,var(--accent-deep),var(--accent)); transition:width .6s ease; }
.mc-pct-label { font-size:10.5px; font-weight:700; color:var(--text-muted); white-space:nowrap; font-variant-numeric:tabular-nums; }

/* ──────── MEMBER DETAIL ──────── */
.member-detail-topbar { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }
.member-detail-wrap { display:flex; flex-direction:column; gap:16px; }
.member-detail-title { font-size:18px; font-weight:700; color:var(--text); letter-spacing:-.01em; margin-bottom:4px; }
.member-detail-title span { color:var(--text-muted); font-weight:400; font-size:15px; }

/* Tabs */
.act-type-tabs { display:flex; gap:3px; background:var(--surface); border-radius:12px; padding:4px; width:fit-content; border:1px solid var(--border); margin-bottom:18px; }
.act-type-tab { padding:7px 16px; border:none; background:transparent; font-size:12px; font-weight:600; color:var(--text-muted); cursor:pointer; border-radius:9px; transition:all .18s; display:flex; align-items:center; gap:5px; }
.act-type-tab.active { color:#fff; background:var(--accent); box-shadow:0 3px 10px rgba(21,154,255,0.35); }
.act-type-tab:hover:not(.active) { background:rgba(0,0,0,0.04); color:var(--text); }
.ss-tab-badge { display:inline-flex; align-items:center; justify-content:center; width:15px; height:15px; background:rgba(255,255,255,0.25); color:#fff; border-radius:50%; font-size:9px; font-weight:700; }
.act-type-tab:not(.active) .ss-tab-badge { background:var(--accent); }

/* 7-day sparkline */
.sparkline-row { display:flex; align-items:flex-end; gap:5px; height:60px; margin-top:4px; }
.spark-bar-col { display:flex; flex-direction:column; align-items:center; gap:4px; flex:1; }
.spark-bar-track { width:100%; flex:1; background:rgba(21,154,255,0.07); border-radius:4px; position:relative; overflow:hidden; }
.spark-bar-fill { width:100%; position:absolute; bottom:0; background:linear-gradient(180deg,var(--accent),var(--accent-deep)); border-radius:4px; transition:height .5s; }
.spark-label { font-size:9px; color:var(--text-faint); white-space:nowrap; font-variant-numeric:tabular-nums; }

/* ──────── DESKTOP STATS ──────── */
.desktop-stat-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; }
.dsg-card { display:flex; align-items:center; gap:14px; border-radius:14px; padding:17px 19px; border:1px solid transparent; transition:transform .15s; }
.dsg-card:hover { transform:translateY(-1px); }
.dsg-active { background:rgba(21,154,255,0.04); border-color:rgba(21,154,255,0.14); }
.dsg-idle   { background:rgba(100,116,139,0.04); border-color:rgba(100,116,139,0.14); }
.dsg-pct    { background:rgba(12,107,184,0.04); border-color:rgba(12,107,184,0.14); }
.dsg-icon { width:42px; height:42px; border-radius:12px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.dsg-active .dsg-icon { background:rgba(21,154,255,0.1); color:var(--accent); }
.dsg-idle   .dsg-icon { background:rgba(100,116,139,0.1); color:#64748b; }
.dsg-pct    .dsg-icon { background:rgba(12,107,184,0.1); color:var(--accent-deep); }
.dsg-body { display:flex; flex-direction:column; gap:3px; flex:1; }
.dsg-label { font-size:10.5px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); font-weight:700; }
.dsg-value { font-size:24px; font-weight:700; line-height:1; font-variant-numeric:tabular-nums; letter-spacing:-.01em; }
.dsg-active .dsg-value { color:var(--accent); }
.dsg-idle   .dsg-value { color:#64748b; }
.dsg-pct    .dsg-value { color:var(--accent-deep); }
.dsg-pct-row { display:flex; align-items:center; gap:14px; }
.dsg-pct-bar-wrap { flex:1; height:6px; background:rgba(12,107,184,0.07); border-radius:4px; overflow:hidden; }
.dsg-pct-bar { height:100%; background:linear-gradient(90deg,var(--accent-deep),var(--accent)); border-radius:4px; transition:width .6s ease; }

/* ──────── DESKTOP BOTTOM GRID ──────── */
.desktop-bottom-grid { display:grid; grid-template-columns:1fr 2fr; gap:14px; align-items:start; margin-top:6px; }

/* App donut */
.app-donut-layout { display:flex; align-items:center; gap:18px; flex-wrap:wrap; }
.app-donut-svg { width:130px; height:130px; flex-shrink:0; filter:drop-shadow(0 4px 14px rgba(21,154,255,0.12)); }
.app-donut-legend { display:flex; flex-direction:column; gap:7px; flex:1; min-width:110px; }

/* ══════════════════════════════════════════════
   ACTIVE / IDLE TIMELINE — side-by-side panels
   ══════════════════════════════════════════════ */
.timeline-split-wrap { display:grid; grid-template-columns:1fr 1fr; gap:14px; align-items:start; }

.timeline-lane-panel { display:flex; flex-direction:column; gap:0; }

/* Accent left border per lane */
.timeline-lane-active-panel { border-left:3px solid var(--accent); }
.timeline-lane-idle-panel   { border-left:3px solid #94a3b8; }

/* Count badge */
.tl-count-badge { font-size:11px; font-weight:700; padding:3px 9px; border-radius:16px; }
.tl-count-active { background:rgba(21,154,255,0.1); color:var(--accent); }
.tl-count-idle   { background:rgba(148,163,184,0.12); color:#64748b; }

/* Lane dot indicator */
.tl-lane-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.tl-dot-active { background:var(--accent); box-shadow:0 0 0 3px rgba(21,154,255,0.18); }
.tl-dot-idle   { background:#94a3b8; box-shadow:0 0 0 3px rgba(148,163,184,0.18); }

/* Mini gantt bar inside each panel */
.tl-gantt-mini { margin-bottom:14px; }
.tl-gantt-track { position:relative; height:18px; background:var(--surface); border:1px solid var(--border); border-radius:8px; overflow:visible; margin-bottom:6px; }
.tl-gantt-bar { position:absolute; top:2px; bottom:2px; border-radius:5px; min-width:2px; }
.tl-bar-active { background:linear-gradient(180deg,#5cbdff,#0c6bb8); box-shadow:0 1px 4px rgba(21,154,255,0.4); }
.tl-bar-idle   { background:linear-gradient(180deg,#c8d3df,#8a9ab0); box-shadow:0 1px 3px rgba(0,0,0,0.1); }
.tl-now-line { position:absolute; top:-3px; bottom:-3px; width:2px; background:#ef4444; border-radius:1px; box-shadow:0 0 0 2px rgba(239,68,68,0.15); z-index:4; }
.tl-ruler { position:relative; height:12px; }
.tl-ruler span { position:absolute; top:0; transform:translateX(-50%); font-size:9px; color:var(--text-faint); font-variant-numeric:tabular-nums; white-space:nowrap; }

/* Entry rows */
.tl-entries { display:flex; flex-direction:column; gap:5px; max-height:260px; overflow-y:auto; padding-right:2px; scrollbar-width:thin; scrollbar-color:var(--border) transparent; }
.tl-entries::-webkit-scrollbar { width:3px; }
.tl-entries::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }

.tl-entry { display:flex; align-items:center; justify-content:space-between; padding:8px 11px; border-radius:9px; border:1px solid transparent; transition:transform .12s ease; }
.tl-entry:hover { transform:translateX(2px); }
.tl-entry-active { background:rgba(21,154,255,0.05); border-color:rgba(21,154,255,0.1); }
.tl-entry-idle   { background:rgba(100,116,139,0.04); border-color:rgba(100,116,139,0.1); }

.tl-entry-times { display:flex; align-items:center; gap:5px; }
.tl-t { font-size:12.5px; font-weight:600; color:var(--text); font-variant-numeric:tabular-nums; }
.tl-arrow-icon { color:var(--text-faint); flex-shrink:0; }
.tl-dur { font-size:11.5px; font-weight:700; color:var(--text-muted); background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:3px 8px; white-space:nowrap; font-variant-numeric:tabular-nums; }

.act-loading { font-size:13px; color:var(--text-muted); padding:8px 0; }
.act-empty   { font-size:13px; color:var(--text-muted); padding:8px 0; }

/* ──────── BROWSER SECTION ──────── */
.stat-cards-row { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:10px; }
.stat-card { background:var(--card); border-radius:13px; padding:14px 16px; border:1px solid var(--border); display:flex; align-items:center; gap:12px; box-shadow:var(--shadow-xs); }
.sc-icon { width:38px; height:38px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.sc-blue  { background:rgba(21,154,255,0.09); color:var(--accent); }
.sc-slate { background:rgba(100,116,139,0.09); color:#64748b; }
.sc-label { font-size:10px; color:var(--text-muted); text-transform:uppercase; letter-spacing:.05em; margin-bottom:3px; font-weight:700; }
.sc-value { font-size:22px; font-weight:700; color:var(--text); font-variant-numeric:tabular-nums; letter-spacing:-.01em; }

.domain-hint { font-size:11.5px; color:var(--text-faint); margin:-4px 0 10px; }
.domain-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
.domain-card { background:var(--card); border-radius:13px; padding:13px 15px; border:1px solid var(--border); transition:border-color .18s, box-shadow .18s; cursor:pointer; display:flex; flex-direction:column; gap:10px; box-shadow:var(--shadow-xs); }
.domain-card:hover { border-color:rgba(21,154,255,0.25); box-shadow:var(--shadow-md); }
.domain-card.is-expanded { border-color:rgba(21,154,255,0.35); box-shadow:var(--shadow-lg); cursor:default; }
.domain-card-header { display:flex; align-items:center; gap:8px; }
.domain-favicon-wrap { width:30px; height:30px; border-radius:8px; background:rgba(21,154,255,0.06); display:flex; align-items:center; justify-content:center; flex-shrink:0; overflow:hidden; }
.domain-favicon { border-radius:4px; }
.domain-favicon-fallback { width:16px; height:16px; border-radius:50%; background:var(--accent); color:#fff; font-size:9px; font-weight:700; display:flex; align-items:center; justify-content:center; }
.domain-name-block { overflow:hidden; flex:1; }
.domain-name { font-size:12.5px; font-weight:700; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:block; }
.domain-visits-count { font-size:10px; color:var(--text-faint); display:block; margin-top:1px; }
.domain-time-pill { font-size:10.5px; font-weight:700; color:var(--accent); background:rgba(21,154,255,0.08); padding:3px 8px; border-radius:10px; white-space:nowrap; flex-shrink:0; font-variant-numeric:tabular-nums; }
.domain-expand-chevron { color:var(--text-faint); opacity:.55; transition:transform .2s ease; flex-shrink:0; }
.domain-expand-chevron.rotated { transform:rotate(180deg); opacity:1; color:var(--accent); }
.domain-url-list { border-top:1px solid var(--border); padding-top:10px; margin-top:3px; }
.domain-url-table { display:flex; flex-direction:column; gap:3px; max-height:200px; overflow-y:auto; }
.domain-url-row { display:grid; grid-template-columns:1fr 1.4fr auto; gap:7px; align-items:center; padding:7px 8px; border-radius:7px; text-decoration:none; transition:background .13s; font-size:11.5px; }
.domain-url-header { font-size:9.5px; font-weight:700; color:var(--text-faint); text-transform:uppercase; letter-spacing:.05em; }
.domain-url-row:not(.domain-url-header):hover { background:rgba(21,154,255,0.06); }
.domain-url-path { color:var(--accent); font-family:'Courier New',monospace; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.domain-url-title { color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.domain-url-time { font-weight:700; color:var(--text-muted); white-space:nowrap; font-variant-numeric:tabular-nums; }
.domain-url-empty { font-size:12px; color:var(--text-muted); padding:5px 0; }

/* ──────── SCREENSHOTS ──────── */
.ss-status-bar { display:flex; align-items:center; gap:12px; padding:12px 16px; border-radius:12px; margin-bottom:16px; border:1px solid transparent; flex-wrap:wrap; box-shadow:var(--shadow-xs); }
.ss-status-ok      { background:rgba(21,154,255,0.04); border-color:rgba(21,154,255,0.18); }
.ss-status-warn    { background:rgba(100,116,139,0.04); border-color:rgba(100,116,139,0.18); }
.ss-status-error   { background:rgba(220,38,38,0.04); border-color:rgba(220,38,38,0.18); }
.ss-status-unknown { background:rgba(0,0,0,0.025); border-color:var(--border); }
.ss-status-icon-wrap { width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.ss-status-ok    .ss-status-icon-wrap { background:rgba(21,154,255,0.12); color:var(--accent); }
.ss-status-warn  .ss-status-icon-wrap { background:rgba(100,116,139,0.1); color:#64748b; }
.ss-status-error .ss-status-icon-wrap { background:rgba(220,38,38,0.09); color:#dc2626; }
.ss-status-unknown .ss-status-icon-wrap { background:var(--border); color:var(--text-muted); }
.ss-status-text { display:flex; flex-direction:column; gap:1px; flex:1; font-size:12.5px; }
.ss-status-text strong { color:var(--text); }
.ss-status-text span  { color:var(--text-muted); }
.ss-status-pills { display:flex; flex-wrap:wrap; gap:5px; }
.ss-pill { font-size:10.5px; font-weight:600; padding:3px 9px; border-radius:20px; }
.pill-ok  { background:rgba(21,154,255,0.08); color:var(--accent); border:1px solid rgba(21,154,255,0.18); }
.pill-off { background:rgba(220,38,38,0.07); color:#dc2626; border:1px solid rgba(220,38,38,0.18); }

.ss-meta-strip { display:grid; grid-template-columns:repeat(auto-fill,minmax(170px,1fr)); gap:11px; margin-bottom:20px; }
.ss-meta-card { display:flex; align-items:center; gap:12px; background:var(--card); border-radius:13px; padding:14px 16px; border:1px solid var(--border); box-shadow:var(--shadow-xs); }
.ss-meta-icon-wrap { width:38px; height:38px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.ss-meta-blue  { background:rgba(21,154,255,0.09); color:var(--accent); }
.ss-meta-slate { background:rgba(100,116,139,0.09); color:#64748b; }
.ss-meta-navy  { background:rgba(12,107,184,0.09); color:var(--accent-deep); }
.ss-meta-body { display:flex; flex-direction:column; gap:2px; flex:1; }
.ss-meta-label { font-size:10px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); font-weight:700; }
.ss-meta-value { font-size:20px; font-weight:700; color:var(--text); font-variant-numeric:tabular-nums; }
.ss-meta-total { font-size:12px; font-weight:400; color:var(--text-muted); }
.ss-meta-prog-track { width:100%; height:3px; background:rgba(21,154,255,0.08); border-radius:2px; overflow:hidden; margin-top:5px; }
.ss-meta-prog-fill { height:100%; background:linear-gradient(90deg,var(--accent-deep),var(--accent)); border-radius:2px; transition:width .6s ease; }

.ss-premium-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:11px; }
.ss-premium-card { background:var(--card); border-radius:13px; overflow:hidden; border:1px solid var(--border); cursor:pointer; transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease; position:relative; box-shadow:var(--shadow-xs); }
.ss-premium-card:hover { transform:translateY(-3px) scale(1.01); box-shadow:0 12px 30px rgba(21,154,255,0.15); border-color:rgba(21,154,255,0.32); }
.ss-badge-num { position:absolute; top:7px; left:7px; background:rgba(0,0,0,0.52); backdrop-filter:blur(6px); color:#fff; font-size:9.5px; font-weight:700; padding:3px 8px; border-radius:14px; z-index:2; }
.ss-premium-footer { display:flex; align-items:center; justify-content:space-between; padding:8px 12px; background:var(--card); border-top:1px solid var(--border); }
.ss-premium-time { font-size:11.5px; font-weight:600; color:var(--text); font-variant-numeric:tabular-nums; }
.ss-premium-hint { font-size:10px; color:var(--accent); opacity:0; transition:opacity .15s; font-weight:600; }
.ss-premium-card:hover .ss-premium-hint { opacity:1; }
.ss-thumb-wrap { position:relative; width:100%; padding-top:56.25%; background:var(--surface); overflow:hidden; }
.ss-thumb { position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; transition:transform .2s ease; }
.ss-premium-card:hover .ss-thumb { transform:scale(1.04); }
.ss-thumb-overlay { position:absolute; inset:0; background:rgba(21,154,255,0); display:flex; align-items:center; justify-content:center; transition:background .18s; }
.ss-premium-card:hover .ss-thumb-overlay { background:rgba(10,22,40,0.24); }
.ss-expand-icon { opacity:0; transition:opacity .18s; }
.ss-premium-card:hover .ss-expand-icon { opacity:1; }
.ss-placeholder .ss-thumb-wrap { background:rgba(21,154,255,0.025); border-bottom:1px dashed rgba(21,154,255,0.12); }
.ss-placeholder-inner { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:5px; }
.ss-placeholder-icon { color:var(--text-muted); opacity:.25; }
.ss-placeholder-label { font-size:10.5px; color:var(--text-muted); opacity:.45; }
.ss-num { font-size:11px; font-weight:700; color:var(--accent); background:rgba(21,154,255,0.08); padding:2px 7px; border-radius:8px; }
.ss-empty-state { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:44px; gap:12px; }
.ss-empty-title { font-size:14px; font-weight:600; color:var(--text-muted); }

/* Lightbox */
.ss-lightbox-overlay { position:fixed; inset:0; background:rgba(4,8,18,0.92); display:flex; align-items:center; justify-content:center; z-index:1000; padding:20px; backdrop-filter:blur(8px); }
.ss-lightbox-box { background:#0a1520; border-radius:16px; overflow:hidden; max-width:90vw; max-height:90vh; display:flex; flex-direction:column; box-shadow:0 48px 120px rgba(0,0,0,0.75); position:relative; border:1px solid rgba(255,255,255,0.05); }
.ss-lightbox-header { display:flex; align-items:center; justify-content:space-between; padding:14px 18px; background:rgba(255,255,255,0.03); border-bottom:1px solid rgba(255,255,255,0.06); }
.ss-lightbox-meta { display:flex; flex-direction:column; gap:2px; }
.ss-lightbox-title { font-size:13.5px; font-weight:700; color:#fff; }
.ss-lightbox-sub   { font-size:11.5px; color:#6b7c8f; }
.ss-lightbox-close { background:rgba(255,255,255,0.07); border:none; color:#fff; width:30px; height:30px; border-radius:50%; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:background .15s; }
.ss-lightbox-close:hover { background:rgba(255,255,255,0.16); }
.ss-lightbox-img-wrap { overflow:auto; max-height:calc(90vh - 76px); display:flex; align-items:flex-start; justify-content:center; }
.ss-lightbox-img { max-width:100%; height:auto; display:block; }
.ss-nav-btn { position:absolute; top:50%; transform:translateY(-50%); background:rgba(255,255,255,0.1); border:none; color:#fff; width:40px; height:40px; border-radius:50%; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:background .15s; z-index:10; }
.ss-nav-btn:hover { background:rgba(21,154,255,0.5); }
.ss-nav-prev { left:12px; }
.ss-nav-next { right:12px; }

/* ──────── MODAL ──────── */
.modal-overlay { position:fixed; inset:0; background:rgba(4,8,16,0.6); display:flex; justify-content:center; align-items:center; z-index:100; backdrop-filter:blur(5px); }
.modal-box { background:var(--card); padding:24px; border-radius:16px; box-shadow:var(--shadow-lg); display:flex; flex-direction:column; gap:12px; border:1px solid var(--border); min-width:260px; }
.modal-actions { display:flex; gap:8px; justify-content:flex-end; }

/* ──────── DARK MODE OVERRIDES ──────── */
.dark .act-type-tabs { border-color:rgba(255,255,255,0.07); }
.dark .domain-card   { border-color:rgba(255,255,255,0.055); }
.dark .member-card   { border-color:rgba(255,255,255,0.055); }
.dark .ss-premium-card { border-color:rgba(255,255,255,0.055); }
.dark .ss-premium-footer { border-top-color:rgba(255,255,255,0.045); }
.dark .tl-gantt-track { background:rgba(255,255,255,0.025); }
.dark .tl-entry-active { background:rgba(21,154,255,0.06); }
.dark .tl-entry-idle   { background:rgba(100,116,139,0.06); }
.dark .mini-cal-nav-btn { border-color:rgba(255,255,255,0.07); }
.dark .day-task-mini-item { border-color:rgba(255,255,255,0.06); }

/* ──────── RESPONSIVE ──────── */
@media screen and (max-width:1280px) {
  .desktop-bottom-grid { grid-template-columns:1fr; }
  .timeline-split-wrap { grid-template-columns:1fr 1fr; }
}
@media screen and (max-width:1100px) {
  .tasks-layout { grid-template-columns:1fr; }
  .tasks-calendar-col { position:static; flex-direction:row; flex-wrap:wrap; }
  .tasks-calendar-col .mini-cal-card { flex:1; min-width:240px; }
}
@media screen and (max-width:1024px) {
  .domain-grid { grid-template-columns:repeat(2,1fr); }
  .ss-premium-grid { grid-template-columns:repeat(3,1fr); }
}
@media screen and (max-width:800px) {
  .timeline-split-wrap { grid-template-columns:1fr; }
}
@media screen and (max-width:768px) {
  .sidebar { position:fixed; top:0; left:-260px; height:100%; margin:0; border-radius:0; transition:left .28s ease; }
  .sidebar.show { left:0; }
  .mobile-toggle { display:flex; }
  .dashboard-layout { flex-direction:column; }
  .content { padding:18px 14px; }
  .task-list { grid-template-columns:1fr; }
  .member-card-grid { grid-template-columns:1fr; }
  .desktop-stat-grid { grid-template-columns:1fr; }
  .ss-premium-grid { grid-template-columns:repeat(2,1fr); }
  .domain-grid { grid-template-columns:1fr; }
  .timeline-split-wrap { grid-template-columns:1fr; }
  .header-search { flex-direction:column; align-items:flex-start; }
  .search-wrap { max-width:100%; }
  .act-page-header { flex-direction:column; }
  .tasks-calendar-col { flex-direction:column; }
}
@media screen and (max-width:520px) {
  .task-card-footer { flex-direction:column; align-items:stretch; }
  .assign-section-compact { width:100%; }
}
</style>
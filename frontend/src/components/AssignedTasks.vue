<template>
  <div :class="['dashboard-layout', darkMode ? 'dark' : 'light']">

    <!-- ===== SIDEBAR ===== -->
    <aside :class="['sidebar', { show: sidebarOpen }]">
      <div class="user-info">
        <div class="avatar-circle">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor">
            <circle cx="12" cy="8" r="4" stroke-width="2"/>
            <path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M6 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
          </svg>
        </div>
        <span class="username">{{ userProfile.username || 'Employee' }}</span>
        <span class="user-role">{{ userProfile.email }}</span>
      </div>

      <div class="nav-group">
        <span class="nav-group-label">Workspace</span>
      </div>

      <nav class="sidebar-nav">
        <button class="nav-btn" :class="{ active: selectedTab === 'attendance' }" @click="selectedTab = 'attendance'; sidebarOpen=false">
          <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="10" stroke-width="2"/><path stroke-width="2" stroke-linecap="round" d="M12 6v6l4 2"/></svg>
          <span>Attendance</span>
        </button>
        <button class="nav-btn" :class="{ active: selectedTab === 'tasks' }" @click="selectedTab = 'tasks'; sidebarOpen=false">
          <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M9 2h6v4H9zM5 6h14v16H5z"/></svg>
          <span>Tasks</span>
        </button>
        <button class="nav-btn" :class="{ active: selectedTab === 'taskCalendar' }" @click="selectedTab = 'taskCalendar'; sidebarOpen=false">
          <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><rect x="3" y="4" width="18" height="18" rx="2" stroke-width="2"/><path stroke-width="2" stroke-linecap="round" d="M16 2v4M8 2v4M3 10h18"/></svg>
          <span>Task Calendar</span>
        </button>
        <button class="nav-btn" :class="{ active: selectedTab === 'activity' }" @click="selectedTab = 'activity'; fetchMyActivity(); sidebarOpen=false">
          <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M3 12h4l3-9 4 18 3-9h4"/></svg>
          <span>My Activity</span>
        </button>
        <button class="nav-btn" :class="{ active: selectedTab === 'globalChat' }" @click="selectedTab = 'globalChat'; sidebarOpen=false">
          <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z"/></svg>
          <span>Group Chat</span>
          <span v-if="unreadCount > 0" class="chat-badge">{{ unreadCount }}</span>
        </button>
        <button class="nav-btn" :class="{ active: selectedTab === 'profile' }" @click="selectedTab = 'profile'; sidebarOpen=false">
          <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="8" r="4" stroke-width="2"/><path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M6 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/></svg>
          <span>Profile</span>
        </button>
      </nav>

      <div class="sidebar-divider"></div>

      <button class="nav-btn logout-btn" @click="handleLogout">
        <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><rect x="5" y="11" width="14" height="10" stroke-width="2"/><path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <span>Logout</span>
      </button>

      <div class="theme-toggle">
        <label class="theme-label">
          <input type="checkbox" v-model="darkMode"/>
          <span class="theme-track"><span class="theme-thumb"></span></span>
          {{ darkMode ? 'Dark' : 'Light' }}
        </label>
      </div>
    </aside>

    <button class="mobile-toggle" @click="sidebarOpen = !sidebarOpen">
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
    </button>
    <div v-if="sidebarOpen" class="overlay" @click="sidebarOpen = false"></div>

    <!-- ===== MAIN CONTENT ===== -->
    <main class="content">

      <!-- HEADER -->
      <header class="top-header" @click="showNotifications=false">
        <div class="greeting-block">
          <h2 class="greeting">Hello, <span class="greeting-name">{{ userProfile.username }}</span></h2>
          <span class="greeting-sub">{{ new Date().toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric' }) }}</span>
        </div>

        <div class="header-right" @click.stop>
          <!-- Tracking status badge -->
          <div class="tracking-indicator" :class="{ idle: myTrackStatus.isIdle, stopped: !myTrackStatus.isTracking }">
            <span class="tracking-dot"></span>
            <span class="tracking-label">{{ trackingStatusLabel }}</span>
          </div>

          <div class="notification-bell" @click="toggleNotifications">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor">
              <path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-5-5.917V4a1 1 0 10-2 0v1.083A6 6 0 006 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1h6z"/>
            </svg>
            <span v-if="notifications.length > 0" class="notif-count blink">{{ notifications.length }}</span>
          </div>

          <div v-if="showNotifications" class="notification-panel">
            <p v-if="notifications.length === 0" class="empty-notif">No new notifications</p>
            <div v-for="(notif, index) in notifications" :key="index" class="notification-item">{{ notif }}</div>
          </div>

          <div class="avatar-circle header-avatar">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor"><circle cx="12" cy="8" r="4" stroke-width="2"/><path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M6 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/></svg>
          </div>
        </div>
      </header>

      <!-- STATS CARD -->
      <div v-if="selectedTab === 'attendance' || selectedTab === 'tasks'" class="dashboard-cards">
        <div class="stat-card">
          <div class="sc-icon sc-blue">
            <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </div>
          <div>
            <p class="sc-label">Active Hours This Week</p>
            <p class="sc-value">{{ weeklyActiveHoursFmt }}</p>
            <p class="sc-sub">{{ weeklyDateRange }}</p>
          </div>
        </div>
      </div>

      <!-- ===== PANELS ===== -->
      <div class="main-panels">

        <!-- ATTENDANCE -->
        <section v-if="selectedTab === 'attendance'" class="panel-card">
          <div class="panel-header">
            <span class="panel-title">Daily Attendance</span>
          </div>
          <div class="attendance-row">
            <div class="attendance-field">
              <label>Check-In Time</label>
              <input type="time" v-model="daily.manualCheckIn" :disabled="!canClockIn"/>
              <button class="btn-primary" @click="dailyClockIn" :disabled="!canClockIn">Check In</button>
            </div>
            <div class="attendance-field">
              <label>Check-Out Time</label>
              <input type="time" v-model="daily.manualCheckOut" :disabled="!canClockOut"/>
              <button class="btn-primary" @click="dailyClockOut" :disabled="!canClockOut">Check Out</button>
              <div class="break-controls">
                <button class="btn-outline-accent" @click="pauseWork" :disabled="isPaused || !canClockOut">Pause</button>
                <button class="btn-accent" @click="resumeWork" :disabled="!isPaused">Resume</button>
              </div>
            </div>
          </div>
          <div class="status-container">
            <span v-if="daily.clockedIn && !daily.systemCheckOut" class="status working">Working Today</span>
            <span v-if="daily.systemCheckOut" class="status done">Attendance Completed</span>
            <span v-if="!daily.clockedIn" class="status pending">Not Checked In</span>
          </div>
        </section>

        <!-- TASKS -->
        <section v-if="selectedTab === 'tasks'" class="tasks-layout">
          <div class="panel-card tasks-main-col">
            <div class="panel-header"><span class="panel-title">Your Assigned Tasks</span></div>
            <ul v-if="tasks.length" class="task-grid task-grid-compact task-grid-scroll">
              <li v-for="task in tasks" :key="task.id" class="task-card task-card-compact">
                <div class="task-header">
                  <strong class="task-title">{{ task.title }}</strong>
                  <span class="status" :class="task.status">{{ task.status.replace('_',' ') }}</span>
                </div>
                <div class="task-desc-card">
                  <p class="desc">{{ task.description }}</p>
                  <p class="task-meta"><strong>Start:</strong> {{ formatDate(task.start_date) }} &nbsp;·&nbsp; <strong>End:</strong> {{ formatDate(task.end_date) }}</p>
                </div>
                <div v-if="task.attachment_url" class="task-attachment">
                  <a :href="task.attachment_url" target="_blank" download>Download Attachment</a>
                </div>
                <select v-model="task.status" @change="updateTaskStatus(task)" class="status-select">
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="complete">Complete</option>
                </select>
                <button class="comment-toggle-btn" @click="toggleComments(task.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8-1.64 0-3.173-.4-4.5-1.1L3 21l1.1-4.5C3.4 15.173 3 13.64 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
                  <span>{{ openComments[task.id] ? 'Hide Comments' : 'Show Comments' }}</span>
                  <svg class="comment-toggle-chevron" :class="{ rotated: openComments[task.id] }" xmlns="http://www.w3.org/2000/svg" width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                </button>
                <div class="comment-box" v-if="openComments[task.id]">
                  <CommentListCreate :taskId="task.id" :current-user="userProfile.username" @refresh="fetchTasks"/>
                </div>
              </li>
            </ul>
            <div class="empty-state" v-else>
              <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="opacity:.3"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m-6-8h6M5 6h14M5 18h14"/></svg>
              <p>No assigned tasks.</p>
            </div>
          </div>

          <!-- Calendar side -->
          <div class="panel-card tasks-calendar-col">
            <div class="panel-header"><span class="panel-title">Task Calendar</span></div>
            <div class="calendar-controls calendar-controls-stacked">
              <label>Select Date:</label>
              <input type="date" v-model="selectedDate" @change="filterTasksByDate"/>
            </div>
            <div class="calendar-grid calendar-grid-mini">
              <div class="calendar-day header" v-for="day in weekdays" :key="day">{{ day.slice(0,1) }}</div>
              <div class="calendar-day blank" v-for="n in firstDayOffset" :key="'blank-side-'+n"></div>
              <div v-for="day in daysInMonth" :key="day" class="calendar-day" :class="{ today: isToday(day), selected: isSelected(day) }" @click="selectCalendarDay(day)">
                <div class="day-number">{{ day }}</div>
                <div class="events">
                  <div v-for="task in tasksByDate(day)" :key="task.id" class="event" :class="task.status"></div>
                </div>
              </div>
            </div>
            <ul class="task-list task-list-mini">
              <li v-for="task in filteredTasks" :key="task.id">
                <h3>{{ task.title }} <span class="status" :class="task.status">{{ task.status.replace('_',' ') }}</span></h3>
                <p><strong>Start:</strong> {{ formatDate(task.start_date) }} · <strong>End:</strong> {{ formatDate(task.end_date) }}</p>
              </li>
              <li v-if="!filteredTasks.length" class="task-list-empty">No tasks on this date.</li>
            </ul>
          </div>
        </section>

        <!-- TASK CALENDAR full page -->
        <section v-if="selectedTab === 'taskCalendar'" class="panel-card">
          <div class="panel-header">
            <span class="panel-title">Task Calendar</span>
            <div class="calendar-controls">
              <label>Select Date:</label>
              <input type="date" v-model="selectedDate" @change="filterTasksByDate"/>
            </div>
          </div>
          <div class="calendar-grid">
            <div class="calendar-day header" v-for="day in weekdays" :key="day">{{ day }}</div>
            <div class="calendar-day blank" v-for="n in firstDayOffset" :key="'blank-'+n"></div>
            <div v-for="day in daysInMonth" :key="day" class="calendar-day" :class="{ today: isToday(day), selected: isSelected(day) }" @click="selectCalendarDay(day)">
              <div class="day-number">{{ day }}</div>
              <div class="events">
                <div v-for="task in tasksByDate(day)" :key="task.id" class="event" :class="task.status" :title="task.title">{{ task.title }}</div>
              </div>
            </div>
          </div>
          <ul class="task-list">
            <li v-for="task in filteredTasks" :key="task.id">
              <h3>{{ task.title }} <span class="status" :class="task.status">{{ task.status.replace('_',' ') }}</span></h3>
              <p>{{ task.description }}</p>
              <p><strong>Start:</strong> {{ formatDate(task.start_date) }} | <strong>End:</strong> {{ formatDate(task.end_date) }}</p>
            </li>
            <li v-if="!filteredTasks.length" class="task-list-empty">No tasks on this date.</li>
          </ul>
        </section>

        <!-- ===== MY ACTIVITY TAB ===== -->
        <section v-if="selectedTab === 'activity'" class="panel-card activity-section">
          <div class="panel-header">
            <span class="panel-title">My Activity</span>
          </div>

          <!-- Read-only tracking status banner -->
          <div class="tracking-status-banner" :class="myTrackStatus.isTracking ? (myTrackStatus.isIdle ? 'banner-idle' : 'banner-active') : 'banner-stopped'">
            <span class="banner-dot"></span>
            <span class="banner-text">{{ trackingBannerText }}</span>
          </div>

          <!-- Desktop / Browser tab switcher -->
          <div class="act-type-tabs">
            <button class="act-type-tab" :class="{ active: activityTab === 'desktop' }" @click="activityTab = 'desktop'">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
              Desktop
            </button>
            <button class="act-type-tab" :class="{ active: activityTab === 'browser' }" @click="activityTab = 'browser'; fetchBrowserActivity()">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/></svg>
              Browser
            </button>
          </div>

          <div class="activity-date-row">
            <label>Date:</label>
            <input type="date" v-model="activityDate" @change="onActivityDateChange"/>
            <button class="btn-ghost" @click="onActivityDateChange">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              Refresh
            </button>
          </div>

          <div v-if="activityLoading" class="act-loading">Loading…</div>

          <template v-else>

            <div class="act-live-note" v-if="activityDate === todayDate">
              <span class="act-live-dot"></span> Live — updates automatically
            </div>

            <!-- ===== DESKTOP TAB ===== -->
            <template v-if="activityTab === 'desktop'">

              <!-- Only show stats when there is actual data -->
              <template v-if="hasDesktopData">
                <div class="emp-stat-grid">
                  <div class="dsg-card dsg-active">
                    <div class="dsg-icon"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg></div>
                    <div class="dsg-body">
                      <span class="dsg-label">Active</span>
                      <span class="dsg-value">{{ displayActiveFmt }}</span>
                    </div>
                  </div>
                  <div class="dsg-card dsg-idle">
                    <div class="dsg-icon"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg></div>
                    <div class="dsg-body">
                      <span class="dsg-label">Idle</span>
                      <span class="dsg-value">{{ displayIdleFmt }}</span>
                    </div>
                  </div>
                  <div class="dsg-card dsg-pct">
                    <div class="dsg-icon"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg></div>
                    <div class="dsg-body" style="flex:1;">
                      <span class="dsg-label">Active %</span>
                      <div class="dsg-pct-row">
                        <span class="dsg-value">{{ displayActivePct }}%</span>
                        <div class="dsg-pct-bar-wrap"><div class="dsg-pct-bar" :style="{ width: displayActivePct + '%' }"></div></div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- App donut + timeline -->
                <div class="emp-bottom-grid" v-if="appBreakdown.length || activityPeriods.length">
                  <div v-if="appBreakdown.length" class="panel-card emp-donut-card">
                    <div class="panel-header"><span class="panel-title">App Usage</span></div>
                    <div class="app-donut-layout">
                      <svg class="app-donut-svg" viewBox="0 0 140 140" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="70" cy="70" r="48" fill="none" stroke="rgba(0,0,0,0.05)" stroke-width="18"/>
                        <circle v-for="(app, i) in appBreakdown.slice(0,6)" :key="app.app+'_eseg'" cx="70" cy="70" r="48" fill="none" :stroke="donutShade(i)" stroke-width="18" stroke-linecap="butt" :stroke-dasharray="_appDonutDash(app.seconds, i)" :stroke-dashoffset="_appDonutOffset(i)" style="transition:all 0.7s ease;"/>
                        <circle cx="70" cy="70" r="39" fill="var(--card)"/>
                        <text x="70" y="66" text-anchor="middle" font-size="16" font-weight="700" fill="var(--text)" font-family="Poppins,sans-serif">{{ appBreakdown.length }}</text>
                        <text x="70" y="80" text-anchor="middle" font-size="7.5" fill="var(--text-muted)" font-family="Poppins,sans-serif">APPS</text>
                      </svg>
                      <div class="app-donut-legend">
                        <div v-for="(app, i) in appBreakdown.slice(0,6)" :key="app.app+'_legend'" class="donut-legend-row">
                          <span class="donut-legend-dot" :style="{ background: donutShade(i) }"></span>
                          <span class="donut-legend-name">{{ app.app }}</span>
                          <span class="donut-legend-time">{{ app.duration }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-if="activityPeriods.length" class="panel-card emp-timeline-card">
                    <div class="panel-header"><span class="panel-title">Active / Idle Timeline</span></div>
                    <div class="act-period-list">
                      <div v-for="(p, i) in activityPeriods" :key="i" class="tl-entry" :class="p.type === 'active' ? 'tl-entry-active' : 'tl-entry-idle'">
                        <span class="tl-count-badge" :class="p.type === 'active' ? 'tl-count-active' : 'tl-count-idle'">{{ p.type === 'active' ? 'Active' : 'Idle' }}</span>
                        <span class="tl-entry-times">
                          <span class="tl-t">{{ p.from }}</span>
                          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="tl-arrow-icon"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                          <span class="tl-t">{{ p.to }}</span>
                        </span>
                        <span class="tl-dur">{{ p.duration }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </template>

              <!-- No data state -->
              <div v-else class="act-empty">No activity recorded for {{ activityDate }}.</div>

              <!-- 7-DAY HISTORY always shown if available -->
              <div v-if="activityHistory.length" class="act-history-section">
                <h3 class="section-label">Last 7 days</h3>
                <div class="attendance-card">
                  <table class="history-table">
                    <thead>
                      <tr><th>Date</th><th>Active</th><th>Idle</th><th>Active %</th></tr>
                    </thead>
                    <tbody>
                      <tr v-for="row in activityHistory" :key="row.date">
                        <td>{{ row.date }}</td>
                        <td><span class="time-chip time-chip-accent">{{ row.active_time_formatted }}</span></td>
                        <td><span class="time-chip">{{ row.idle_time_formatted }}</span></td>
                        <td>
                          <div class="hist-pct-wrap">
                            <div class="hist-pct-track"><div class="hist-pct-bar" :style="{ width: row.active_percentage + '%' }"></div></div>
                            <span>{{ row.active_percentage }}%</span>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </template>

            <!-- ===== BROWSER TAB ===== -->
            <template v-if="activityTab === 'browser'">
              <div v-if="browserLoading" class="act-loading">Loading browser activity…</div>
              <div v-else-if="browserActivity">
                <div class="emp-stat-grid emp-stat-grid-2">
                  <div class="dsg-card dsg-active">
                    <div class="dsg-icon"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg></div>
                    <div class="dsg-body">
                      <span class="dsg-label">Total Browsing</span>
                      <span class="dsg-value">{{ browserActivity.total_browser || '0m' }}</span>
                    </div>
                  </div>
                  <div class="dsg-card dsg-idle">
                    <div class="dsg-icon"><svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/></svg></div>
                    <div class="dsg-body">
                      <span class="dsg-label">Sites Visited</span>
                      <span class="dsg-value">{{ browserActivity.domain_breakdown ? browserActivity.domain_breakdown.length : 0 }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="browserActivity.domain_breakdown && browserActivity.domain_breakdown.length">
                  <h4 class="section-label" style="margin:16px 0 8px;">Time per Website</h4>
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
                            <div class="domain-url-row domain-url-header"><span>Path</span><span>Title</span><span>Time</span></div>
                            <a v-for="v in domainVisits(site.domain)" :key="v.id" :href="v.url || '#'" target="_blank" rel="noopener" class="domain-url-row">
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
            </template>

          </template>
        </section>

        <!-- GLOBAL CHAT -->
        <section v-if="selectedTab === 'globalChat'" class="panel-card">
          <div class="chat-page-header">
            <span class="panel-title">Group Chat</span>
            <button class="btn-danger btn-sm" @click="clearChat">Clear</button>
          </div>
          <div class="chat-container">
            <div class="chat-messages">
              <div v-for="msg in messages" :key="msg.id" :class="['chat-msg', msg.sender_username === userProfile.username ? 'self' : 'other']">
                <span class="chat-sender">{{ msg.sender_username }}</span>
                <span class="chat-bubble">{{ msg.message }}</span>
                <span class="chat-time">{{ formatDateTime(msg.created_at) }}</span>
              </div>
            </div>
            <div class="chat-input-wrap">
              <input type="text" v-model="newMessage" placeholder="Type your message..." @keyup.enter="sendMessage">
              <button class="btn-primary" @click="sendMessage">
                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
              </button>
            </div>
          </div>
        </section>

        <!-- PROFILE -->
        <section v-if="selectedTab === 'profile'" class="panel-card">
          <div class="panel-header"><span class="panel-title">Profile</span></div>
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
              <input v-model="userProfile.password" type="password" placeholder="Leave blank to keep current"/>
            </div>
            <button class="btn-primary" @click="updateUserProfile">Save Changes</button>
          </div>
        </section>

      </div>

      <!-- INFO MODAL -->
      <div class="modal-overlay" v-if="infoModal.show" @click.self="closeInfoModal">
        <div class="modal-box info-modal" :class="'info-modal-' + infoModal.variant">
          <div class="info-modal-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </div>
          <h3>{{ infoModal.title }}</h3>
          <p>{{ infoModal.message }}</p>
          <div class="modal-actions">
            <button class="btn-primary" @click="closeInfoModal">OK</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from "axios"
import CommentListCreate from "./CommentListCreate.vue"

const API_BASE = import.meta.env.VITE_API_URL

const DONUT_SHADES = ["#159aff","#0c6bb8","#5fb6ff","#3c4a5e","#9aa5b1","#1a2a3a","#bcd9f5","#6b7280"]
function donutShade(i) { return DONUT_SHADES[i % DONUT_SHADES.length] }

export default {
  name: "EmployeeDashboard",
  components: { CommentListCreate },

  data() {
    return {
      selectedTab: "attendance",
      sidebarOpen: false,
      darkMode: false,
      tasks: [],
      isPaused: false,
      infoModal: { show: false, title: "", message: "", variant: "success" },
      daily: {
        manualCheckIn: "",
        manualCheckOut: "",
        clockedIn: false,
        systemCheckIn: null,
        systemCheckOut: null,
      },
      userProfile: { username: "", email: "", password: "" },
      messages: [],
      newMessage: "",
      unreadCount: 0,
      notifications: [],
      showNotifications: false,
      _tasksLoadedOnce: false,
      _chatLoadedOnce: false,

      // Calendar
      selectedDate: new Date().toISOString().split("T")[0],
      weekdays: ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],
      daysInMonth: [],
      firstDayOffset: 0,
      filteredTasks: [],
      openComments: {},

      // Activity
      activityTab: "desktop",
      activityDate: new Date().toISOString().split("T")[0],
      // Raw seconds from backend
      activityActiveSeconds: 0,
      activityIdleSeconds: 0,
      activityActivePct: 0,
      activityPeriods: [],
      appBreakdown: [],
      activityHistory: [],
      activityLoading: false,

      browserActivity: null,
      browserLoading: false,
      expandedDomain: null,

      // Tracking status (read-only, from backend)
      myTrackStatus: { isTracking: false, isIdle: false },
      statusPollInterval: null,
      activityPollInterval: null,

      // Intervals
      chatInterval:     null,
      reminderInterval: null,
      tasksInterval:    null,
    }
  },

  computed: {
    todayDate() { return new Date().toISOString().split("T")[0] },

    canClockIn()  { return !(this.daily.clockedIn || this.daily.systemCheckIn) },
    canClockOut() {
      return !!(this.daily.clockedIn || this.daily.systemCheckIn) && !this.daily.systemCheckOut
    },

    trackingStatusLabel() {
      if (!this.myTrackStatus.isTracking) return 'Offline'
      return this.myTrackStatus.isIdle ? 'Idle' : 'Active'
    },
    trackingBannerText() {
      if (!this.myTrackStatus.isTracking) return 'Tracking offline — make sure the desktop tracker is running.'
      if (this.myTrackStatus.isIdle) return 'Currently idle — no input detected recently.'
      return 'Tracking active — your activity is being recorded automatically.'
    },

    // Whether there is any desktop data to show
    hasDesktopData() {
      return this.activityActiveSeconds > 0 || this.activityIdleSeconds > 0
    },

    displayActiveSeconds() { return this.activityActiveSeconds },
    displayIdleSeconds()   { return this.activityIdleSeconds },
    displayActiveFmt()     { return this._fmtSec(this.activityActiveSeconds) },
    displayIdleFmt()       { return this._fmtSec(this.activityIdleSeconds) },
    displayActivePct()     { return this.activityActivePct },

    // Weekly hours from history (last 7 days with data)
    weeklyActiveSeconds() {
      if (!this.activityHistory.length) return 0
      return this.activityHistory.reduce((sum, row) => {
        const s = typeof row.total_active_seconds === 'number'
          ? row.total_active_seconds
          : this._parseDurationToSeconds(row.active_time_formatted)
        return sum + s
      }, 0)
    },
    weeklyActiveHoursFmt() {
      const s = this.weeklyActiveSeconds
      if (!s) return '0h'
      const h = Math.floor(s / 3600)
      const m = Math.floor((s % 3600) / 60)
      return m > 0 ? `${h}h ${m}m` : `${h}h`
    },
    weeklyDateRange() {
      if (!this.activityHistory.length) return ''
      const dates = this.activityHistory.map(r => r.date).filter(Boolean).sort()
      if (!dates.length) return ''
      return `${dates[0]} → ${dates[dates.length - 1]}`
    },
  },

  mounted() {
    this.initDashboard()
    this.generateCalendar()
  },

  beforeUnmount() {
    clearInterval(this.chatInterval)
    clearInterval(this.reminderInterval)
    clearInterval(this.statusPollInterval)
    clearInterval(this.activityPollInterval)
    clearInterval(this.tasksInterval)
    document.removeEventListener("click", this.hideNotifications)
  },

  methods: {
    donutShade(i) { return donutShade(i) },

    // ── BOOTSTRAP ──
    async initDashboard() {
      await this.fetchUserProfile()
      this.fetchTasks()
      this.fetchDailyAttendance()
      this.fetchChatMessages()
      this.fetchMyActivity()
      this.fetchActivityHistory()
      this.fetchMyTrackStatus()

      this.chatInterval        = setInterval(this.fetchChatMessages, 3000)
      this.reminderInterval    = setInterval(this.checkReminders, 60000)
      this.statusPollInterval  = setInterval(this.fetchMyTrackStatus, 30000)
      this.tasksInterval       = setInterval(this.fetchTasks, 30000)
      // Auto-refresh activity when on today's date
      this.activityPollInterval = setInterval(() => {
        if (this.selectedTab === 'activity' && this.activityDate === this.todayDate) {
          this.fetchMyActivity()
        }
      }, 60000)

      document.addEventListener("click", this.hideNotifications)
    },

    // ── API HELPER ──
    async apiCall(method, url, data = null) {
      try {
        const token  = localStorage.getItem("access")
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
        console.error("API error:", url, err.response?.status, err.response?.data || err)
        throw err
      }
    },

    // ── TRACKING STATUS ──
    async fetchMyTrackStatus() {
      try {
        const data = await this.apiCall("get", "activity/my-status/")
        this.myTrackStatus = {
          isTracking: !!data.is_tracking,
          isIdle:     !!data.is_idle,
        }
      } catch (err) {
        // endpoint may not exist yet — fail quietly
      }
    },

    // ── ACTIVITY ──
    onActivityDateChange() {
      this.fetchMyActivity()
      if (this.activityTab === 'browser') this.fetchBrowserActivity()
    },

    async fetchMyActivity() {
      this.activityLoading = true
      this.activityActiveSeconds = 0
      this.activityIdleSeconds   = 0
      this.activityActivePct     = 0
      this.activityPeriods       = []
      this.appBreakdown          = []
      try {
        // Uses my-activity/ endpoint (employee-safe, returns raw seconds + timeline)
        const data = await this.apiCall("get", `my-activity/?date=${this.activityDate}`)

        this.activityActiveSeconds = data.total_active_seconds || 0
        this.activityIdleSeconds   = data.total_idle_seconds   || 0
        this.activityActivePct     = data.active_pct           || 0
        this.appBreakdown          = data.app_breakdown        || []
        this.activityPeriods       = this._buildPeriodsFromTimeline(data.timeline || [])
      } catch (err) {
        console.error("Activity fetch error:", err)
      } finally {
        this.activityLoading = false
      }
    },

    async fetchActivityHistory() {
      try {
        const data           = await this.apiCall("get", "activity/history/?days=7")
        this.activityHistory = data.history || []
      } catch (err) {
        console.error("History fetch error:", err)
      }
    },

    async fetchBrowserActivity() {
      this.browserLoading  = true
      this.browserActivity = null
      this.expandedDomain  = null
      try {
        // Uses my-browser-activity/ — employee-safe endpoint
        const data = await this.apiCall("get", `my-browser-activity/?date=${this.activityDate}`)
        this.browserActivity = data
      } catch (err) {
        console.error("Browser activity fetch error:", err)
        this.browserActivity = { total_browser: '0m', domain_breakdown: [], visits: [] }
      } finally {
        this.browserLoading = false
      }
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

    // ── APP DONUT HELPERS ──
    _appDonutCircumference() { return 2 * Math.PI * 48 },
    _appDonutTotalSeconds()  { return this.appBreakdown.slice(0,6).reduce((s, a) => s + (a.seconds || 0), 0) },
    _appDonutDash(seconds, index) {
      const circ  = this._appDonutCircumference()
      const total = this._appDonutTotalSeconds()
      if (!total) return `0 ${circ}`
      return `${(seconds / total) * circ} ${circ - (seconds / total) * circ}`
    },
    _appDonutOffset(index) {
      const circ = this._appDonutCircumference()
      let offset = -(circ / 4)
      const total = this._appDonutTotalSeconds()
      for (let i = 0; i < index; i++) {
        offset -= total ? ((this.appBreakdown[i].seconds || 0) / total) * circ : 0
      }
      return offset
    },

    // ── PERIOD BUILDER (uses from_time/to_time from my-activity/ timeline) ──
    _buildPeriodsFromTimeline(timeline) {
      if (!timeline?.length) return []
      const periods = []
      let current = null
      timeline.forEach(row => {
        const type = row.type === 'idle' ? 'idle' : 'active'
        if (!current || current.type !== type) {
          if (current) periods.push(current)
          current = { type, from: row.from_time, to: row.to_time, seconds: row.seconds, duration: row.duration }
        } else {
          current.to      = row.to_time
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
    _parseDurationToSeconds(str) {
      if (!str) return 0
      const hMatch = str.match(/(\d+)\s*h/)
      const mMatch = str.match(/(\d+)\s*m/)
      return (hMatch ? parseInt(hMatch[1]) : 0) * 3600 + (mMatch ? parseInt(mMatch[1]) : 0) * 60
    },

    // ── TASKS ──
    async fetchTasks() {
      const previousIds  = new Set(this.tasks.map(t => t.id))
      const isFirstLoad  = !this._tasksLoadedOnce
      this.tasks         = await this.apiCall("get", "assigned-tasks/")
      this.taskReminder(previousIds, isFirstLoad)
      this._tasksLoadedOnce = true
      this.filterTasksByDate()
    },
    async updateTaskStatus(task) {
      await this.apiCall("patch", `task-status/${task.id}/breakdown/`, { status: task.status })
      this.filterTasksByDate()
    },

    // ── ATTENDANCE ──
    // FIX: uses my-attendance/ (employee-safe) instead of attendance/ (lead-only)
    async fetchDailyAttendance() {
      try {
        const list  = await this.apiCall("get", "my-attendance/")
        const today = this.todayDate
        const record = list.find(r => (r.date || '').split('T')[0] === today)
        if (record) {
          this.daily.systemCheckIn  = record.system_check_in  || null
          this.daily.systemCheckOut = record.system_check_out || null
          this.daily.clockedIn      = !!(record.system_check_in || record.manual_check_in)
          const openBreak = (record.breaks || []).find(b => b.start && !b.end)
          this.isPaused = !!openBreak
        } else {
          this.daily.systemCheckIn  = null
          this.daily.systemCheckOut = null
          this.daily.clockedIn      = false
          this.isPaused             = false
        }
        this.checkAttendanceReminder()
      } catch (err) {
        console.error("Attendance fetch error:", err)
      }
    },

    async dailyClockIn() {
      if (!this.daily.manualCheckIn) {
        this.showInfoModal("Time Required", "Please select a check-in time.", "error")
        return
      }
      try {
        await this.apiCall("post", "attendance/check-in/", {
          manual_check_in: this.daily.manualCheckIn + ":00"
        })
        this.showInfoModal("Checked In", "You have successfully checked in for today.", "success")
        await this.fetchDailyAttendance()
      } catch (err) {
        const msg = err.response?.data?.error || err.response?.data?.detail || "Could not check in."
        this.showInfoModal("Check-In Failed", msg, "error")
      }
    },

    async dailyClockOut() {
      if (!this.daily.manualCheckOut) {
        this.showInfoModal("Time Required", "Please select a check-out time.", "error")
        return
      }
      try {
        await this.apiCall("post", "attendance/check-out/", {
          manual_check_out: this.daily.manualCheckOut + ":00"
        })
        this.showInfoModal("Checked Out", "You have successfully checked out for today.", "success")
        await this.fetchDailyAttendance()
      } catch (err) {
        const msg = err.response?.data?.error || err.response?.data?.detail || "Could not check out."
        this.showInfoModal("Check-Out Failed", msg, "error")
      }
    },

    async pauseWork() {
      try {
        await this.apiCall("post", "attendance/pause/")
        this.isPaused = true
      } catch (err) {
        const msg = err.response?.data?.error || err.response?.data?.detail || "Cannot start break."
        this.showInfoModal("Break Error", msg, "error")
      }
    },
    async resumeWork() {
      try {
        await this.apiCall("post", "attendance/resume/")
        this.isPaused = false
      } catch (err) {
        const msg = err.response?.data?.error || err.response?.data?.detail || "Cannot resume work."
        this.showInfoModal("Resume Error", msg, "error")
      }
    },

    // ── CHAT ──
    async fetchChatMessages() {
      try {
        const data  = await this.apiCall("get", "group-chat/")
        const fresh = Array.isArray(data) ? data : (data.results || [])
        const isFirstLoad = !this._chatLoadedOnce

        if (!isFirstLoad) {
          const previousIds = new Set(this.messages.map(m => m.id))
          fresh
            .filter(m => !previousIds.has(m.id) && m.sender_username !== this.userProfile.username)
            .forEach(m => this.pushNotification(`New message from ${m.sender_username}: ${this._truncate(m.message, 60)}`))
        }

        this.messages      = fresh
        this._chatLoadedOnce = true
        // unreadCount: messages from others when not in chat tab
        this.unreadCount   = this.selectedTab !== 'globalChat'
          ? fresh.filter(m => m.sender_username !== this.userProfile.username).length
          : 0
      } catch (err) {
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

    // ── PROFILE ──
    async fetchUserProfile() {
      try {
        const data             = await this.apiCall("get", "me/")
        this.userProfile.username = data.username || ""
        this.userProfile.email    = data.email    || ""
        this.userProfile.password = ""
      } catch (err) { console.error("Profile fetch error:", err) }
    },
    async updateUserProfile() {
      try {
        const payload = { username: this.userProfile.username, email: this.userProfile.email }
        if (this.userProfile.password) payload.password = this.userProfile.password
        await this.apiCall("patch", "me/update/", payload)
        alert("Profile updated successfully")
        this.userProfile.password = ""
        await this.fetchUserProfile()
      } catch (err) {
        alert(err.response?.data?.error || "Failed to update profile")
      }
    },

    // ── CALENDAR ──
    generateCalendar() {
      const date  = new Date(this.selectedDate)
      const year  = date.getFullYear()
      const month = date.getMonth()
      const days  = new Date(year, month + 1, 0).getDate()
      this.daysInMonth    = Array.from({ length: days }, (_, i) => i + 1)
      this.firstDayOffset = new Date(year, month, 1).getDay()
    },
    filterTasksByDate() {
      const d = this.selectedDate
      this.filteredTasks = this.tasks.filter(t => t.start_date <= d && t.end_date >= d)
    },
    isToday(day) {
      const today = new Date()
      const d     = new Date(this.selectedDate)
      return today.getDate() === day && today.getMonth() === d.getMonth() && today.getFullYear() === d.getFullYear()
    },
    isSelected(day) { return new Date(this.selectedDate).getDate() === day },
    tasksByDate(day) {
      const d      = new Date(this.selectedDate)
      const target = new Date(d.getFullYear(), d.getMonth(), day).toISOString().split("T")[0]
      return this.tasks.filter(t => t.start_date <= target && t.end_date >= target)
    },
    selectCalendarDay(day) {
      const d = new Date(this.selectedDate)
      this.selectedDate = new Date(d.getFullYear(), d.getMonth(), day).toISOString().split("T")[0]
      this.filterTasksByDate()
    },
    toggleComments(taskId) { this.openComments[taskId] = !this.openComments[taskId] },

    // ── MISC ──
    handleLogout() { localStorage.clear(); this.$router.push("/login") },
    formatDate(dateStr)     { return dateStr ? new Date(dateStr).toLocaleDateString() : "-" },
    formatDateTime(dateStr) { return dateStr ? new Date(dateStr).toLocaleString()     : "-" },
    toggleNotifications()   { this.showNotifications = !this.showNotifications },
    hideNotifications()     { this.showNotifications = false },

    // ── NOTIFICATIONS ──
    pushNotification(text) {
      if (this.notifications[0] === text) return
      this.notifications.unshift(text)
      if (this.notifications.length > 20) this.notifications.pop()
    },
    _truncate(str, maxLen) { return str?.length > maxLen ? str.slice(0, maxLen) + '…' : str || '' },

    taskReminder(previousIds, isFirstLoad) {
      if (isFirstLoad || !previousIds) return
      this.tasks
        .filter(t => !previousIds.has(t.id))
        .forEach(t => this.pushNotification(`New task assigned: "${t.title}"`))
    },
    checkReminders() {
      const today = this.todayDate
      this.tasks.forEach(t => {
        if (t.status === 'complete' || !t.end_date) return
        if (t.end_date.split('T')[0] === today) this.pushNotification(`Task "${t.title}" is due today`)
      })
    },
    checkAttendanceReminder() {
      if (this.daily.clockedIn && !this.daily.systemCheckOut && new Date().getHours() >= 18) {
        this.pushNotification("Don't forget to check out for today.")
      }
    },

    // ── MODAL ──
    showInfoModal(title, message, variant = "success") { this.infoModal = { show: true, title, message, variant } },
    closeInfoModal() { this.infoModal.show = false },
  }
}
</script>

<style scoped>
/* QRM EMPLOYEE DASHBOARD */
* { font-family:'Poppins',sans-serif; box-sizing:border-box; margin:0; padding:0; }

.light {
  --bg:#edf0f5; --surface:#f6f8fb; --card:#ffffff; --text:#121c2d;
  --text-muted:#64748b; --text-faint:#94a3b8; --border:rgba(15,23,42,0.07);
  --border-mid:rgba(15,23,42,0.11); --accent:#159aff; --accent-deep:#0c6bb8;
  --shadow-xs:0 1px 2px rgba(16,24,40,0.05); --shadow-sm:0 1px 3px rgba(16,24,40,0.06);
  --shadow-md:0 4px 16px rgba(16,24,40,0.07); --shadow-lg:0 20px 48px rgba(16,24,40,0.10);
  --sidebar-bg:linear-gradient(175deg,#0a1525 0%,#0f1e34 50%,#0b1828 100%);
}
.dark {
  --bg:#080d15; --surface:#0d1420; --card:#111825; --text:#e8edf5;
  --text-muted:#7b8fa8; --text-faint:#4a5568; --border:rgba(255,255,255,0.065);
  --border-mid:rgba(255,255,255,0.10); --accent:#159aff; --accent-deep:#0c6bb8;
  --shadow-xs:0 1px 2px rgba(0,0,0,0.35); --shadow-sm:0 1px 3px rgba(0,0,0,0.4);
  --shadow-md:0 6px 20px rgba(0,0,0,0.4); --shadow-lg:0 24px 64px rgba(0,0,0,0.55);
  --sidebar-bg:linear-gradient(175deg,#050a12 0%,#0a1220 50%,#060c18 100%);
}

.dashboard-layout { display:flex; min-height:100vh; background:var(--bg); transition:background .3s; }

/* SIDEBAR */
.sidebar { width:230px; margin:12px; border-radius:20px; padding:20px 14px 16px; color:#fff; background:var(--sidebar-bg); box-shadow:0 20px 60px rgba(5,12,24,0.5),inset 0 1px 0 rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.045); display:flex; flex-direction:column; gap:4px; position:relative; z-index:11; flex-shrink:0; }
.user-info { display:flex; flex-direction:column; align-items:center; padding-bottom:16px; margin-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.06); }
.avatar-circle { width:42px; height:42px; border-radius:50%; margin-bottom:8px; display:flex; align-items:center; justify-content:center; background:rgba(21,154,255,0.16); color:#9bd2ff; border:2px solid rgba(21,154,255,0.5); box-shadow:0 0 0 4px rgba(21,154,255,0.1); flex-shrink:0; }
.username { font-weight:700; font-size:12.5px; color:#f0f4fa; text-align:center; }
.user-role { font-size:10.5px; color:rgba(255,255,255,0.4); margin-top:2px; font-weight:500; text-align:center; word-break:break-all; }
.nav-group { padding:4px 4px 2px; }
.nav-group-label { font-size:9.5px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:rgba(255,255,255,0.28); }
.sidebar-nav { display:flex; flex-direction:column; gap:4px; }
.nav-btn { border:none; background:transparent; color:rgba(255,255,255,0.55); padding:9px 10px; border-radius:10px; font-size:12.5px; font-weight:500; cursor:pointer; text-align:left; transition:all .16s; display:flex; align-items:center; gap:9px; width:100%; position:relative; }
.nav-btn.active { background:rgba(21,154,255,0.14); color:#fff; box-shadow:inset 3px 0 0 #159aff; }
.nav-btn:hover:not(.active) { background:rgba(255,255,255,0.055); color:rgba(255,255,255,0.85); }
.icon { width:16px; height:16px; flex-shrink:0; }
.chat-badge { background:#dc2626; color:#fff; font-size:9.5px; font-weight:700; padding:1px 6px; border-radius:20px; margin-left:auto; }
.sidebar-divider { height:1px; background:rgba(255,255,255,0.06); margin:8px 0; }
.logout-btn { color:rgba(255,107,107,0.85); }
.logout-btn:hover { background:rgba(220,38,38,0.12); color:#ff8787; }
.theme-toggle { margin-top:10px; }
.theme-label { display:flex; align-items:center; gap:8px; font-size:11px; color:rgba(255,255,255,0.42); cursor:pointer; }
.theme-label input { display:none; }
.theme-track { width:28px; height:16px; border-radius:8px; background:rgba(255,255,255,0.1); position:relative; transition:background .2s; flex-shrink:0; }
.theme-label input:checked + .theme-track { background:rgba(21,154,255,0.6); }
.theme-thumb { position:absolute; top:2px; left:2px; width:12px; height:12px; border-radius:50%; background:#fff; transition:transform .2s; }
.theme-label input:checked + .theme-track .theme-thumb { transform:translateX(12px); }

/* MAIN */
.content { flex:1; padding:24px 32px; color:var(--text); display:flex; flex-direction:column; gap:16px; overflow:auto; min-width:0; }
.mobile-toggle { display:none; position:fixed; top:14px; left:14px; z-index:200; background:var(--accent); color:#fff; border:none; padding:9px; border-radius:10px; cursor:pointer; }
.overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.45); z-index:10; }

/* HEADER */
.top-header { display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; }
.greeting-block { display:flex; flex-direction:column; gap:2px; }
.greeting { font-weight:700; font-size:22px; letter-spacing:-.02em; }
.greeting-name { color:var(--accent); }
.greeting-sub { font-size:12px; color:var(--text-muted); font-weight:500; }
.header-right { display:flex; align-items:center; gap:8px; flex-wrap:wrap; position:relative; }
.header-avatar { width:38px; height:38px; margin:0; background:var(--surface); color:var(--text-muted); border:1px solid var(--border); }

/* TRACKING INDICATOR */
.tracking-indicator { display:flex; align-items:center; gap:6px; font-size:11.5px; font-weight:600; padding:6px 12px; border-radius:20px; background:rgba(21,154,255,0.08); color:var(--accent); border:1px solid rgba(21,154,255,0.2); }
.tracking-indicator.idle    { background:rgba(100,116,139,0.08); color:#64748b; border-color:rgba(100,116,139,0.2); }
.tracking-indicator.stopped { background:var(--surface); color:var(--text-faint); border-color:var(--border); }
.tracking-dot { width:7px; height:7px; border-radius:50%; background:var(--accent); animation:pulse 1.5s infinite; }
.tracking-indicator.idle    .tracking-dot { background:#94a3b8; animation:none; }
.tracking-indicator.stopped .tracking-dot { background:#cbd5e1; animation:none; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.75)} }

/* NOTIFICATIONS */
.notification-bell { position:relative; cursor:pointer; width:38px; height:38px; border-radius:50%; background:var(--card); border:1px solid var(--border); color:var(--text-muted); display:flex; align-items:center; justify-content:center; }
.notif-count { position:absolute; top:-4px; right:-4px; background:#dc2626; color:#fff; font-size:9.5px; font-weight:700; padding:1px 5px; border-radius:20px; }
.blink { animation:blink 1s infinite; }
@keyframes blink { 0%,50%,100%{opacity:1} 25%,75%{opacity:0} }
.notification-panel { position:absolute; right:0; top:48px; background:var(--card); color:var(--text); border-radius:14px; width:260px; max-height:300px; overflow-y:auto; box-shadow:var(--shadow-lg); border:1px solid var(--border); z-index:50; }
.notification-item { padding:11px 14px; border-bottom:1px solid var(--border); font-size:12.5px; }
.empty-notif { text-align:center; color:var(--text-muted); padding:16px; font-size:12.5px; }

/* STAT CARDS */
.dashboard-cards { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:12px; }
.stat-card { background:var(--card); border-radius:14px; padding:16px 18px; border:1px solid var(--border); display:flex; align-items:center; gap:13px; box-shadow:var(--shadow-sm); }
.sc-icon { width:40px; height:40px; border-radius:11px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.sc-blue { background:rgba(21,154,255,0.1); color:var(--accent); }
.sc-label { font-size:10px; color:var(--text-muted); text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px; font-weight:700; }
.sc-value { font-size:21px; font-weight:700; color:var(--text); font-variant-numeric:tabular-nums; }
.sc-sub { font-size:10px; color:var(--text-faint); margin-top:2px; }

/* PANELS */
.main-panels { display:flex; flex-direction:column; gap:16px; }
.panel-card { background:var(--card); border-radius:16px; padding:20px 22px; border:1px solid var(--border); box-shadow:var(--shadow-md); }
.panel-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; flex-wrap:wrap; gap:10px; }
.panel-title { font-size:15px; font-weight:700; color:var(--text); }

/* BUTTONS */
.btn-primary { padding:8px 15px; border-radius:9px; background:var(--accent); color:#fff; border:none; cursor:pointer; font-weight:600; font-size:12.5px; transition:all .15s; display:inline-flex; align-items:center; gap:5px; }
.btn-primary:hover { background:#0c87e6; transform:translateY(-1px); }
.btn-primary:disabled { opacity:.4; cursor:not-allowed; transform:none; }
.btn-danger { padding:8px 15px; border-radius:9px; background:#dc2626; color:#fff; border:none; cursor:pointer; font-weight:600; font-size:12.5px; }
.btn-danger.btn-sm { padding:5px 12px; font-size:11.5px; }
.btn-outline-accent { padding:8px 15px; border-radius:9px; background:transparent; color:var(--accent); border:1px solid rgba(21,154,255,0.3); cursor:pointer; font-weight:600; font-size:12.5px; }
.btn-outline-accent:disabled { opacity:.4; cursor:not-allowed; }
.btn-accent { padding:8px 15px; border-radius:9px; background:var(--accent-deep); color:#fff; border:none; cursor:pointer; font-size:12.5px; font-weight:600; }
.btn-accent:disabled { opacity:.4; cursor:not-allowed; }
.btn-ghost { padding:8px 14px; border-radius:9px; background:var(--card); border:1px solid var(--border); color:var(--text-muted); cursor:pointer; font-size:12px; font-weight:600; display:inline-flex; align-items:center; gap:5px; }
.btn-ghost:hover { border-color:var(--accent); color:var(--accent); }

/* ATTENDANCE */
.attendance-row { display:flex; gap:14px; flex-wrap:wrap; }
.attendance-field { display:flex; flex-direction:column; gap:7px; flex:1; min-width:200px; }
.attendance-field label { font-size:11.5px; font-weight:600; color:var(--text-muted); }
.break-controls { margin-top:8px; display:flex; gap:8px; }
.status-container { margin-top:14px; }
.status { padding:4px 11px; border-radius:8px; font-size:11px; font-weight:700; letter-spacing:.03em; text-transform:capitalize; display:inline-block; }
.status.working    { background:rgba(21,154,255,0.1); color:var(--accent); }
.status.done       { background:rgba(34,197,94,0.1); color:#15803d; }
.status.pending     { background:#fef9c3; color:#854d0e; }
.status.in_progress { background:#dbeafe; color:#1d4ed8; }
.status.complete    { background:#dcfce7; color:#166534; }

/* TASKS */
.tasks-layout { display:grid; grid-template-columns:2fr 1fr; gap:16px; align-items:start; }
.tasks-main-col { min-width:0; }
.tasks-calendar-col { min-width:0; position:sticky; top:0; }
.task-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:14px; list-style:none; }
.task-grid-compact { grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:10px; }
.task-grid-scroll { max-height:640px; overflow-y:auto; padding-right:4px; scrollbar-width:thin; scrollbar-color:var(--border-mid) transparent; }
.task-card { background:var(--surface); border-radius:15px; padding:16px 18px; box-shadow:var(--shadow-sm); border:1px solid var(--border); display:flex; flex-direction:column; gap:9px; }
.task-card-compact { padding:11px 13px; gap:6px; border-radius:12px; }
.task-header { display:flex; justify-content:space-between; align-items:center; padding:9px 13px; border-radius:10px; background:linear-gradient(135deg,var(--accent-deep),var(--accent)); color:#fff; }
.task-card-compact .task-header { padding:6px 10px; border-radius:8px; }
.task-title { font-weight:700; font-size:13px; }
.task-card-compact .task-title { font-size:11.5px; }
.task-desc-card { background:rgba(21,154,255,0.04); border-radius:10px; padding:11px 13px; border:1px solid rgba(21,154,255,0.08); font-size:12.5px; }
.task-card-compact .task-desc-card { padding:8px 10px; font-size:11px; border-radius:8px; }
.desc { color:var(--text-muted); line-height:1.55; margin-bottom:6px; }
.task-card-compact .desc { -webkit-line-clamp:2; display:-webkit-box; -webkit-box-orient:vertical; overflow:hidden; }
.task-meta { font-size:11.5px; color:var(--text-faint); }
.task-attachment a { color:var(--accent); font-size:12px; }
.status-select { padding:7px 10px; border-radius:9px; border:1px solid var(--border); background:var(--card); color:var(--text); font-size:12.5px; }
.comment-toggle-btn { display:flex; align-items:center; gap:6px; width:100%; padding:6px 9px; border-radius:8px; border:1px solid var(--border); background:var(--surface); color:var(--text-muted); cursor:pointer; font-size:10.5px; font-weight:600; transition:all .15s; }
.comment-toggle-btn:hover { border-color:rgba(21,154,255,0.3); color:var(--accent); }
.comment-toggle-btn span { flex:1; text-align:left; }
.comment-toggle-chevron { transition:transform .18s; flex-shrink:0; }
.comment-toggle-chevron.rotated { transform:rotate(180deg); }
.comment-box { margin-top:2px; border-top:1px dashed var(--border); padding-top:8px; max-height:260px; overflow-y:auto; }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:10px; padding:36px 24px; color:var(--text-muted); font-size:13px; text-align:center; }

/* CALENDAR */
.calendar-controls { display:flex; align-items:center; gap:10px; }
.calendar-controls-stacked { flex-direction:column; align-items:flex-start; gap:5px; margin-bottom:12px; }
.calendar-controls label { font-weight:500; font-size:12.5px; color:var(--text-muted); }
.calendar-controls input[type="date"] { padding:7px 11px; border-radius:9px; border:1px solid var(--border); background:var(--card); color:var(--text); font-size:12.5px; }
.calendar-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; margin-bottom:16px; }
.calendar-grid-mini { gap:3px; margin-bottom:12px; }
.calendar-day { min-height:74px; border:1px solid var(--border); border-radius:9px; padding:5px; display:flex; flex-direction:column; background:var(--card); font-size:.85rem; cursor:pointer; }
.calendar-grid-mini .calendar-day { min-height:34px; padding:3px; border-radius:7px; }
.calendar-day.header { font-weight:700; text-align:center; background:linear-gradient(135deg,var(--accent-deep),var(--accent)); color:#fff; min-height:unset; padding:8px; font-size:11px; letter-spacing:.04em; cursor:default; }
.calendar-grid-mini .calendar-day.header { font-size:9px; padding:5px 0; }
.calendar-day.blank { background:transparent; border:none; cursor:default; }
.day-number { font-weight:700; font-size:12px; margin-bottom:3px; color:var(--text); }
.calendar-grid-mini .day-number { font-size:10.5px; margin-bottom:2px; }
.calendar-day.today    { border:2px solid var(--accent); }
.calendar-day.selected { background:rgba(21,154,255,0.06); }
.events { display:flex; flex-direction:column; gap:2px; }
.calendar-grid-mini .events { flex-direction:row; flex-wrap:wrap; gap:2px; }
.event { font-size:.72rem; padding:2px 5px; border-radius:5px; color:#fff; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.calendar-grid-mini .event { width:6px; height:6px; padding:0; border-radius:50%; }
.event.pending     { background:#b45309; }
.event.in_progress { background:var(--accent); }
.event.complete    { background:#15803d; }
.task-list { list-style:none; max-height:420px; overflow-y:auto; }
.task-list li { background:var(--surface); padding:13px 15px; border-radius:11px; margin-bottom:8px; border:1px solid var(--border); }
.task-list h3 { font-size:13.5px; font-weight:700; color:var(--text); display:flex; align-items:center; gap:8px; margin-bottom:5px; }
.task-list p { font-size:12.5px; color:var(--text-muted); margin-top:3px; }
.task-list-mini { max-height:280px; overflow-y:auto; }
.task-list-mini li { padding:9px 11px; margin-bottom:6px; }
.task-list-mini h3 { font-size:11.5px; gap:6px; }
.task-list-mini h3 .status { font-size:9px; padding:2px 6px; }
.task-list-mini p { font-size:10.5px; }
.task-list-empty { background:transparent !important; border:1px dashed var(--border) !important; text-align:center; color:var(--text-faint); font-size:11.5px; padding:14px !important; }

/* ACTIVITY TAB */
.activity-section { display:flex; flex-direction:column; }
.tracking-status-banner { display:flex; align-items:center; gap:9px; padding:13px 16px; border-radius:12px; margin-bottom:16px; border:1px solid transparent; }
.banner-active  { background:rgba(21,154,255,0.06); border-color:rgba(21,154,255,0.18); }
.banner-idle    { background:rgba(100,116,139,0.06); border-color:rgba(100,116,139,0.18); }
.banner-stopped { background:var(--surface); border-color:var(--border); }
.banner-dot { width:9px; height:9px; border-radius:50%; flex-shrink:0; background:var(--accent); animation:pulse 1.5s infinite; }
.banner-idle    .banner-dot { background:#94a3b8; animation:none; }
.banner-stopped .banner-dot { background:#cbd5e1; animation:none; }
.banner-text { font-size:12.5px; color:var(--text-muted); }
.act-type-tabs { display:flex; gap:3px; background:var(--surface); border-radius:12px; padding:4px; width:fit-content; border:1px solid var(--border); margin-bottom:16px; }
.act-type-tab { padding:7px 16px; border:none; background:transparent; font-size:12px; font-weight:600; color:var(--text-muted); cursor:pointer; border-radius:9px; transition:all .18s; display:flex; align-items:center; gap:5px; }
.act-type-tab.active { color:#fff; background:var(--accent); box-shadow:0 3px 10px rgba(21,154,255,0.35); }
.activity-date-row { display:flex; align-items:center; gap:10px; margin-bottom:20px; flex-wrap:wrap; }
.activity-date-row label { font-weight:600; font-size:12.5px; color:var(--text-muted); }
.activity-date-row input { padding:7px 11px; border-radius:9px; border:1px solid var(--border); background:var(--card); color:var(--text); font-size:12.5px; }
.act-loading { color:var(--text-muted); font-size:13px; padding:16px 0; }
.act-empty   { color:var(--text-faint); font-size:12.5px; padding:10px 0; text-align:center; }
.act-live-note { display:flex; align-items:center; gap:6px; font-size:11.5px; color:var(--accent); margin-bottom:16px; font-weight:600; }
.act-live-dot { width:7px; height:7px; border-radius:50%; background:var(--accent); animation:pulse 1.5s infinite; }

/* STAT GRID */
.emp-stat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:18px; }
.emp-stat-grid-2 { grid-template-columns:repeat(2,1fr); margin-bottom:0; }
.dsg-card { display:flex; align-items:center; gap:12px; border-radius:13px; padding:14px 16px; border:1px solid transparent; }
.dsg-active { background:rgba(21,154,255,0.04); border-color:rgba(21,154,255,0.14); }
.dsg-idle   { background:rgba(100,116,139,0.04); border-color:rgba(100,116,139,0.14); }
.dsg-pct    { background:rgba(12,107,184,0.04); border-color:rgba(12,107,184,0.14); }
.dsg-icon { width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.dsg-active .dsg-icon { background:rgba(21,154,255,0.1); color:var(--accent); }
.dsg-idle   .dsg-icon { background:rgba(100,116,139,0.1); color:#64748b; }
.dsg-pct    .dsg-icon { background:rgba(12,107,184,0.1); color:var(--accent-deep); }
.dsg-body { display:flex; flex-direction:column; gap:2px; flex:1; min-width:0; }
.dsg-label { font-size:9.5px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); font-weight:700; }
.dsg-value { font-size:19px; font-weight:700; line-height:1; font-variant-numeric:tabular-nums; }
.dsg-active .dsg-value { color:var(--accent); }
.dsg-idle   .dsg-value { color:#64748b; }
.dsg-pct    .dsg-value { color:var(--accent-deep); }
.dsg-pct-row { display:flex; align-items:center; gap:9px; }
.dsg-pct-bar-wrap { flex:1; height:5px; background:rgba(12,107,184,0.07); border-radius:4px; overflow:hidden; }
.dsg-pct-bar { height:100%; background:linear-gradient(90deg,var(--accent-deep),var(--accent)); border-radius:4px; transition:width .6s; }

/* APP DONUT + TIMELINE */
.emp-bottom-grid { display:grid; grid-template-columns:1fr 1.3fr; gap:14px; align-items:start; margin-bottom:20px; }
.emp-donut-card,.emp-timeline-card { padding:16px 18px; }
.app-donut-layout { display:flex; align-items:center; gap:16px; flex-wrap:wrap; }
.app-donut-svg { width:110px; height:110px; flex-shrink:0; filter:drop-shadow(0 4px 14px rgba(21,154,255,0.12)); }
.app-donut-legend { display:flex; flex-direction:column; gap:6px; flex:1; min-width:100px; }
.donut-legend-row { display:flex; align-items:center; gap:8px; }
.donut-legend-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
.donut-legend-name { flex:1; font-size:12px; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-weight:500; }
.donut-legend-time { font-size:11px; font-weight:700; color:var(--text-muted); white-space:nowrap; font-variant-numeric:tabular-nums; }
.act-period-list { display:flex; flex-direction:column; gap:6px; max-height:260px; overflow-y:auto; }
.tl-entry { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:8px 12px; border-radius:9px; border:1px solid transparent; flex-wrap:wrap; }
.tl-entry-active { background:rgba(21,154,255,0.05); border-color:rgba(21,154,255,0.1); }
.tl-entry-idle   { background:rgba(100,116,139,0.04); border-color:rgba(100,116,139,0.1); }
.tl-count-badge { font-size:10px; font-weight:700; padding:3px 8px; border-radius:16px; text-transform:uppercase; }
.tl-count-active { background:rgba(21,154,255,0.1); color:var(--accent); }
.tl-count-idle   { background:rgba(148,163,184,0.12); color:#64748b; }
.tl-entry-times { display:flex; align-items:center; gap:5px; }
.tl-t { font-size:12px; font-weight:600; color:var(--text); font-variant-numeric:tabular-nums; }
.tl-arrow-icon { color:var(--text-faint); flex-shrink:0; }
.tl-dur { font-size:11px; font-weight:700; color:var(--text-muted); background:var(--surface); border:1px solid var(--border); border-radius:7px; padding:3px 8px; white-space:nowrap; }

/* HISTORY TABLE */
.act-history-section { margin-top:4px; }
.section-label { font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:.07em; color:var(--text-muted); margin-bottom:12px; display:block; }
.attendance-card { background:var(--card); border-radius:14px; overflow-x:auto; }
.history-table { width:100%; border-collapse:collapse; }
.history-table th { font-size:10.5px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); font-weight:700; padding:9px 12px; border-bottom:1px solid var(--border); text-align:left; white-space:nowrap; }
.history-table td { padding:9px 12px; font-size:12.5px; border-bottom:1px solid var(--border); color:var(--text); }
.history-table tbody tr:hover { background:rgba(21,154,255,0.03); }
.time-chip { background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:2px 9px; font-size:12px; font-weight:600; font-variant-numeric:tabular-nums; color:var(--text-muted); }
.time-chip-accent { background:rgba(21,154,255,0.07); border-color:rgba(21,154,255,0.15); color:var(--accent); }
.hist-pct-wrap { display:flex; align-items:center; gap:7px; }
.hist-pct-track { width:60px; height:5px; background:rgba(21,154,255,0.08); border-radius:3px; overflow:hidden; flex-shrink:0; }
.hist-pct-bar { height:100%; background:linear-gradient(90deg,var(--accent-deep),var(--accent)); border-radius:3px; }
.hist-pct-wrap span { font-size:11.5px; font-weight:600; color:var(--text-muted); }

/* BROWSER */
.domain-hint { font-size:11.5px; color:var(--text-faint); margin:-4px 0 10px; }
.domain-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
.domain-card { background:var(--card); border-radius:13px; padding:13px 15px; border:1px solid var(--border); cursor:pointer; display:flex; flex-direction:column; gap:10px; box-shadow:var(--shadow-xs); }
.domain-card:hover,.domain-card.is-expanded { border-color:rgba(21,154,255,0.35); box-shadow:var(--shadow-md); }
.domain-card-header { display:flex; align-items:center; gap:8px; }
.domain-favicon-wrap { width:30px; height:30px; border-radius:8px; background:rgba(21,154,255,0.06); display:flex; align-items:center; justify-content:center; flex-shrink:0; overflow:hidden; }
.domain-favicon-fallback { width:16px; height:16px; border-radius:50%; background:var(--accent); color:#fff; font-size:9px; font-weight:700; display:flex; align-items:center; justify-content:center; }
.domain-name-block { overflow:hidden; flex:1; }
.domain-name { font-size:12.5px; font-weight:700; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:block; }
.domain-visits-count { font-size:10px; color:var(--text-faint); display:block; margin-top:1px; }
.domain-time-pill { font-size:10.5px; font-weight:700; color:var(--accent); background:rgba(21,154,255,0.08); padding:3px 8px; border-radius:10px; white-space:nowrap; flex-shrink:0; }
.domain-expand-chevron { color:var(--text-faint); opacity:.55; transition:transform .2s; flex-shrink:0; }
.domain-expand-chevron.rotated { transform:rotate(180deg); opacity:1; color:var(--accent); }
.domain-url-list { border-top:1px solid var(--border); padding-top:10px; }
.domain-url-table { display:flex; flex-direction:column; gap:3px; max-height:200px; overflow-y:auto; }
.domain-url-row { display:grid; grid-template-columns:1fr 1.4fr auto; gap:7px; align-items:center; padding:7px 8px; border-radius:7px; text-decoration:none; font-size:11.5px; }
.domain-url-header { font-size:9.5px; font-weight:700; color:var(--text-faint); text-transform:uppercase; letter-spacing:.05em; }
.domain-url-row:not(.domain-url-header):hover { background:rgba(21,154,255,0.06); }
.domain-url-path { color:var(--accent); font-family:'Courier New',monospace; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.domain-url-title { color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.domain-url-time { font-weight:700; color:var(--text-muted); white-space:nowrap; font-variant-numeric:tabular-nums; }
.domain-url-empty { font-size:12px; color:var(--text-muted); padding:5px 0; }

/* CHAT */
.chat-page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }
.chat-container { display:flex; flex-direction:column; gap:12px; }
.chat-messages { overflow-y:auto; display:flex; flex-direction:column; gap:8px; border:1px solid var(--border); border-radius:12px; min-height:220px; max-height:420px; padding:14px; background:var(--surface); }
.chat-msg { display:flex; flex-direction:column; max-width:72%; }
.chat-msg.self { align-self:flex-end; align-items:flex-end; }
.chat-msg.other { align-self:flex-start; }
.chat-sender { font-size:10px; font-weight:700; color:var(--text-muted); margin-bottom:3px; text-transform:uppercase; letter-spacing:.03em; }
.chat-bubble { padding:9px 13px; border-radius:12px; font-size:13px; line-height:1.5; }
.chat-msg.self  .chat-bubble { background:linear-gradient(135deg,var(--accent-deep),var(--accent)); color:#fff; border-radius:12px 12px 2px 12px; }
.chat-msg.other .chat-bubble { background:var(--card); color:var(--text); border:1px solid var(--border); border-radius:12px 12px 12px 2px; }
.chat-time { font-size:10px; color:var(--text-faint); margin-top:3px; }
.chat-input-wrap { display:flex; gap:8px; }
.chat-input-wrap input { flex:1; padding:10px 13px; border-radius:10px; border:1px solid var(--border); background:var(--surface); color:var(--text); font-size:13px; }

/* PROFILE */
.profile-form { display:flex; flex-direction:column; gap:14px; max-width:420px; }
.form-field { display:flex; flex-direction:column; gap:6px; }
.form-field label { font-size:11.5px; font-weight:600; color:var(--text-muted); }

input[type=text],input[type=email],input[type=password],input[type=time],input[type=date] { padding:9px 12px; border-radius:9px; border:1px solid var(--border); background:var(--card); color:var(--text); font-size:13px; }
input:focus { outline:none; border-color:rgba(21,154,255,0.4); box-shadow:0 0 0 3px rgba(21,154,255,0.08); }
select { font-family:inherit; }

/* MODAL */
.modal-overlay { position:fixed; inset:0; background:rgba(4,8,16,0.55); display:flex; justify-content:center; align-items:center; z-index:100; backdrop-filter:blur(5px); }
.modal-box { background:var(--card); padding:28px 26px; border-radius:18px; box-shadow:var(--shadow-lg); display:flex; flex-direction:column; gap:6px; border:1px solid var(--border); min-width:280px; max-width:340px; text-align:center; align-items:center; }
.modal-actions { display:flex; gap:8px; justify-content:center; margin-top:10px; width:100%; }
.modal-actions .btn-primary { flex:1; justify-content:center; }
.info-modal-icon { width:48px; height:48px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin-bottom:6px; }
.info-modal-success .info-modal-icon { background:rgba(21,154,255,0.12); color:var(--accent); }
.info-modal-error   .info-modal-icon { background:rgba(220,38,38,0.1); color:#dc2626; }
.info-modal h3 { font-size:15.5px; font-weight:700; color:var(--text); }
.info-modal p  { font-size:12.5px; color:var(--text-muted); line-height:1.5; }

@media (max-width:1024px) {
  .tasks-layout { grid-template-columns:1fr; }
  .tasks-calendar-col { position:static; }
  .emp-bottom-grid { grid-template-columns:1fr; }
  .domain-grid { grid-template-columns:repeat(2,1fr); }
}
@media (max-width:768px) {
  .sidebar { position:fixed; top:0; left:-260px; height:100%; margin:0; border-radius:0; transition:left .28s; }
  .sidebar.show { left:0; }
  .mobile-toggle { display:flex; }
  .content { padding:60px 16px 24px; }
  .emp-stat-grid { grid-template-columns:1fr; }
  .domain-grid { grid-template-columns:1fr; }
  .top-header { flex-direction:column; align-items:flex-start; }
}
</style>

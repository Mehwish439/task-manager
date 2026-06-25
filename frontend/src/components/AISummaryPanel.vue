<template>
  <div class="ai-summary-panel">

    <!-- ══════════════════════════════════════════════════════
         HEADER — title, subtitle, period toggle
    ══════════════════════════════════════════════════════ -->
    <div class="ais-header">
      <div class="ais-title-row">
        <div class="ais-icon-wrap">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3
                 m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547
                 A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531
                 c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
        </div>
        <div>
          <h4 class="ais-title">AI Productivity Summary</h4>
          <p class="ais-sub">Powered by Mistral-7B · HuggingFace Inference API</p>
        </div>
      </div>

      <div class="ais-header-right">
        <!-- Period toggle -->
        <div class="ais-period-toggle">
          <button
            class="ais-period-btn"
            :class="{ active: period === 'weekly' }"
            @click="setPeriod('weekly')"
          >Weekly</button>
          <button
            class="ais-period-btn"
            :class="{ active: period === 'monthly' }"
            @click="setPeriod('monthly')"
          >Monthly</button>
        </div>

        <!-- Export button (only shown when summary exists) -->
        <button
          v-if="result && result.summary"
          class="ais-export-btn"
          @click="exportText"
          title="Export summary as .txt file"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
          </svg>
          Export
        </button>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════
         GENERATE BUTTON (shown before any result)
    ══════════════════════════════════════════════════════ -->
    <div class="ais-generate-row" v-if="!loading && !result">
      <button class="ais-generate-btn" @click="generate">
        <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"
             fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M13 10V3L4 14h7v7l9-11h-7z"/>
        </svg>
        Generate {{ period === 'weekly' ? '7-Day' : '30-Day' }} AI Summary
      </button>
      <p class="ais-hint">
        Sends activity data to HuggingFace and returns an AI-written report.
        First call may take ~30s while the model warms up.
      </p>
    </div>

    <!-- ══════════════════════════════════════════════════════
         LOADING STATE
    ══════════════════════════════════════════════════════ -->
    <div class="ais-loading" v-if="loading">
      <div class="ais-spinner-wrap">
        <div class="ais-spinner"></div>
      </div>
      <div class="ais-loading-body">
        <p class="ais-loading-title">Generating AI summary…</p>
        <p class="ais-loading-sub">{{ loadingMessage }}</p>
        <div class="ais-loading-steps">
          <span
            v-for="(step, i) in loadingSteps"
            :key="i"
            class="ais-step-dot"
            :class="{ 'step-done': loadingStepIndex > i, 'step-active': loadingStepIndex === i }"
          ></span>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════
         ERROR STATE
    ══════════════════════════════════════════════════════ -->
    <div class="ais-error" v-if="error && !loading">
      <div class="ais-error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
             fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667
               1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16
               c-.77 1.333.192 3 1.732 3z"/>
        </svg>
      </div>
      <div class="ais-error-body">
        <strong>Failed to generate summary</strong>
        <p>{{ error }}</p>
        <button class="ais-retry-btn" @click="generate">
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11
                 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          Try Again
        </button>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════
         NO DATA STATE
    ══════════════════════════════════════════════════════ -->
    <div class="ais-no-data" v-if="result && !result.summary && result.message && !loading">
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"
           fill="none" viewBox="0 0 24 24" stroke="currentColor" style="opacity:.25;">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
          d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0
             012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0
             01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
      <p class="ais-no-data-msg">{{ result.message }}</p>
      <p class="ais-no-data-hint">
        Make sure the Electron tracker app is running for this member
        and that data has been synced for the selected period.
      </p>
    </div>

    <!-- ══════════════════════════════════════════════════════
         RESULT — stats strip + charts + AI narrative
    ══════════════════════════════════════════════════════ -->
    <template v-if="result && result.summary && !loading">

      <!-- Stats strip -->
      <div class="ais-stats-strip">
        <div class="ais-stat-card ais-stat-active">
          <span class="ais-stat-label">Total Active</span>
          <span class="ais-stat-value">{{ result.stats.total_active }}</span>
        </div>
        <div class="ais-stat-card ais-stat-idle">
          <span class="ais-stat-label">Total Idle</span>
          <span class="ais-stat-value">{{ result.stats.total_idle }}</span>
        </div>
        <div class="ais-stat-card ais-stat-pct">
          <span class="ais-stat-label">Active %</span>
          <span class="ais-stat-value">{{ result.stats.overall_active_pct }}%</span>
        </div>
        <div class="ais-stat-card ais-stat-browser">
          <span class="ais-stat-label">Browser</span>
          <span class="ais-stat-value">{{ result.stats.total_browser }}</span>
        </div>
        <div class="ais-stat-card ais-stat-days">
          <span class="ais-stat-label">Days</span>
          <span class="ais-stat-value">{{ result.stats.days_tracked }}</span>
        </div>
        <div class="ais-stat-card ais-stat-screenshots">
          <span class="ais-stat-label">Screenshots</span>
          <span class="ais-stat-value">{{ result.stats.screenshot_count }}</span>
        </div>
      </div>

      <!-- Period label -->
      <p class="ais-period-label">
        {{ capitalize(result.period) }} report ·
        {{ result.period_start }} → {{ result.period_end }}
      </p>

      <!-- ── Daily activity bar chart ── -->
      <div class="ais-chart-card" v-if="result.stats.daily && result.stats.daily.length">
        <h5 class="ais-card-title">
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2
                 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0
                 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2
                 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
          Daily Active Time
        </h5>
        <div class="ais-bar-chart">
          <div
            v-for="day in result.stats.daily"
            :key="day.date"
            class="ais-bar-col"
            :title="`${day.date}\nActive: ${day.active} (${day.active_pct}%)\nIdle: ${day.idle}\nTop App: ${day.top_app}`"
          >
            <div class="ais-bar-track">
              <div
                class="ais-bar-fill"
                :style="{ height: barHeight(day.active_seconds) + '%' }"
                :class="barClass(day.active_pct)"
              ></div>
            </div>
            <span class="ais-bar-label">{{ shortDate(day.date) }}</span>
            <span class="ais-bar-pct">{{ day.active_pct }}%</span>
          </div>
        </div>
        <!-- Bar legend -->
        <div class="ais-bar-legend">
          <span class="ais-legend-dot bar-high"></span><span>≥80% active</span>
          <span class="ais-legend-dot bar-mid"></span><span>50–79%</span>
          <span class="ais-legend-dot bar-low"></span><span>&lt;50%</span>
        </div>
      </div>

      <!-- ── Top apps + Top domains side by side ── -->
      <div class="ais-side-grid">

        <!-- Top apps -->
        <div class="ais-side-card" v-if="result.stats.top_apps && result.stats.top_apps.length">
          <h5 class="ais-card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13"
                 fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0
                   002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            Top Applications
          </h5>
          <div
            v-for="(app, i) in result.stats.top_apps"
            :key="app.app"
            class="ais-side-row"
          >
            <span class="ais-rank" :style="{ color: rankColor(i) }">{{ i + 1 }}</span>
            <span class="ais-side-name">{{ app.app }}</span>
            <span class="ais-side-time">{{ app.time }}</span>
          </div>
        </div>

        <!-- Top domains -->
        <div class="ais-side-card" v-if="result.stats.top_domains && result.stats.top_domains.length">
          <h5 class="ais-card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13"
                 fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0
                   01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657
                   0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
            </svg>
            Top Websites
          </h5>
          <div
            v-for="(site, i) in result.stats.top_domains"
            :key="site.domain"
            class="ais-side-row"
          >
            <span class="ais-rank" :style="{ color: rankColor(i) }">{{ i + 1 }}</span>
            <img
              :src="`https://www.google.com/s2/favicons?sz=16&domain=${site.domain}`"
              width="14" height="14" class="ais-favicon"
              onerror="this.style.display='none'"
            />
            <span class="ais-side-name">{{ site.domain }}</span>
            <span class="ais-side-visits">{{ site.visits }}x</span>
            <span class="ais-side-time">{{ site.time }}</span>
          </div>
        </div>
      </div>

      <!-- ── Best / Worst day highlight ── -->
      <div class="ais-highlights" v-if="result.stats.best_day || result.stats.worst_day">
        <div class="ais-highlight ais-highlight-best" v-if="result.stats.best_day">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
          </svg>
          <div>
            <span class="ais-hl-label">Best Day</span>
            <span class="ais-hl-date">{{ result.stats.best_day.date }}</span>
            <span class="ais-hl-value">{{ result.stats.best_day.active }}</span>
            <span class="ais-hl-pct">{{ result.stats.best_day.pct }}% active</span>
          </div>
        </div>
        <div class="ais-highlight ais-highlight-worst" v-if="result.stats.worst_day">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"/>
          </svg>
          <div>
            <span class="ais-hl-label">Worst Day</span>
            <span class="ais-hl-date">{{ result.stats.worst_day.date }}</span>
            <span class="ais-hl-value">{{ result.stats.worst_day.active }}</span>
            <span class="ais-hl-pct">{{ result.stats.worst_day.pct }}% active</span>
          </div>
        </div>
      </div>

      <!-- ── AI Narrative ── -->
      <div class="ais-narrative">
        <div class="ais-narrative-header">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4
                 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547
                 A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531
                 c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
          AI Analysis — {{ result.username }}
          <span class="ais-narrative-badge">{{ capitalize(result.period) }}</span>
        </div>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div class="ais-text" v-html="formatSummary(result.summary)"></div>
      </div>

      <!-- ── Action row ── -->
      <div class="ais-action-row">
        <button class="ais-regen-btn" @click="generate" :disabled="loading">
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11
                 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          Regenerate
        </button>
        <button class="ais-copy-btn" @click="copySummary">
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6
                 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
          </svg>
          {{ copied ? '✓ Copied!' : 'Copy Text' }}
        </button>
        <span class="ais-generated-at" v-if="generatedAt">
          Generated {{ generatedAt }}
        </span>
      </div>

    </template>

  </div>
</template>

<script>
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL

const LOADING_STEPS = [
  'Collecting activity data from database…',
  'Building prompt for Mistral-7B…',
  'Calling HuggingFace Inference API… (first call can take ~30s)',
  'Parsing and cleaning AI response…',
]

// Rank colours — blue gradient for top positions
const RANK_COLOURS = ['#159aff', '#0c6bb8', '#5fb6ff', '#3c4a5e', '#9aa5b1', '#6b7280']

export default {
  name: 'AISummaryPanel',

  props: {
    /**
     * ID of the team member to summarise.
     * Passed from LeadDashboard as :userId="activityMemberId"
     */
    userId: {
      type: [Number, String],
      required: true,
    },
    /**
     * Optional: if true, automatically generate on mount without
     * waiting for the user to click the Generate button.
     */
    autoGenerate: {
      type: Boolean,
      default: false,
    },
  },

  emits: ['summary-ready'],

  data() {
    return {
      period:           'weekly',
      loading:          false,
      loadingSteps:     LOADING_STEPS,
      loadingStepIndex: 0,
      loadingMessage:   LOADING_STEPS[0],
      loadingInterval:  null,
      result:           null,
      error:            null,
      copied:           false,
      generatedAt:      null,
    }
  },

  watch: {
    userId(newId) {
      // Reset when the parent switches to a different member
      this.result      = null
      this.error       = null
      this.generatedAt = null
      if (this.autoGenerate && newId) {
        this.generate()
      }
    },
  },

  mounted() {
    if (this.autoGenerate && this.userId) {
      this.generate()
    }
  },

  beforeUnmount() {
    this._clearLoadingCycle()
  },

  methods: {

    // ── Period ─────────────────────────────────────────────────────────────

    setPeriod(p) {
      if (this.period === p) return
      this.period      = p
      this.result      = null
      this.error       = null
      this.generatedAt = null
    },

    // ── Main generate call ─────────────────────────────────────────────────

    async generate() {
      if (!this.userId) return
      this.loading     = true
      this.error       = null
      this.result      = null
      this.generatedAt = null
      this._startLoadingCycle()

      try {
        const token = localStorage.getItem('access')
        const res   = await axios.get(
          `${API_BASE}activity/ai-summary/${this.userId}/?period=${this.period}`,
          {
            headers: { Authorization: `Bearer ${token}` },
            timeout: 100000,   // 100s — generous for HF free tier cold start
          }
        )
        this.result      = res.data
        this.generatedAt = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        this.$emit('summary-ready', res.data)
      } catch (err) {
        if (err.response?.data?.error) {
          this.error = err.response.data.error
        } else if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
          this.error =
            'Request timed out. The HuggingFace model is likely warming up. ' +
            'Please wait 30 seconds and click "Try Again".'
        } else if (err.response?.status === 503) {
          this.error =
            'The AI service is temporarily unavailable. ' +
            'Please try again in a moment.'
        } else if (err.response?.status === 401) {
          this.error =
            'Authentication failed. Please refresh the page and log in again.'
        } else if (err.response?.status === 403) {
          this.error = 'You do not have permission to view AI summaries.'
        } else {
          this.error =
            `Unexpected error: ${err.message || 'Unknown'}. ` +
            'Check the Django server logs for details.'
        }
      } finally {
        this.loading = false
        this._clearLoadingCycle()
      }
    },

    // ── Loading cycle ──────────────────────────────────────────────────────

    _startLoadingCycle() {
      this.loadingStepIndex = 0
      this.loadingMessage   = LOADING_STEPS[0]
      this.loadingInterval  = setInterval(() => {
        this.loadingStepIndex = Math.min(
          this.loadingStepIndex + 1,
          LOADING_STEPS.length - 1
        )
        this.loadingMessage = LOADING_STEPS[this.loadingStepIndex]
      }, 8000)
    },

    _clearLoadingCycle() {
      if (this.loadingInterval) {
        clearInterval(this.loadingInterval)
        this.loadingInterval  = null
        this.loadingStepIndex = 0
      }
    },

    // ── Bar chart helpers ──────────────────────────────────────────────────

    barHeight(activeSeconds) {
      if (!this.result?.stats?.daily?.length) return 0
      const max = Math.max(
        ...this.result.stats.daily.map(d => d.active_seconds || 0)
      )
      if (!max) return 0
      return Math.max(4, Math.round((activeSeconds / max) * 100))
    },

    barClass(pct) {
      if (pct >= 80) return 'bar-high'
      if (pct >= 50) return 'bar-mid'
      return 'bar-low'
    },

    shortDate(dateStr) {
      // "2025-06-17" → "17/6" or day name for weekly
      try {
        const d   = new Date(dateStr + 'T00:00:00')
        const day = ['Su','Mo','Tu','We','Th','Fr','Sa'][d.getDay()]
        return this.period === 'weekly'
          ? day
          : `${d.getDate()}/${d.getMonth() + 1}`
      } catch { return dateStr.slice(5) }
    },

    rankColor(i) {
      return RANK_COLOURS[i % RANK_COLOURS.length]
    },

    // ── Text formatting ────────────────────────────────────────────────────

    /**
     * Convert the AI's markdown-like output to safe HTML.
     * Rules:
     *   **bold**          → <strong>
     *   - bullet          → <li class="ais-li">
     *   1. **Section**    → <h5 class="ais-section-head">
     *   blank lines       → paragraph breaks
     */
    formatSummary(text) {
      if (!text) return ''

      // 1. Escape HTML entities for safety
      let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')

      // 2. Bold: **text**
      html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

      // 3. Section headings: lines that start with a digit and a dot
      //    e.g.  "1. Overview"  or  "1. <strong>Overview</strong>"
      html = html.replace(
        /^(\d+)\.\s+(?:<strong>)?(.+?)(?:<\/strong>)?$/gm,
        '<h5 class="ais-section-head">$2</h5>'
      )

      // 4. Bullet lines: starting with - or *
      html = html.replace(/^[-*]\s+(.+)$/gm, '<li class="ais-li">$1</li>')

      // 5. Wrap consecutive <li> groups in <ul>
      html = html.replace(
        /(<li class="ais-li">[\s\S]*?<\/li>(\n)?)+/g,
        match => `<ul class="ais-ul">${match}</ul>`
      )

      // 6. Paragraph breaks on double newlines (skip if line is heading/list)
      const lines = html.split('\n')
      let output  = ''
      let inPara  = false
      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed) {
          if (inPara) { output += '</p>'; inPara = false }
          continue
        }
        if (trimmed.startsWith('<h5') || trimmed.startsWith('<ul') || trimmed.startsWith('<li')) {
          if (inPara) { output += '</p>'; inPara = false }
          output += trimmed
        } else {
          if (!inPara) { output += '<p class="ais-p">'; inPara = true }
          else output += ' '
          output += trimmed
        }
      }
      if (inPara) output += '</p>'

      return output
    },

    // ── Copy to clipboard ──────────────────────────────────────────────────

    async copySummary() {
      if (!this.result?.summary) return
      const plain = this._buildPlainText()
      try {
        await navigator.clipboard.writeText(plain)
      } catch {
        // Fallback for environments without clipboard API
        const el = document.createElement('textarea')
        el.value = plain
        el.style.position = 'fixed'
        el.style.opacity  = '0'
        document.body.appendChild(el)
        el.focus()
        el.select()
        document.execCommand('copy')
        document.body.removeChild(el)
      }
      this.copied = true
      setTimeout(() => { this.copied = false }, 2500)
    },

    // ── Export as .txt ─────────────────────────────────────────────────────

    exportText() {
      if (!this.result?.summary) return
      const plain    = this._buildPlainText()
      const blob     = new Blob([plain], { type: 'text/plain;charset=utf-8' })
      const url      = URL.createObjectURL(blob)
      const link     = document.createElement('a')
      const filename = `ai-summary-${this.result.username}-${this.result.period}-${this.result.period_end}.txt`
      link.href      = url
      link.download  = filename
      link.click()
      URL.revokeObjectURL(url)
    },

    _buildPlainText() {
      const s = this.result
      const st = s.stats
      const header = [
        `QRM AI PRODUCTIVITY SUMMARY`,
        `Member  : ${s.username}`,
        `Period  : ${capitalize_(s.period)} (${s.period_start} → ${s.period_end})`,
        `Generated: ${new Date().toLocaleString()}`,
        '',
        '─── STATS ───────────────────────────────────',
        `Total Active   : ${st.total_active}`,
        `Total Idle     : ${st.total_idle}`,
        `Active %       : ${st.overall_active_pct}%`,
        `Browser Time   : ${st.total_browser}`,
        `Days Tracked   : ${st.days_tracked}`,
        `Screenshots    : ${st.screenshot_count}`,
        '',
        '─── TOP APPS ────────────────────────────────',
        ...st.top_apps.map((a, i) => `  ${i + 1}. ${a.app} — ${a.time}`),
        '',
        '─── TOP WEBSITES ────────────────────────────',
        ...st.top_domains.map((d, i) => `  ${i + 1}. ${d.domain} — ${d.time} (${d.visits} visits)`),
        '',
        '─── AI ANALYSIS ─────────────────────────────',
        s.summary,
      ].join('\n')
      return header
    },

    capitalize(str) {
      return str ? str.charAt(0).toUpperCase() + str.slice(1) : ''
    },
  },
}

// Module-level helper (used inside _buildPlainText where `this` isn't available)
function capitalize_(str) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : ''
}
</script>

<style scoped>
/* ── Root ────────────────────────────────────────────────────────────────── */
.ai-summary-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-bottom: 8px;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.ais-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.ais-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.ais-icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 11px;
  background: linear-gradient(135deg, rgba(21,154,255,0.15), rgba(12,107,184,0.2));
  color: #159aff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid rgba(21,154,255,0.2);
}
.ais-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 2px;
}
.ais-sub {
  font-size: 11px;
  color: var(--text-muted);
  margin: 0;
}
.ais-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

/* Period toggle */
.ais-period-toggle {
  display: flex;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 3px;
  gap: 2px;
}
.ais-period-btn {
  padding: 5px 14px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.18s;
  font-family: inherit;
}
.ais-period-btn.active {
  background: #159aff;
  color: #fff;
  box-shadow: 0 2px 8px rgba(21, 154, 255, 0.3);
}
.ais-period-btn:hover:not(.active) {
  color: var(--text);
  background: rgba(0,0,0,0.05);
}

/* Export button */
.ais-export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 13px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.ais-export-btn:hover {
  color: var(--text);
  border-color: rgba(21, 154, 255, 0.3);
  background: rgba(21, 154, 255, 0.04);
}

/* ── Generate row ────────────────────────────────────────────────────────── */
.ais-generate-row {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  padding: 20px;
  background: var(--card);
  border: 1px dashed var(--border);
  border-radius: 14px;
}
.ais-generate-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 11px 24px;
  background: linear-gradient(135deg, #0c6bb8, #159aff);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(21, 154, 255, 0.35);
  transition: transform 0.15s, box-shadow 0.15s;
  font-family: inherit;
  white-space: nowrap;
}
.ais-generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(21, 154, 255, 0.45);
}
.ais-hint {
  font-size: 12px;
  color: var(--text-muted);
  max-width: 360px;
  margin: 0;
  line-height: 1.5;
}

/* ── Loading ─────────────────────────────────────────────────────────────── */
.ais-loading {
  display: flex;
  align-items: center;
  gap: 18px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px 24px;
}
.ais-spinner-wrap {
  flex-shrink: 0;
}
.ais-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(21, 154, 255, 0.15);
  border-top-color: #159aff;
  border-radius: 50%;
  animation: ais-spin 0.75s linear infinite;
}
@keyframes ais-spin { to { transform: rotate(360deg); } }
.ais-loading-body { flex: 1; }
.ais-loading-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 4px;
}
.ais-loading-sub {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0 0 10px;
}
.ais-loading-steps {
  display: flex;
  gap: 6px;
}
.ais-step-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--border);
  transition: background 0.3s;
}
.ais-step-dot.step-done   { background: rgba(21,154,255,0.4); }
.ais-step-dot.step-active { background: #159aff; animation: ais-pulse 1s infinite; }
@keyframes ais-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%       { transform: scale(1.4); opacity: 0.7; }
}

/* ── Error ───────────────────────────────────────────────────────────────── */
.ais-error {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: rgba(220, 38, 38, 0.04);
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 12px;
  padding: 16px 18px;
}
.ais-error-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ais-error-body strong {
  display: block;
  font-size: 13px;
  color: #dc2626;
  margin-bottom: 4px;
}
.ais-error-body p {
  font-size: 12px;
  color: #b91c1c;
  margin: 0 0 12px;
  line-height: 1.5;
}
.ais-retry-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 13px;
  background: rgba(220, 38, 38, 0.08);
  border: 1px solid rgba(220, 38, 38, 0.25);
  border-radius: 7px;
  font-size: 12px;
  font-weight: 600;
  color: #dc2626;
  cursor: pointer;
  transition: background 0.15s;
  font-family: inherit;
}
.ais-retry-btn:hover { background: rgba(220, 38, 38, 0.15); }

/* ── No data ─────────────────────────────────────────────────────────────── */
.ais-no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 36px 24px;
  gap: 8px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
}
.ais-no-data-msg {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}
.ais-no-data-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
  max-width: 360px;
  line-height: 1.5;
}

/* ── Stats strip ─────────────────────────────────────────────────────────── */
.ais-stats-strip {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
}
.ais-stat-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 11px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.ais-stat-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}
.ais-stat-value {
  font-size: 17px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.1;
}
.ais-stat-active      .ais-stat-value { color: #159aff; }
.ais-stat-idle        .ais-stat-value { color: #6b7280; }
.ais-stat-pct         .ais-stat-value { color: #0c6bb8; }
.ais-stat-browser     .ais-stat-value { color: #3c4a5e; }
.ais-stat-days        .ais-stat-value { color: var(--text); }
.ais-stat-screenshots .ais-stat-value { color: #9aa5b1; }

/* Period label */
.ais-period-label {
  font-size: 11px;
  color: var(--text-muted);
  margin: -6px 0 0;
}

/* ── Daily bar chart ─────────────────────────────────────────────────────── */
.ais-chart-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px 20px;
}
.ais-card-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin: 0 0 16px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.ais-bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 80px;
  padding-bottom: 2px;
}
.ais-bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  height: 100%;
}
.ais-bar-track {
  flex: 1;
  width: 100%;
  background: rgba(21, 154, 255, 0.06);
  border-radius: 4px;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-end;
}
.ais-bar-fill {
  width: 100%;
  border-radius: 4px;
  transition: height 0.6s ease;
}
.bar-high { background: linear-gradient(180deg, #159aff, #0c6bb8); }
.bar-mid  { background: linear-gradient(180deg, #5fb6ff, #3c4a5e); }
.bar-low  { background: linear-gradient(180deg, #9aa5b1, #6b7280); }
.ais-bar-label {
  font-size: 9px;
  color: var(--text-muted);
  white-space: nowrap;
}
.ais-bar-pct {
  font-size: 8px;
  font-weight: 700;
  color: var(--text-muted);
  white-space: nowrap;
}
.ais-bar-legend {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  font-size: 11px;
  color: var(--text-muted);
  flex-wrap: wrap;
}
.ais-legend-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 2px;
  flex-shrink: 0;
}
.ais-legend-dot.bar-high { background: #159aff; }
.ais-legend-dot.bar-mid  { background: #5fb6ff; }
.ais-legend-dot.bar-low  { background: #9aa5b1; }

/* ── Side grid: apps + domains ───────────────────────────────────────────── */
.ais-side-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.ais-side-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px 18px;
}
.ais-side-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid var(--border);
  font-size: 12px;
}
.ais-side-row:last-child { border-bottom: none; }
.ais-rank {
  font-size: 11px;
  font-weight: 700;
  width: 16px;
  flex-shrink: 0;
  text-align: center;
}
.ais-favicon { border-radius: 3px; flex-shrink: 0; }
.ais-side-name {
  flex: 1;
  color: var(--text);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ais-side-visits {
  font-size: 10px;
  color: var(--text-muted);
  white-space: nowrap;
  flex-shrink: 0;
}
.ais-side-time {
  font-size: 11px;
  font-weight: 700;
  color: #159aff;
  white-space: nowrap;
  flex-shrink: 0;
}

/* ── Best / Worst highlights ─────────────────────────────────────────────── */
.ais-highlights {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.ais-highlight {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px 16px;
  border-radius: 12px;
  border: 1px solid transparent;
}
.ais-highlight-best {
  background: rgba(21, 154, 255, 0.05);
  border-color: rgba(21, 154, 255, 0.18);
  color: #159aff;
}
.ais-highlight-worst {
  background: rgba(107, 114, 128, 0.05);
  border-color: rgba(107, 114, 128, 0.18);
  color: #6b7280;
}
.ais-highlight svg { flex-shrink: 0; margin-top: 2px; }
.ais-highlight > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.ais-hl-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.7;
}
.ais-hl-date  { font-size: 12px; font-weight: 600; color: var(--text); }
.ais-hl-value { font-size: 16px; font-weight: 700; }
.ais-hl-pct   { font-size: 11px; opacity: 0.75; }

/* ── AI Narrative ────────────────────────────────────────────────────────── */
.ais-narrative {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px 22px;
}
.ais-narrative-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #159aff;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.ais-narrative-badge {
  margin-left: auto;
  background: rgba(21, 154, 255, 0.1);
  color: #159aff;
  border: 1px solid rgba(21, 154, 255, 0.2);
  border-radius: 10px;
  padding: 2px 9px;
  font-size: 10px;
  font-weight: 700;
  text-transform: capitalize;
  letter-spacing: 0.04em;
}
.ais-text {
  font-size: 13px;
  line-height: 1.75;
  color: var(--text);
}

/* Rendered markdown elements */
:deep(.ais-section-head) {
  font-size: 13px;
  font-weight: 700;
  color: #0c6bb8;
  margin: 18px 0 8px;
  padding-bottom: 5px;
  border-bottom: 1px solid var(--border);
}
:deep(.ais-section-head:first-child) { margin-top: 0; }
:deep(.ais-ul) {
  list-style: none;
  padding: 0;
  margin: 4px 0 12px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
:deep(.ais-li) {
  padding-left: 16px;
  position: relative;
  font-size: 13px;
  color: var(--text);
  line-height: 1.6;
}
:deep(.ais-li)::before {
  content: '›';
  position: absolute;
  left: 0;
  color: #159aff;
  font-weight: 700;
  font-size: 14px;
  line-height: 1.4;
}
:deep(.ais-p) {
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--text);
  line-height: 1.7;
}
:deep(.ais-p:last-child) { margin-bottom: 0; }

/* ── Action row ──────────────────────────────────────────────────────────── */
.ais-action-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.ais-regen-btn,
.ais-copy-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.ais-regen-btn {
  background: rgba(21, 154, 255, 0.08);
  color: #159aff;
  border: 1px solid rgba(21, 154, 255, 0.22);
}
.ais-regen-btn:hover:not(:disabled) { background: rgba(21, 154, 255, 0.16); }
.ais-regen-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.ais-copy-btn {
  background: transparent;
  color: var(--text-muted);
  border: 1px solid var(--border);
}
.ais-copy-btn:hover {
  color: var(--text);
  border-color: rgba(21, 154, 255, 0.3);
  background: rgba(21, 154, 255, 0.04);
}
.ais-generated-at {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-muted);
}

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 1100px) {
  .ais-stats-strip { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 768px) {
  .ais-side-grid      { grid-template-columns: 1fr; }
  .ais-highlights     { grid-template-columns: 1fr; }
  .ais-stats-strip    { grid-template-columns: repeat(2, 1fr); }
  .ais-header         { flex-direction: column; align-items: flex-start; }
  .ais-header-right   { flex-direction: column; align-items: flex-start; }
  .ais-bar-chart      { gap: 4px; }
  .ais-generate-row   { flex-direction: column; align-items: flex-start; }
}
@media (max-width: 480px) {
  .ais-stats-strip    { grid-template-columns: 1fr 1fr; }
}
</style>

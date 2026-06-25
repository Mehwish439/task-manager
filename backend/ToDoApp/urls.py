from django.urls import path
from .views import (
    # Auth
    RegisterView, MyTokenObtainPairView, MeView,
    CustomTokenRefreshView, UpdateUserProfile,
    # Tasks
    CreateTaskView, AssignedTaskListView, CreatedTaskListView,
    TaskUpdateView, TaskDeleteView, AssignTaskView,
    TaskFileDownloadView, TaskStatusBreakdownView, TaskCalendarView,
    # Team
    TeamMemberListView,
    # Comments
    CommentListCreateAPIView, CommentDetailAPIView,
    # Attendance
    CheckInView, CheckOutView, PauseWorkView, ResumeWorkView,
    AttendanceListView, AttendanceCSVExportView,
    # Chat
    GroupChatListCreateView, GroupChatClearView,
    # Activity
    TrackActivityView,
    ActivitySummaryView,
    ActivityLogsView,
    TeamActivitySummaryView,
    MemberActivityDetailView,
    ActivityHistoryView,
    AppTimeLeaderboardView,
    WeeklyActivityReportView,
    MyActivityLogsView,
    # Browser Activity (NEW)
    BrowserActivityView,
    BrowserActivityListView,
)

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────
    path('api/register/',      RegisterView.as_view()),
    path('api/login/',         MyTokenObtainPairView.as_view()),
    path('api/me/',            MeView.as_view()),
    path('api/refresh-token/', CustomTokenRefreshView.as_view()),
    path('api/me/update/',     UpdateUserProfile.as_view()),

    # ── Tasks ─────────────────────────────────────────────────────
    path('api/create-task/',                         CreateTaskView.as_view()),
    path('api/assigned-tasks/',                      AssignedTaskListView.as_view()),
    path('api/created-tasks/',                       CreatedTaskListView.as_view()),
    path('api/update-task/<int:id>/',                TaskUpdateView.as_view()),
    path('api/delete-task/<int:id>/',                TaskDeleteView.as_view()),
    path('api/assign-task/<int:task_id>/',           AssignTaskView.as_view()),
    path('api/download-task-file/<int:task_id>/',    TaskFileDownloadView.as_view()),
    path('api/task-status/<int:task_id>/breakdown/', TaskStatusBreakdownView.as_view()),
    path('api/tasks/calendar/',                      TaskCalendarView.as_view()),

    # ── Comments ──────────────────────────────────────────────────
    path('api/tasks/<int:task_id>/comments/', CommentListCreateAPIView.as_view()),
    path('api/comments/<int:pk>/',            CommentDetailAPIView.as_view()),

    # ── Team ──────────────────────────────────────────────────────
    path('api/team-members/', TeamMemberListView.as_view()),

    # ── Attendance ────────────────────────────────────────────────
    path('api/attendance/check-in/',  CheckInView.as_view()),
    path('api/attendance/check-out/', CheckOutView.as_view()),
    path('api/attendance/',           AttendanceListView.as_view()),
    path('api/attendance/export/',    AttendanceCSVExportView.as_view()),
    path('api/attendance/pause/',     PauseWorkView.as_view()),
    path('api/attendance/resume/',    ResumeWorkView.as_view()),

    # ── Chat ──────────────────────────────────────────────────────
    path('api/group-chat/',       GroupChatListCreateView.as_view()),
    path('api/group-chat-clear/', GroupChatClearView.as_view()),

    # ── Activity — Electron desktop tracker ───────────────────────
    path('api/track-activity/', TrackActivityView.as_view()),

    # ── Activity — read endpoints ─────────────────────────────────
    path('api/activity/summary/',             ActivitySummaryView.as_view()),
    path('api/activity/team/',                TeamActivitySummaryView.as_view()),
    path('api/activity/logs/',                ActivityLogsView.as_view()),
    path('api/activity/member/<int:user_id>/', MemberActivityDetailView.as_view()),
    path('api/activity/history/',             ActivityHistoryView.as_view()),
    path('api/activity/leaderboard/',         AppTimeLeaderboardView.as_view()),
    path('api/activity/weekly-report/',       WeeklyActivityReportView.as_view()),
    path('api/activity/my-logs/',             MyActivityLogsView.as_view()),

    # ── Browser Activity (NEW) ────────────────────────────────────
    # Chrome Extension → Electron → POST here with JWT attached
    path('api/browser-activity/',       BrowserActivityView.as_view()),

    # Lead dashboard browser tab: GET ?user_id=X&date=YYYY-MM-DD
    path('api/browser-activity/list/',  BrowserActivityListView.as_view()),
]
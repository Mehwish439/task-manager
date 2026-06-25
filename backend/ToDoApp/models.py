from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta


class CustomUser(AbstractUser):
    ROLE_CHOICES = (('team_lead', 'Team Lead'), ('team_member', 'Team Member'),)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    def __str__(self): return self.username


class Task(models.Model):
    STATUS_CHOICES = (('in_progress','In Progress'),('testing','Testing'),('complete','Complete'),)
    title       = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ManyToManyField(CustomUser, blank=True, related_name='assigned_tasks')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_by  = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_tasks')
    start_date  = models.DateField(null=True, blank=True)
    end_date    = models.DateField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    attachment  = models.FileField(upload_to='task_files/', null=True, blank=True)
    def __str__(self): return self.title


class TaskStatus(models.Model):
    task       = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='statuses')
    user       = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_task_statuses')
    status     = models.CharField(max_length=20, choices=Task.STATUS_CHOICES, default='in_progress')
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: unique_together = ('task', 'user')
    def __str__(self): return f"{self.task.title} - {self.user.username} ({self.status})"


class Comment(models.Model):
    task       = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent     = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    class Meta: ordering = ['created_at']
    def __str__(self): return f'Comment by {self.author.username} on "{self.task.title}"'
    def is_reply(self): return self.parent is not None


class Attendance(models.Model):
    user             = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendance_records')
    system_check_in  = models.DateTimeField(default=timezone.now)
    system_check_out = models.DateTimeField(null=True, blank=True)
    manual_check_in  = models.TimeField(null=True, blank=True)
    manual_check_out = models.TimeField(null=True, blank=True)
    date             = models.DateField(default=timezone.now)
    created_at       = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.user.username} - {self.date}"

    @property
    def is_checked_out(self): return self.system_check_out is not None

    @property
    def total_break_time(self):
        total = sum(
            (b.break_end - b.break_start).total_seconds()
            for b in self.breaks.all() if b.break_end
        )
        return timedelta(seconds=total)

    @property
    def worked_hours(self):
        if not self.system_check_out or not self.system_check_in: return None
        total  = (self.system_check_out - self.system_check_in).total_seconds()
        worked = total - self.total_break_time.total_seconds()
        return round(worked / 3600, 2)

    @property
    def manual_difference_minutes(self):
        if self.manual_check_in and self.system_check_in:
            manual_dt = timezone.make_aware(datetime.combine(self.date, self.manual_check_in))
            return int(abs((self.system_check_in - manual_dt).total_seconds() / 60))
        return None


class Break(models.Model):
    attendance  = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name="breaks")
    break_start = models.DateTimeField()
    break_end   = models.DateTimeField(null=True, blank=True)
    def __str__(self): return f"Break for {self.attendance.user.username} on {self.attendance.date}"


class ChatMessage(models.Model):
    sender     = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['created_at']
    def __str__(self): return f"{self.sender.username}: {self.message[:20]}"


# ── Activity Tracking ─────────────────────────────────────────────

class EmployeeActivity(models.Model):
    """
    One row per segment logged by the Electron tracker.
    Also receives browser segments (identified by [Browser] prefix in window_title).
    """
    EVENT_TYPES   = (('idle', 'Idle'), ('active', 'Active'),)
    user          = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activity_logs')
    timestamp     = models.DateTimeField()
    ended_at      = models.DateTimeField(null=True, blank=True)
    event_type    = models.CharField(max_length=20, choices=EVENT_TYPES, default='active')
    active_window = models.CharField(max_length=255, blank=True, null=True)
    window_title  = models.CharField(max_length=500, blank=True, null=True)
    seconds       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.username} | {self.active_window} | {self.event_type} | {self.timestamp}"

    @property
    def is_browser(self):
        """Returns True if this segment came from the Chrome extension."""
        return bool(self.window_title and self.window_title.startswith('[Browser]'))


class AppTimeSession(models.Model):
    """Aggregated seconds per app per user per day."""
    user          = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='app_sessions')
    date          = models.DateField(default=timezone.now)
    app_name      = models.CharField(max_length=255)
    seconds_spent = models.PositiveIntegerField(default=0)
    last_seen     = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('user', 'date', 'app_name')
        ordering        = ['-date', '-seconds_spent']
    def __str__(self): return f"{self.user.username} | {self.app_name} | {self.date} | {self.seconds_spent}s"


class DailyActivitySummary(models.Model):
    """One row per user per day — pre-computed totals."""
    user                 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='daily_summaries')
    date                 = models.DateField(default=timezone.now)
    total_active_seconds = models.PositiveIntegerField(default=0)
    total_idle_seconds   = models.PositiveIntegerField(default=0)
    total_pings          = models.PositiveIntegerField(default=0)
    top_app              = models.CharField(max_length=255, blank=True, null=True)
    updated_at           = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('user', 'date')
        ordering        = ['-date']
    def __str__(self): return f"{self.user.username} | {self.date} | active={self.total_active_seconds}s"


# ── Browser Activity (NEW) ────────────────────────────────────────

class BrowserActivity(models.Model):
    """
    One row per browser URL visit.
    Sent from Chrome Extension → Electron bridge → Django.
    Stored separately so the dashboard can show a dedicated Browser tab
    with domain breakdown, page titles, and visit timestamps.

    NOTE: Browser visits are ALSO written to EmployeeActivity (with
    window_title prefixed '[Browser] ...') so the existing timeline
    and app totals work without any changes.
    """
    user          = models.ForeignKey(
                        CustomUser, on_delete=models.CASCADE,
                        related_name='browser_activity_logs'
                    )
    url           = models.CharField(max_length=2000)
    domain        = models.CharField(max_length=255, blank=True)
    title         = models.CharField(max_length=500, blank=True)
    timestamp     = models.DateTimeField()
    ended_at      = models.DateTimeField(null=True, blank=True)
    seconds       = models.PositiveIntegerField(default=0)
    activity_type = models.CharField(max_length=20, default='browser')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} | {self.domain} | {self.timestamp}"
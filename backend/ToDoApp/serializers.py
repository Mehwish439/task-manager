from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    CustomUser,
    Task,
    Comment,
    Attendance,
    Break,
    ChatMessage,
    EmployeeActivity,
    AppTimeSession,
    DailyActivitySummary,
    BrowserActivity,        # NEW
)
from datetime import timedelta
from django.utils import timezone


# =========================
# JWT TOKEN SERIALIZER
# =========================
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token


# =========================
# USER SERIALIZERS
# =========================
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'role']


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']


# =========================
# COMMENT SERIALIZERS
# =========================
class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'author_username', 'content', 'created_at', 'parent', 'replies']
        read_only_fields = ['author', 'created_at', 'task', 'replies']

    def validate(self, data):
        request = self.context.get('request')
        task = self.context.get('task') or (self.instance.task if self.instance else None)
        if not request or not task:
            return data
        user = request.user
        is_creator = task.created_by == user
        is_assigned = task.assigned_to.filter(id=user.id).exists()
        if not (is_creator or is_assigned):
            raise PermissionDenied("You are not allowed to comment on this task.")
        return data


# =========================
# TASK SERIALIZER
# =========================
class TaskSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    assigned_to = UserBasicSerializer(many=True, read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    attachment = serializers.FileField(read_only=True)
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'created_by',
            'assigned_to', 'start_date', 'end_date',
            'created_at', 'updated_at', 'attachment', 'attachment_url', 'comments'
        ]

    def get_comments(self, obj):
        top_level_comments = obj.comments.filter(parent__isnull=True)
        return CommentSerializer(top_level_comments, many=True, context=self.context).data

    def get_attachment_url(self, obj):
        request = self.context.get('request')
        if obj.attachment:
            return request.build_absolute_uri(obj.attachment.url)
        return None


# =========================
# BREAK SERIALIZER
# =========================
class BreakSerializer(serializers.ModelSerializer):
    start = serializers.SerializerMethodField()
    end   = serializers.SerializerMethodField()

    class Meta:
        model = Break
        fields = ['start', 'end']

    def get_start(self, obj):
        return timezone.localtime(obj.break_start).strftime("%H:%M")

    def get_end(self, obj):
        if obj.break_end:
            return timezone.localtime(obj.break_end).strftime("%H:%M")
        return None


# =========================
# ATTENDANCE SERIALIZER
# =========================
class AttendanceSerializer(serializers.ModelSerializer):
    user                      = serializers.CharField(source='user.username', read_only=True)
    role                      = serializers.CharField(source='user.role', read_only=True)
    worked_hours              = serializers.FloatField(read_only=True)
    manual_difference_minutes = serializers.IntegerField(read_only=True)
    total_break_hours         = serializers.SerializerMethodField()
    last_break_duration_minutes = serializers.SerializerMethodField()
    breaks                    = BreakSerializer(many=True, read_only=True)
    system_check_in           = serializers.SerializerMethodField()
    system_check_out          = serializers.SerializerMethodField()
    created_at                = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id', 'user', 'role', 'date', 'system_check_in', 'manual_check_in',
            'system_check_out', 'manual_check_out', 'worked_hours',
            'manual_difference_minutes', 'created_at',
            'total_break_hours', 'last_break_duration_minutes', 'breaks'
        ]
        read_only_fields = fields

    def get_system_check_in(self, obj):
        if obj.system_check_in:
            return timezone.localtime(obj.system_check_in).strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_system_check_out(self, obj):
        if obj.system_check_out:
            return timezone.localtime(obj.system_check_out).strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_created_at(self, obj):
        if obj.created_at:
            return timezone.localtime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_total_break_hours(self, obj):
        total_seconds = sum(
            ((b.break_end or timezone.now()) - b.break_start).total_seconds()
            for b in obj.breaks.all()
        )
        return round(total_seconds / 3600, 2)

    def get_last_break_duration_minutes(self, obj):
        last_break = obj.breaks.filter(break_end__isnull=False).last()
        if last_break:
            return round((last_break.break_end - last_break.break_start).total_seconds() / 60, 2)
        return 0


# =========================
# GROUP CHAT SERIALIZER
# =========================
class GroupChatSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender_username', 'message', 'created_at']


# =========================
# TASK CALENDAR SERIALIZER
# =========================
class TaskCalendarSerializer(serializers.ModelSerializer):
    assigned_to = UserBasicSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'start_date', 'end_date', 'assigned_to']


# =========================
# EMPLOYEE ACTIVITY SERIALIZER
# =========================
class EmployeeActivitySerializer(serializers.ModelSerializer):
    username   = serializers.CharField(source="user.username", read_only=True)
    is_browser = serializers.BooleanField(read_only=True)

    class Meta:
        model = EmployeeActivity
        fields = [
            "id", "user", "username",
            "active_window", "window_title",
            "event_type", "timestamp", "ended_at",
            "seconds", "is_browser",
        ]


# =========================
# APP TIME SESSION SERIALIZER
# =========================
class AppTimeSessionSerializer(serializers.ModelSerializer):
    time_formatted = serializers.SerializerMethodField()

    class Meta:
        model = AppTimeSession
        fields = ["id", "app_name", "seconds_spent", "time_formatted", "date", "last_seen"]

    def get_time_formatted(self, obj):
        total   = obj.seconds_spent
        hours   = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60
        if hours > 0:   return f"{hours}h {minutes}m"
        if minutes > 0: return f"{minutes}m {seconds}s"
        return f"{seconds}s"


# =========================
# DAILY ACTIVITY SUMMARY SERIALIZER
# =========================
class DailyActivitySummarySerializer(serializers.ModelSerializer):
    username             = serializers.CharField(source="user.username", read_only=True)
    active_time_formatted = serializers.SerializerMethodField()
    idle_time_formatted  = serializers.SerializerMethodField()
    active_percentage    = serializers.SerializerMethodField()

    class Meta:
        model = DailyActivitySummary
        fields = [
            "id", "username", "date",
            "total_active_seconds", "total_idle_seconds", "total_pings",
            "top_app", "active_time_formatted", "idle_time_formatted",
            "active_percentage", "updated_at",
        ]

    def _fmt(self, seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h}h {m}m" if h > 0 else f"{m}m"

    def get_active_time_formatted(self, obj): return self._fmt(obj.total_active_seconds)
    def get_idle_time_formatted(self, obj):   return self._fmt(obj.total_idle_seconds)

    def get_active_percentage(self, obj):
        total = obj.total_active_seconds + obj.total_idle_seconds
        if total == 0: return 0
        return round((obj.total_active_seconds / total) * 100, 1)


# =========================
# TEAM ACTIVITY SUMMARY SERIALIZER
# =========================
class TeamMemberActivitySerializer(serializers.Serializer):
    user_id              = serializers.IntegerField()
    username             = serializers.CharField()
    date                 = serializers.DateField()
    total_active_seconds = serializers.IntegerField()
    total_idle_seconds   = serializers.IntegerField()
    total_pings          = serializers.IntegerField()
    top_app              = serializers.CharField(allow_null=True)
    active_percentage    = serializers.FloatField()
    active_time_formatted = serializers.CharField()
    app_breakdown        = AppTimeSessionSerializer(many=True)


# =========================
# BROWSER ACTIVITY SERIALIZER  (NEW)
# =========================
class BrowserActivitySerializer(serializers.ModelSerializer):
    username     = serializers.CharField(source='user.username', read_only=True)
    time_formatted = serializers.SerializerMethodField()

    class Meta:
        model  = BrowserActivity
        fields = [
            'id', 'user', 'username',
            'url', 'domain', 'title',
            'timestamp', 'ended_at',
            'seconds', 'time_formatted',
            'activity_type',
        ]
        read_only_fields = ['id', 'username', 'time_formatted']

    def get_time_formatted(self, obj):
        s = obj.seconds
        h = s // 3600
        m = (s % 3600) // 60
        if h > 0: return f"{h}h {m}m"
        if m > 0: return f"{m}m {s % 60}s"
        return f"{s}s"
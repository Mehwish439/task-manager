from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import transaction
from .models import (
    CustomUser,
    Company,
    InviteCode,
    Task,
    Comment,
    Attendance,
    Break,
    ChatMessage,
    EmployeeActivity,
    AppTimeSession,
    DailyActivitySummary,
    BrowserActivity,
    ScreenshotActivity,
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
        token['company_id']   = user.company_id
        token['company_name'] = user.company.name if user.company else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        # super_admin has no company and always allowed in
        if user.role != 'super_admin':
            if not user.company:
                raise ValidationError('This account is not linked to a company.')
            if not user.company.is_active:
                raise ValidationError('Your company account has been suspended. Contact support.')
        return data


# =========================
# COMPANY SERIALIZERS
# =========================
class CompanySerializer(serializers.ModelSerializer):
    member_count   = serializers.IntegerField(read_only=True)
    lead_count     = serializers.IntegerField(read_only=True)
    employee_count = serializers.IntegerField(read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'plan', 'is_active', 'max_users',
            'owner', 'owner_username', 'member_count', 'lead_count',
            'employee_count', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'owner', 'created_at']


class InviteCodeSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    is_valid             = serializers.SerializerMethodField()

    class Meta:
        model = InviteCode
        fields = [
            'id', 'code', 'role', 'created_by', 'created_by_username',
            'created_at', 'expires_at', 'max_uses', 'uses',
            'is_active', 'is_valid',
        ]
        read_only_fields = ['id', 'code', 'created_by', 'created_at', 'uses', 'is_valid']

    def get_is_valid(self, obj):
        return obj.is_valid()


# =========================
# PUBLIC SIGNUP — creates a NEW COMPANY (first user = team_lead/owner)
# =========================
class CompanySignupSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=255)
    username     = serializers.CharField(max_length=150)
    email        = serializers.EmailField()
    password     = serializers.CharField(write_only=True, min_length=6)

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise ValidationError('That username is already taken.')
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise ValidationError('An account with that email already exists.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        company = Company.objects.create(name=validated_data['company_name'])
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='team_lead',
            company=company,
        )
        company.owner = user
        company.save(update_fields=['owner'])
        return user


# =========================
# PUBLIC JOIN — via invite code (employee or additional lead)
# =========================
class InviteJoinSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=12)
    username    = serializers.CharField(max_length=150)
    email       = serializers.EmailField()
    password    = serializers.CharField(write_only=True, min_length=6)

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise ValidationError('That username is already taken.')
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise ValidationError('An account with that email already exists.')
        return value

    def validate_invite_code(self, value):
        try:
            invite = InviteCode.objects.select_related('company').get(code=value.strip().upper())
        except InviteCode.DoesNotExist:
            raise ValidationError('Invalid invite code.')
        if not invite.is_valid():
            raise ValidationError('This invite code has expired or is no longer active.')
        if not invite.company.is_active:
            raise ValidationError('This company account is currently suspended.')
        if invite.company.members.count() >= invite.company.max_users:
            raise ValidationError('This company has reached its user limit. Contact your team lead.')
        self._invite = invite
        return value

    @transaction.atomic
    def create(self, validated_data):
        invite = self._invite
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=invite.role,
            company=invite.company,
        )
        invite.uses += 1
        if invite.max_uses and invite.uses >= invite.max_uses:
            invite.is_active = False
        invite.save(update_fields=['uses', 'is_active'])
        return user


# =========================
# INTERNAL REGISTER — used by a logged-in Team Lead's "Add New User" panel.
# Company is forced to request.user.company; a lead can only create users
# inside their own company. Public signup no longer uses this endpoint.
# =========================
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_role(self, value):
        if value not in ('team_lead', 'team_member'):
            raise ValidationError('Invalid role.')
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or request.user.role != 'team_lead':
            raise PermissionDenied('Only a team lead can add users this way.')
        company = request.user.company
        if not company:
            raise ValidationError('Your account is not linked to a company.')
        if company.members.count() >= company.max_users:
            raise ValidationError('User limit reached for your plan. Upgrade to add more users.')
        return CustomUser.objects.create_user(company=company, **validated_data)


# =========================
# USER SERIALIZERS
# =========================
class UserSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'role', 'company', 'company_name']


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

    # FIX: these were plain FloatField/IntegerField(read_only=True) with no
    # `source`/`get_*`, so DRF fell back to `getattr(obj, 'worked_hours')` and
    # `getattr(obj, 'manual_difference_minutes')` — i.e. whatever @property is
    # defined on the Attendance model. Right after check-in, system_check_out
    # is still None, and that property does arithmetic like
    # `(system_check_out - system_check_in).total_seconds()`, which raises
    # TypeError on None and produced an uncaught 500 on /attendance/check-in/.
    # Check-out never showed this because both timestamps are set by then.
    # Converted to SerializerMethodFields that compute the same values but
    # degrade to 0 / None instead of crashing when check-out hasn't happened.
    worked_hours              = serializers.SerializerMethodField()
    manual_difference_minutes = serializers.SerializerMethodField()

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

    def get_worked_hours(self, obj):
        # No check-out yet (fresh check-in) -> nothing worked out, return 0
        # instead of blowing up on `None - datetime`.
        if not obj.system_check_in or not obj.system_check_out:
            return 0.0
        total_break_seconds = sum(
            ((b.break_end or timezone.now()) - b.break_start).total_seconds()
            for b in obj.breaks.all()
        )
        worked_seconds = (obj.system_check_out - obj.system_check_in).total_seconds() - total_break_seconds
        return round(max(worked_seconds, 0) / 3600, 2)

    def get_manual_difference_minutes(self, obj):
        # Difference between manual (user-entered) and system check-in times,
        # in minutes. Falls back to None if either side is missing instead of
        # raising, and mirrors that same guard for check-out-based diffs.
        try:
            if obj.manual_check_in and obj.system_check_in:
                sys_local = timezone.localtime(obj.system_check_in).time()
                manual = obj.manual_check_in
                if hasattr(manual, 'hour'):
                    diff_seconds = (
                        (manual.hour * 3600 + manual.minute * 60 + manual.second)
                        - (sys_local.hour * 3600 + sys_local.minute * 60 + sys_local.second)
                    )
                    return int(diff_seconds / 60)
        except (TypeError, AttributeError):
            pass
        return 0

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
    username              = serializers.CharField(source="user.username", read_only=True)
    active_time_formatted = serializers.SerializerMethodField()
    idle_time_formatted   = serializers.SerializerMethodField()
    active_percentage     = serializers.SerializerMethodField()

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
    user_id               = serializers.IntegerField()
    username              = serializers.CharField()
    date                  = serializers.DateField()
    total_active_seconds  = serializers.IntegerField()
    total_idle_seconds    = serializers.IntegerField()
    total_pings           = serializers.IntegerField()
    top_app               = serializers.CharField(allow_null=True)
    active_percentage     = serializers.FloatField()
    active_time_formatted = serializers.CharField()
    app_breakdown         = AppTimeSessionSerializer(many=True)


# =========================
# BROWSER ACTIVITY SERIALIZER
# =========================
class BrowserActivitySerializer(serializers.ModelSerializer):
    username       = serializers.CharField(source='user.username', read_only=True)
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


# =========================
# SCREENSHOT ACTIVITY SERIALIZER
# =========================
class ScreenshotActivitySerializer(serializers.ModelSerializer):
    username  = serializers.CharField(source="user.username", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ScreenshotActivity
        fields = [
            "id", "user", "username",
            "image", "image_url",
            "timestamp", "created_at",
        ]
        read_only_fields = ["id", "created_at", "username", "image_url"]

    def get_image_url(self, obj):
        image = (obj.image or '').strip()
        if not image:
            return ''
        if image.startswith('data:') or image.startswith('http://') or image.startswith('https://'):
            return image
        if image.startswith('iVBOR'):
            return f'data:image/png;base64,{image}'
        elif image.startswith('/9j/'):
            return f'data:image/jpeg;base64,{image}'
        else:
            return f'data:image/png;base64,{image}'
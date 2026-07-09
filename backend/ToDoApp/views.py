from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.utils.dateparse import parse_datetime
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, date, time, timedelta
from django.db.models import Sum, Case, When, IntegerField, Count, Q
from django.db import IntegrityError
import csv, os
from calendar import monthrange
from django.http import HttpResponse, FileResponse
from io import BytesIO
import base64
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle,
        Paragraph, Spacer, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

from .models import (
    CustomUser, Company, InviteCode, Task, Comment, TaskStatus,
    Attendance, ChatMessage, Break,
    EmployeeActivity, AppTimeSession, DailyActivitySummary,
    BrowserActivity,
    ScreenshotActivity,
)
from .serializers import (
    RegisterSerializer, TaskSerializer, UserSerializer,
    MyTokenObtainPairSerializer, CommentSerializer,
    AttendanceSerializer, GroupChatSerializer, TaskCalendarSerializer,
    EmployeeActivitySerializer, AppTimeSessionSerializer,
    DailyActivitySummarySerializer,
    BrowserActivitySerializer,
    ScreenshotActivitySerializer,
    CompanySerializer, InviteCodeSerializer,
    CompanySignupSerializer, InviteJoinSerializer,
)

# =============================================================
# PERMISSIONS
# =============================================================
class IsTeamLead(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'team_lead')


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'super_admin')


def _company_of(request):
    """Company of the requesting user. super_admin has none (sees all)."""
    return request.user.company


def _scope_to_company(queryset, request, field='company'):
    """
    Filter a queryset to the requester's company unless they're a super_admin,
    in which case return everything unscoped.
    """
    if request.user.role == 'super_admin':
        return queryset
    return queryset.filter(**{field: request.user.company})


# =============================================================
# AUTH
# =============================================================
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class CustomTokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            return Response({'access': str(token.access_token)})
        except TokenError:
            return Response({'error': 'Invalid refresh token'}, status=401)


# =============================================================
# SIGNUP / ONBOARDING
# =============================================================
class CompanySignupView(APIView):
    """
    PUBLIC — first signup for a brand-new company.
    Creates the Company AND the first user as its team_lead/owner.
    POST { company_name, username, email, password }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CompanySignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': f'Company "{user.company.name}" created. You are now signed in as the Team Lead.',
            'username': user.username,
            'company':  user.company.name,
        }, status=201)


class InviteJoinView(APIView):
    """
    PUBLIC — join an existing company using an invite code shared by its lead.
    POST { invite_code, username, email, password }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InviteJoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': f'Joined "{user.company.name}" successfully as {user.role.replace("_"," ")}.',
            'username': user.username,
            'company':  user.company.name,
        }, status=201)


class RegisterView(generics.CreateAPIView):
    """
    INTERNAL — used by a logged-in Team Lead's "Add New User" panel.
    Forces the new user into request.user's company (see RegisterSerializer).
    """
    serializer_class   = RegisterSerializer
    permission_classes = [IsTeamLead]


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)

class TeamMemberListView(generics.ListAPIView):
    """All members of the requester's own company (leads + members)."""
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return CustomUser.objects.filter(role='team_member')
        return CustomUser.objects.filter(role='team_member', company=user.company)

class UpdateUserProfile(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request):
        user = request.user
        data = request.data
        try:
            if data.get('username', '').strip(): user.username = data['username'].strip()
            if data.get('email',    '').strip(): user.email    = data['email'].strip()
            if data.get('password', '').strip(): user.set_password(data['password'].strip())
            user.save()
            return Response({'username': user.username, 'email': user.email})
        except IntegrityError:
            return Response({'error': 'Username or email already exists.'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# =============================================================
# INVITE CODES (Team Lead manages invites for their own company)
# =============================================================
class InviteCodeListCreateView(generics.ListCreateAPIView):
    serializer_class   = InviteCodeSerializer
    permission_classes = [IsTeamLead]

    def get_queryset(self):
        return InviteCode.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        company = self.request.user.company
        if not company:
            raise PermissionDenied('Your account is not linked to a company.')
        serializer.save(company=company, created_by=self.request.user)


class InviteCodeToggleView(APIView):
    """POST to flip an invite code's active state (e.g. revoke it)."""
    permission_classes = [IsTeamLead]

    def post(self, request, invite_id):
        invite = get_object_or_404(InviteCode, id=invite_id, company=request.user.company)
        invite.is_active = not invite.is_active
        invite.save(update_fields=['is_active'])
        return Response(InviteCodeSerializer(invite).data)


# =============================================================
# TASKS
# =============================================================
class CreateTaskView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if request.user.role != 'team_lead':
            raise PermissionDenied('Only team leads can create tasks.')
        title           = request.data.get('title')
        description     = request.data.get('description')
        start_date      = request.data.get('start_date')
        end_date        = request.data.get('end_date')
        assigned_to_ids = request.data.get('assigned_to', [])
        attachment      = request.FILES.get('attachment')
        if not all([title, description, start_date, end_date]):
            return Response({'error': 'All fields except assignment are required.'}, status=400)
        task = Task.objects.create(
            title=title, description=description, created_by=request.user,
            start_date=start_date, end_date=end_date, attachment=attachment
        )
        if assigned_to_ids:
            # SECURITY: only assign users from the same company
            users = CustomUser.objects.filter(id__in=assigned_to_ids, company=request.user.company)
            task.assigned_to.set(users)
            for u in users:
                TaskStatus.objects.get_or_create(task=task, user=u)
        return Response({'message': 'Task created successfully', 'task_id': task.id}, status=201)

class TaskDeleteView(generics.DestroyAPIView):
    queryset           = Task.objects.all()
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_field       = 'id'
    def perform_destroy(self, instance):
        if instance.created_by != self.request.user:
            raise PermissionDenied('Only the creator can delete this task.')
        instance.delete()

class AssignTaskView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, task_id):
        if request.user.role != 'team_lead':
            raise PermissionDenied('Only team leads can assign tasks.')
        task  = get_object_or_404(Task, id=task_id, created_by=request.user)
        # SECURITY: only assign users from the same company
        users = CustomUser.objects.filter(id__in=request.data.get('assigned_to', []), company=request.user.company)
        task.assigned_to.add(*users)
        for u in users:
            TaskStatus.objects.get_or_create(task=task, user=u)
        return Response({'message': 'Users assigned successfully.'})

class AssignedTaskListView(generics.ListAPIView):
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)

class CreatedTaskListView(generics.ListAPIView):
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user).order_by('-start_date')

class TaskUpdateView(generics.UpdateAPIView):
    queryset           = Task.objects.all()
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_field       = 'id'
    def perform_update(self, serializer):
        task = self.get_object()
        user = self.request.user
        if task.created_by != user and user not in task.assigned_to.all():
            raise PermissionDenied('Not allowed to update this task.')
        serializer.save()

# =============================================================
# FILE DOWNLOAD
# =============================================================
class TaskFileDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        if request.user != task.created_by and request.user not in task.assigned_to.all():
            raise PermissionDenied('Not allowed.')
        if not task.attachment:
            return Response({'error': 'No file attached.'}, status=404)
        fp = task.attachment.path
        if not os.path.exists(fp):
            return Response({'error': 'File not found.'}, status=404)
        return FileResponse(open(fp, 'rb'), as_attachment=True, filename=os.path.basename(fp))

# =============================================================
# COMMENTS
# =============================================================
class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class   = CommentSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_id'], parent__isnull=True).order_by('created_at')
    def perform_create(self, serializer):
        task = get_object_or_404(Task, id=self.kwargs['task_id'])
        user = self.request.user
        if user != task.created_by and user not in task.assigned_to.all():
            raise PermissionDenied('Not allowed.')
        serializer.save(author=user, task=task)

class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = Comment.objects.all()
    serializer_class   = CommentSerializer
    permission_classes = [IsAuthenticated]
    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('You can only delete your own comments.')
        instance.delete()

# =============================================================
# TASK STATUS
# =============================================================
class TaskStatusBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task     = get_object_or_404(Task, id=task_id)
        statuses = TaskStatus.objects.filter(task=task)
        return Response({'statuses': [
            {'id': s.id, 'user': s.user.username, 'email': s.user.email, 'status': s.status}
            for s in statuses
        ]})

    def patch(self, request, task_id):
        task         = get_object_or_404(Task, id=task_id)
        status_value = request.data.get('status', '').strip().lower()
        if status_value not in ['pending', 'in_progress', 'complete']:
            return Response({'error': 'Invalid status.'}, status=400)
        TaskStatus.objects.update_or_create(task=task, user=request.user, defaults={'status': status_value})
        all_s = TaskStatus.objects.filter(task=task)
        if all(s.status == 'complete' for s in all_s):
            task.status = 'complete'
        elif any(s.status == 'in_progress' for s in all_s):
            task.status = 'in_progress'
        else:
            task.status = 'pending'
        task.save()
        return Response({'message': f'Status updated to "{status_value}".', 'overall_task_status': task.status})

# =============================================================
# ATTENDANCE
# =============================================================
class CheckInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        today = timezone.localdate()
        if Attendance.objects.filter(user=request.user, date=today).exists():
            return Response({'error': 'Already checked in today.'}, status=400)
        att = Attendance.objects.create(
            user=request.user,
            date=today,
            system_check_in=timezone.now(),
            manual_check_in=request.data.get('manual_check_in'),
        )
        # DEFENSIVE: the check-in write above has already succeeded at this
        # point. Serialization is a separate concern — if it ever throws
        # again (e.g. a future field addition with a bad model property), we
        # must not turn a successful check-in into a 500. Log it, degrade to
        # a minimal payload, and still report success.
        try:
            att_data = AttendanceSerializer(att, context={'request': request}).data
        except Exception:
            logger.exception('AttendanceSerializer failed after successful check-in for user %s', request.user.id)
            att_data = {
                'id': att.id,
                'date': str(att.date),
                'system_check_in': timezone.localtime(att.system_check_in).strftime("%Y-%m-%d %H:%M:%S"),
            }
        return Response({
            'message': 'Checked in',
            'attendance': att_data
        })

class CheckOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        today = timezone.localdate()
        att = Attendance.objects.filter(
            user=request.user,
            date=today,
            system_check_out__isnull=True
        ).last()
        if not att:
            # FIX: distinguish "never checked in today" from "already checked out
            # today" instead of returning the same ambiguous error for both. This
            # was the source of confusing messages when a double-submitted
            # check-out request (e.g. from a fast double-click) hit this branch
            # after the first request had already completed successfully.
            already_checked_out = Attendance.objects.filter(
                user=request.user, date=today, system_check_out__isnull=False
            ).exists()
            if already_checked_out:
                return Response({'error': 'You have already checked out today.'}, status=400)
            return Response({'error': 'No active check-in for today.'}, status=400)
        att.system_check_out = timezone.now()
        if request.data.get('manual_check_out'):
            att.manual_check_out = request.data['manual_check_out']
        att.save()
        try:
            att_data = AttendanceSerializer(att, context={'request': request}).data
        except Exception:
            logger.exception('AttendanceSerializer failed after successful check-out for user %s', request.user.id)
            att_data = {
                'id': att.id,
                'date': str(att.date),
                'system_check_out': timezone.localtime(att.system_check_out).strftime("%Y-%m-%d %H:%M:%S"),
            }
        return Response({
            'message': 'Checked out',
            'attendance': att_data
        })

class AttendanceListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.role != 'team_lead':
            raise PermissionDenied('Only team leads.')
        records = Attendance.objects.select_related('user').filter(
            user__company=request.user.company
        ).order_by('-date')
        return Response(AttendanceSerializer(records, many=True).data)

class AttendanceCSVExportView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.role != 'team_lead':
            raise PermissionDenied('Only team leads.')
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="attendance.csv"'
        writer = csv.writer(resp)
        writer.writerow(['User','Date','Clock In','Clock Out','Worked Hours'])
        records = Attendance.objects.select_related('user').filter(user__company=request.user.company)
        for att in records:
            writer.writerow([att.user.username, att.date, att.system_check_in, att.system_check_out, att.worked_hours or 0])
        return resp

class MyAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = (
            Attendance.objects
            .filter(user=request.user)
            .prefetch_related('breaks')
            .order_by('-date')[:30]
        )
        return Response(
            AttendanceSerializer(records, many=True, context={'request': request}).data
        )

class PauseWorkView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        today = timezone.localdate()
        att   = Attendance.objects.filter(user=request.user, date=today, system_check_out__isnull=True).last()
        if not att: return Response({'error': 'No active session'}, status=400)
        Break.objects.create(attendance=att, break_start=timezone.now())
        return Response({'message': 'Break started'})

class ResumeWorkView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        today      = timezone.localdate()
        att        = Attendance.objects.filter(user=request.user, date=today, system_check_out__isnull=True).last()
        if not att: return Response({'error': 'No active session'}, status=400)
        last_break = Break.objects.filter(attendance=att, break_end__isnull=True).last()
        if not last_break: return Response({'error': 'No active break'}, status=400)
        last_break.break_end = timezone.now()
        last_break.save()
        return Response({'message': 'Work resumed'})

# =============================================================
# CHAT — scoped to the user's company
# =============================================================
class GroupChatListCreateView(generics.ListCreateAPIView):
    serializer_class   = GroupChatSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return ChatMessage.objects.filter(company=self.request.user.company).order_by('created_at')
    def perform_create(self, serializer):
        msg = self.request.data.get('message', '').strip()
        if msg:
            serializer.save(sender=self.request.user, company=self.request.user.company, message=msg)

class GroupChatClearView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if request.user.role != 'team_lead':
            return Response({'error': 'Only team leads can clear chat.'}, status=403)
        ChatMessage.objects.filter(company=request.user.company).delete()
        return Response({'status': 'cleared'})

# =============================================================
# CALENDAR
# =============================================================
class TaskCalendarView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        now   = timezone.now()
        month = int(request.query_params.get('month', now.month))
        year  = int(request.query_params.get('year',  now.year))
        first = date(year, month, 1)
        last  = date(year, month, monthrange(year, month)[1])
        if request.user.role == 'team_lead':
            tasks = Task.objects.filter(created_by=request.user, start_date__lte=last, end_date__gte=first)
        else:
            tasks = Task.objects.filter(assigned_to=request.user, start_date__lte=last, end_date__gte=first)
        return Response(TaskCalendarSerializer(tasks.prefetch_related('assigned_to').distinct(), many=True).data)

# =============================================================
# HELPERS
# =============================================================
def _fmt(s):
    s = int(s or 0)
    h = s // 3600
    m = (s % 3600) // 60
    return f'{h}h {m}m' if h > 0 else f'{m}m'


def _day_bounds(target_date):
    tz       = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(target_date, time.min), tz)
    end_dt   = timezone.make_aware(datetime.combine(target_date, time.max), tz)
    return start_dt, end_dt


def _compute_daily_totals(user, target_date):
    start_dt, end_dt = _day_bounds(target_date)
    logs = (
        EmployeeActivity.objects
        .filter(user=user, timestamp__gte=start_dt, timestamp__lte=end_dt)
        .order_by('timestamp')
    )
    agg = logs.aggregate(
        active=Sum(Case(When(event_type='active', then='seconds'), default=0, output_field=IntegerField())),
        idle=Sum(Case(When(event_type='idle', then='seconds'), default=0, output_field=IntegerField())),
    )
    total_active = agg['active'] or 0
    total_idle   = agg['idle']   or 0
    return total_active, total_idle, logs


def _sync_daily_summary(user, target_date, total_active=None, total_idle=None, logs=None):
    if total_active is None or total_idle is None or logs is None:
        total_active, total_idle, logs = _compute_daily_totals(user, target_date)

    summary, _ = DailyActivitySummary.objects.get_or_create(user=user, date=target_date)
    summary.total_active_seconds = total_active
    summary.total_idle_seconds   = total_idle

    app_totals = {}
    for l in logs:
        if l.event_type == 'active':
            app_totals[l.active_window] = app_totals.get(l.active_window, 0) + l.seconds

    for app_name, seconds in app_totals.items():
        sess, _ = AppTimeSession.objects.get_or_create(user=user, date=target_date, app_name=app_name)
        sess.seconds_spent = seconds
        sess.save(update_fields=['seconds_spent', 'last_seen'])

    summary.top_app = max(app_totals, key=app_totals.get) if app_totals else None
    summary.save(update_fields=['total_active_seconds', 'total_idle_seconds', 'top_app'])
    return summary

# =============================================================
# TRACK ACTIVITY
# =============================================================
class TrackActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logs = request.data.get('logs', [])
        if not logs or not isinstance(logs, list):
            return Response({'error': 'logs array required'}, status=400)

        rows_to_create = []
        per_date_dates = set()

        for entry in logs:
            app_name  = (entry.get('app')   or '').strip() or 'System'
            win_title = (entry.get('title') or '').strip() or app_name
            ev_type   = entry.get('type', 'active')
            if ev_type not in ('active', 'idle'):
                ev_type = 'active'
            seconds = int(entry.get('seconds') or 0)
            if seconds <= 0:
                continue

            from_ts = entry.get('from_ts')
            to_ts   = entry.get('to_ts')
            try:
                from_dt = datetime.fromisoformat(from_ts.replace('Z', '+00:00')) if from_ts else timezone.now()
                to_dt   = datetime.fromisoformat(to_ts.replace('Z', '+00:00'))   if to_ts   else timezone.now()
            except (ValueError, AttributeError):
                from_dt = timezone.now()
                to_dt   = timezone.now()

            entry_date = timezone.localtime(from_dt).date()
            per_date_dates.add(entry_date)

            rows_to_create.append(EmployeeActivity(
                user          = request.user,
                event_type    = ev_type,
                active_window = app_name,
                window_title  = win_title,
                seconds       = seconds,
                timestamp     = from_dt,
                ended_at      = to_dt,
            ))

        if rows_to_create:
            EmployeeActivity.objects.bulk_create(rows_to_create)

        for d in per_date_dates:
            _sync_daily_summary(request.user, d)

        return Response({
            'status':        'ok',
            'saved':         len(rows_to_create),
            'dates_updated': len(per_date_dates),
        }, status=201)

# =============================================================
# ACTIVITY LOGS (lead only, own company)
# =============================================================
class ActivityLogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'team_lead':
            raise PermissionDenied('Only team leads.')

        uid = request.query_params.get('user_id')
        dp  = request.query_params.get('date')
        if not uid:
            return Response({'error': 'user_id required'}, status=400)

        target_date = timezone.localdate()
        if dp:
            try:
                target_date = datetime.strptime(dp, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date'}, status=400)

        member = get_object_or_404(CustomUser, id=uid, company=request.user.company)
        total_active, total_idle, logs = _compute_daily_totals(member, target_date)
        total_all = total_active + total_idle

        rows = []
        app_totals = {}
        for l in logs:
            local_from = timezone.localtime(l.timestamp)
            local_to   = timezone.localtime(l.ended_at) if l.ended_at else local_from
            rows.append({
                'id':         l.id,
                'app':        l.active_window,
                'title':      l.window_title or l.active_window,
                'type':       l.event_type,
                'is_browser': l.is_browser,
                'from_time':  local_from.strftime('%H:%M:%S'),
                'to_time':    local_to.strftime('%H:%M:%S'),
                'duration':   _fmt(l.seconds),
                'seconds':    l.seconds,
            })
            if l.event_type == 'active':
                app_totals[l.active_window] = app_totals.get(l.active_window, 0) + l.seconds

        app_breakdown = sorted(
            [{'app': k, 'seconds': v, 'duration': _fmt(v)} for k, v in app_totals.items()],
            key=lambda x: -x['seconds']
        )

        return Response({
            'date':          str(target_date),
            'total_active':  _fmt(total_active),
            'total_idle':    _fmt(total_idle),
            'total_tracked': _fmt(total_all),
            'active_pct':    round((total_active / total_all) * 100, 1) if total_all else 0,
            'app_breakdown': app_breakdown,
            'timeline':      rows,
        })

# =============================================================
# ACTIVITY SUMMARY
# =============================================================
class ActivitySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dp = request.query_params.get('date')
        target_date = timezone.localdate()
        if dp:
            try:
                target_date = datetime.strptime(dp, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date'}, status=400)

        user = request.user
        uid  = request.query_params.get('user_id')
        if uid and user.role == 'team_lead':
            user = get_object_or_404(CustomUser, id=uid, company=request.user.company)

        total_active, total_idle, _logs = _compute_daily_totals(user, target_date)
        summary = _sync_daily_summary(user, target_date, total_active, total_idle, _logs)
        summary_data = DailyActivitySummarySerializer(summary).data

        apps = AppTimeSession.objects.filter(user=user, date=target_date).order_by('-seconds_spent')

        return Response({
            'user':          user.username,
            'date':          target_date,
            'summary':       summary_data,
            'app_breakdown': AppTimeSessionSerializer(apps, many=True).data,
        })

# =============================================================
# TEAM ACTIVITY SUMMARY (own company only)
# =============================================================
class TeamActivitySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'team_lead':
            raise PermissionDenied('Only team leads.')

        target_date = timezone.localdate()
        if dp := request.query_params.get('date'):
            try:
                target_date = datetime.strptime(dp, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date'}, status=400)

        is_today      = (target_date == timezone.localdate())
        recent_cutoff = timezone.now() - timedelta(minutes=2)
        members       = CustomUser.objects.filter(role='team_member', company=request.user.company)
        result        = []

        for member in members:
            active_s, idle_s, _logs = _compute_daily_totals(member, target_date)
            top_app = (
                AppTimeSession.objects
                .filter(user=member, date=target_date)
                .order_by('-seconds_spent')
                .values_list('app_name', flat=True)
                .first()
            )

            total_s    = active_s + idle_s
            active_pct = round((active_s / total_s) * 100, 1) if total_s else 0.0

            is_tracking = is_idle_now = False
            if is_today:
                last = (
                    EmployeeActivity.objects
                    .filter(user=member, timestamp__gte=recent_cutoff)
                    .order_by('-timestamp').first()
                )
                if last:
                    is_tracking = True
                    is_idle_now = (last.event_type == 'idle')

            result.append({
                'user_id':               member.id,
                'username':              member.username,
                'date':                  str(target_date),
                'total_active_seconds':  active_s,
                'total_idle_seconds':    idle_s,
                'top_app':               top_app,
                'active_percentage':     active_pct,
                'active_time_formatted': _fmt(active_s),
                'idle_time_formatted':   _fmt(idle_s),
                'is_tracking':           is_tracking,
                'is_idle':               is_idle_now,
            })

        return Response({'date': str(target_date), 'team': result})

# =============================================================
# MEMBER ACTIVITY DETAIL (own company only)
# =============================================================
class MemberActivityDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.role != 'team_lead':
            raise PermissionDenied('Only team leads.')

        member      = get_object_or_404(CustomUser, id=user_id, role='team_member', company=request.user.company)
        target_date = timezone.localdate()
        if dp := request.query_params.get('date'):
            try:
                target_date = datetime.strptime(dp, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date'}, status=400)

        total_active, total_idle, logs = _compute_daily_totals(member, target_date)
        summary = _sync_daily_summary(member, target_date, total_active, total_idle, logs)
        summary_data = DailyActivitySummarySerializer(summary).data

        timeline = []
        app_totals = {}
        for l in logs:
            local_from = timezone.localtime(l.timestamp)
            local_to   = timezone.localtime(l.ended_at) if l.ended_at else local_from
            timeline.append({
                'id':         l.id,
                'app':        l.active_window,
                'title':      l.window_title or l.active_window,
                'type':       l.event_type,
                'is_browser': l.is_browser,
                'from_time':  local_from.strftime('%H:%M:%S'),
                'to_time':    local_to.strftime('%H:%M:%S'),
                'duration':   _fmt(l.seconds),
                'seconds':    l.seconds,
            })
            if l.event_type == 'active':
                app_totals[l.active_window] = app_totals.get(l.active_window, 0) + l.seconds

        total_all = total_active + total_idle
        app_breakdown = sorted(
            [{'app': k, 'seconds': v, 'duration': _fmt(v)} for k, v in app_totals.items()],
            key=lambda x: -x['seconds']
        )

        return Response({
            'user_id':       member.id,
            'username':      member.username,
            'date':          str(target_date),
            'summary':       summary_data,
            'total_active':  _fmt(total_active),
            'total_idle':    _fmt(total_idle),
            'total_tracked': _fmt(total_all),
            'active_pct':    round((total_active / total_all) * 100, 1) if total_all else 0,
            'app_breakdown': app_breakdown,
            'timeline':      timeline,
        })

# =============================================================
# ACTIVITY HISTORY
# =============================================================
class ActivityHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = min(int(request.query_params.get('days', 7)), 90)
        user = request.user
        if (uid := request.query_params.get('user_id')) and user.role == 'team_lead':
            user = get_object_or_404(CustomUser, id=uid, company=request.user.company)
        summaries = DailyActivitySummary.objects.filter(user=user).order_by('-date')[:days]
        return Response({
            'user':           user.username,
            'days_requested': days,
            'history':        DailyActivitySummarySerializer(summaries, many=True).data,
        })

# =============================================================
# APP TIME LEADERBOARD (own company only)
# =============================================================
class AppTimeLeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'team_lead':
            raise PermissionDenied('Only team leads.')
        target_date = timezone.localdate()
        if dp := request.query_params.get('date'):
            try:
                target_date = datetime.strptime(dp, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date'}, status=400)

        rows = (
            AppTimeSession.objects
            .filter(date=target_date, user__company=request.user.company)
            .values('app_name')
            .annotate(total_seconds=Sum('seconds_spent'))
            .order_by('-total_seconds')[:20]
        )
        return Response({
            'date':     str(target_date),
            'top_apps': [
                {'app_name': r['app_name'], 'total_seconds': r['total_seconds'],
                 'time_formatted': _fmt(r['total_seconds'])}
                for r in rows
            ],
        })

# =============================================================
# WEEKLY PDF REPORT (own company only)
# =============================================================
class WeeklyActivityReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not REPORTLAB_OK:
            return Response({'error': 'reportlab not installed.'}, status=500)

        end_date   = timezone.localdate() - timedelta(days=1)
        start_date = end_date - timedelta(days=6)
        if sp := request.query_params.get('start'):
            try:
                start_date = datetime.strptime(sp, '%Y-%m-%d').date()
                end_date   = start_date + timedelta(days=6)
            except ValueError:
                pass

        uid = request.query_params.get('user_id')
        if uid and request.user.role == 'team_lead':
            members = [get_object_or_404(CustomUser, id=uid, company=request.user.company)]
        elif request.user.role == 'team_lead':
            members = list(CustomUser.objects.filter(role='team_member', company=request.user.company))
        else:
            members = [request.user]

        buffer = BytesIO()
        doc    = SimpleDocTemplate(buffer, pagesize=A4,
                                   rightMargin=2*cm, leftMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story  = []
        date_range = [start_date + timedelta(days=i) for i in range(7)]

        company_name = request.user.company.name if request.user.company else 'QRM'
        story.append(Paragraph(f'{company_name} Weekly Activity Report',
                                ParagraphStyle('T', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER)))
        story.append(Paragraph(f'{start_date.strftime("%d %b %Y")} – {end_date.strftime("%d %b %Y")}',
                                ParagraphStyle('S', parent=styles['Normal'], fontSize=10,
                                               textColor=colors.grey, alignment=TA_CENTER)))
        story.append(Spacer(1, 0.4*cm))
        story.append(HRFlowable(width='100%', thickness=0.5, color=colors.lightgrey))
        story.append(Spacer(1, 0.4*cm))

        for member in members:
            story.append(Paragraph(f'Employee: {member.username}',
                                    ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13,
                                                   spaceBefore=14, spaceAfter=4)))

            rows = [['Date', 'Active', 'Idle', 'Active %', 'Top App']]
            wa = wi = 0
            for d in date_range:
                active_s, idle_s, _logs = _compute_daily_totals(member, d)
                if active_s or idle_s:
                    tot = active_s + idle_s
                    pct = round(active_s / tot * 100, 1) if tot else 0
                    top_app = (
                        AppTimeSession.objects
                        .filter(user=member, date=d)
                        .order_by('-seconds_spent')
                        .values_list('app_name', flat=True)
                        .first()
                    )
                    rows.append([d.strftime('%a %d %b'), _fmt(active_s),
                                  _fmt(idle_s), f'{pct}%', top_app or '—'])
                    wa += active_s
                    wi += idle_s
                else:
                    rows.append([d.strftime('%a %d %b'), '—', '—', '—', '—'])
            wt  = wa + wi
            rows.append(['TOTAL', _fmt(wa), _fmt(wi),
                          f'{round(wa/wt*100,1)}%' if wt else '0%', ''])

            t = Table(rows, colWidths=[3*cm, 3.2*cm, 3.2*cm, 2.8*cm, 4.8*cm], repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0),(-1,0), colors.HexColor('#159aff')),
                ('TEXTCOLOR',  (0,0),(-1,0), colors.white),
                ('FONTNAME',   (0,0),(-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',   (0,0),(-1,-1), 9),
                ('ALIGN',      (1,0),(3,-1), 'CENTER'),
                ('ROWBACKGROUNDS',(0,1),(-1,-2),[colors.white, colors.HexColor('#f5f8ff')]),
                ('BACKGROUND', (0,-1),(-1,-1), colors.HexColor('#e8f5e9')),
                ('FONTNAME',   (0,-1),(-1,-1), 'Helvetica-Bold'),
                ('GRID',       (0,0),(-1,-1), 0.4, colors.HexColor('#dddddd')),
                ('TOPPADDING', (0,0),(-1,-1), 5),
                ('BOTTOMPADDING',(0,0),(-1,-1), 5),
            ]))
            story.append(t)
            story.append(Spacer(1, 1*cm))

        doc.build(story)
        buffer.seek(0)
        resp = HttpResponse(buffer, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="weekly-report-{start_date}.pdf"'
        return resp

# =============================================================
# MY ACTIVITY LOGS — employee endpoint (raw seconds)
# =============================================================
class MyActivityLogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dp = request.query_params.get('date')
        target_date = timezone.localdate()
        if dp:
            try:
                target_date = datetime.strptime(dp, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date'}, status=400)

        total_active, total_idle, logs = _compute_daily_totals(request.user, target_date)
        total_all = total_active + total_idle

        timeline = []
        app_totals = {}
        for l in logs:
            local_from = timezone.localtime(l.timestamp)
            local_to   = timezone.localtime(l.ended_at) if l.ended_at else local_from
            timeline.append({
                'id':         l.id,
                'app':        l.active_window or 'System',
                'title':      l.window_title or l.active_window or 'System',
                'type':       l.event_type,
                'is_browser': l.is_browser,
                'from_time':  local_from.strftime('%H:%M:%S'),
                'to_time':    local_to.strftime('%H:%M:%S'),
                'duration':   _fmt(l.seconds),
                'seconds':    l.seconds,
            })
            if l.event_type == 'active':
                app_totals[l.active_window or 'System'] = (
                    app_totals.get(l.active_window or 'System', 0) + l.seconds
                )

        app_breakdown = sorted(
            [{'app': k, 'seconds': v, 'duration': _fmt(v)} for k, v in app_totals.items()],
            key=lambda x: -x['seconds']
        )

        return Response({
            'date':                 str(target_date),
            'total_active_seconds': total_active,
            'total_idle_seconds':   total_idle,
            'total_active':         _fmt(total_active),
            'total_idle':           _fmt(total_idle),
            'total_tracked':        _fmt(total_all),
            'active_pct':           round((total_active / total_all) * 100, 1) if total_all else 0,
            'app_breakdown':        app_breakdown,
            'timeline':             timeline,
        })

# =============================================================
# MY TRACK STATUS
# =============================================================
class MyTrackStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recent_cutoff = timezone.now() - timedelta(minutes=2)
        last = (
            EmployeeActivity.objects
            .filter(user=request.user, timestamp__gte=recent_cutoff)
            .order_by('-timestamp')
            .first()
        )
        is_tracking = last is not None
        is_idle     = (last.event_type == 'idle') if last else False
        return Response({
            'is_tracking': is_tracking,
            'is_idle':     is_idle,
        })

# =============================================================
# BROWSER ACTIVITY — POST
# =============================================================
class BrowserActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logs = request.data.get('logs', [])
        if not logs or not isinstance(logs, list):
            return Response({'error': 'logs array required'}, status=400)

        created = 0
        for entry in logs:
            raw_title = (entry.get('title') or '').strip()
            app_name  = (entry.get('app')   or '').strip() or 'Browser'
            full_url  = (entry.get('url')   or '').strip()
            seconds   = int(entry.get('seconds') or 0)

            if seconds <= 0:
                continue

            from_ts = entry.get('from_ts')
            to_ts   = entry.get('to_ts')
            try:
                from_dt = datetime.fromisoformat(from_ts.replace('Z', '+00:00')) if from_ts else timezone.now()
                to_dt   = datetime.fromisoformat(to_ts.replace('Z', '+00:00'))   if to_ts   else timezone.now()
            except (ValueError, AttributeError):
                from_dt = timezone.now()
                to_dt   = timezone.now()

            clean_title = raw_title.replace('[Browser] ', '', 1) if raw_title.startswith('[Browser] ') else raw_title

            BrowserActivity.objects.create(
                user          = request.user,
                url           = full_url or app_name,
                domain        = app_name,
                title         = clean_title,
                timestamp     = from_dt,
                ended_at      = to_dt,
                seconds       = seconds,
                activity_type = 'browser',
            )
            created += 1

        return Response({'status': 'ok', 'saved': created}, status=201)

# =============================================================
# BROWSER ACTIVITY LIST — lead dashboard (own company only)
# =============================================================
class BrowserActivityListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'team_lead':
            raise PermissionDenied('Only team leads.')

        uid = request.query_params.get('user_id')
        dp  = request.query_params.get('date')
        if not uid:
            return Response({'error': 'user_id required'}, status=400)

        # SECURITY: ensure target user belongs to the same company
        get_object_or_404(CustomUser, id=uid, company=request.user.company)

        target_date = timezone.localdate()
        if dp:
            try:
                target_date = datetime.strptime(dp, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date'}, status=400)

        start_dt, end_dt = _day_bounds(target_date)
        logs = (
            BrowserActivity.objects
            .filter(user_id=uid, timestamp__gte=start_dt, timestamp__lte=end_dt)
            .order_by('timestamp')
        )

        domain_totals = {}
        for l in logs:
            domain_totals[l.domain] = domain_totals.get(l.domain, 0) + l.seconds

        domain_breakdown = sorted(
            [{'domain': k, 'seconds': v, 'duration': _fmt(v)} for k, v in domain_totals.items()],
            key=lambda x: -x['seconds']
        )
        total_s = sum(domain_totals.values())

        visits = []
        for l in logs:
            local_time = timezone.localtime(l.timestamp)
            try:
                parsed   = urlparse(l.url)
                sub_path = parsed.path
                if parsed.query:
                    sub_path += '?' + parsed.query
                if not sub_path or sub_path == '/':
                    sub_path = ''
            except Exception:
                sub_path = ''

            visits.append({
                'id':             l.id,
                'domain':         l.domain,
                'url':            l.url,
                'sub_path':       sub_path,
                'title':          l.title,
                'timestamp':      l.timestamp.isoformat(),
                'time':           local_time.strftime('%H:%M:%S'),
                'seconds':        l.seconds,
                'time_formatted': _fmt(l.seconds),
            })

        return Response({
            'date':             str(target_date),
            'total_browser_s':  total_s,
            'total_browser':    _fmt(total_s),
            'domain_breakdown': domain_breakdown,
            'visits':           visits,
        })

# =============================================================
# MY BROWSER ACTIVITY — employee dashboard
# =============================================================
class MyBrowserActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dp = request.query_params.get('date')
        target_date = timezone.localdate()
        if dp:
            try:
                target_date = datetime.strptime(dp, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date'}, status=400)

        start_dt, end_dt = _day_bounds(target_date)
        logs = (
            BrowserActivity.objects
            .filter(user=request.user, timestamp__gte=start_dt, timestamp__lte=end_dt)
            .order_by('timestamp')
        )

        domain_totals = {}
        for l in logs:
            domain_totals[l.domain] = domain_totals.get(l.domain, 0) + l.seconds

        domain_breakdown = sorted(
            [{'domain': k, 'seconds': v, 'duration': _fmt(v)} for k, v in domain_totals.items()],
            key=lambda x: -x['seconds']
        )
        total_s = sum(domain_totals.values())

        visits = []
        for l in logs:
            local_time = timezone.localtime(l.timestamp)
            try:
                parsed   = urlparse(l.url)
                sub_path = parsed.path
                if parsed.query:
                    sub_path += '?' + parsed.query
                if not sub_path or sub_path == '/':
                    sub_path = ''
            except Exception:
                sub_path = ''
            visits.append({
                'id':             l.id,
                'domain':         l.domain,
                'url':            l.url,
                'sub_path':       sub_path,
                'title':          l.title,
                'timestamp':      l.timestamp.isoformat(),
                'time':           local_time.strftime('%H:%M:%S'),
                'seconds':        l.seconds,
                'time_formatted': _fmt(l.seconds),
            })

        return Response({
            'date':             str(target_date),
            'total_browser_s':  total_s,
            'total_browser':    _fmt(total_s),
            'domain_breakdown': domain_breakdown,
            'visits':           visits,
        })

# =============================================================
# SCREENSHOT ACTIVITY
# =============================================================
class ScreenshotActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user    = request.user
        user_id = request.query_params.get('user_id')
        dp      = request.query_params.get('date')

        if user.role == 'team_lead' and user_id:
            # SECURITY: only view screenshots of users in the same company
            target_user = get_object_or_404(CustomUser, id=user_id, company=user.company)
        else:
            target_user = user

        target_date = timezone.localdate()
        if dp:
            try:
                target_date = datetime.strptime(dp, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        start_dt, end_dt = _day_bounds(target_date)

        queryset = (
            ScreenshotActivity.objects
            .filter(user=target_user, timestamp__gte=start_dt, timestamp__lte=end_dt)
            .order_by('timestamp')
        )

        serializer = ScreenshotActivitySerializer(queryset, many=True)
        return Response({
            'user_id':     target_user.id,
            'username':    target_user.username,
            'date':        str(target_date),
            'count':       queryset.count(),
            'screenshots': serializer.data,
        })

    def post(self, request):
        logs = request.data.get('logs', [])
        if not isinstance(logs, list):
            return Response({'error': 'logs must be a list'}, status=400)

        today = timezone.localdate()
        existing_count = ScreenshotActivity.objects.filter(
            user=request.user,
            timestamp__date=today
        ).count()

        saved   = 0
        skipped = 0

        for item in logs:
            image     = item.get('image')
            timestamp = item.get('timestamp')

            if not image or not timestamp:
                skipped += 1
                continue

            if existing_count + saved >= 8:
                skipped += 1
                continue

            dt = parse_datetime(timestamp)
            if dt is None:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    dt = timezone.now()

            ScreenshotActivity.objects.create(
                user      = request.user,
                image     = image,
                timestamp = dt,
            )
            saved          += 1
            existing_count += 1

        return Response({
            'status':  'ok',
            'saved':   saved,
            'skipped': skipped,
        }, status=201)


# =============================================================
# SUPER ADMIN — sees across ALL companies
# =============================================================
class SuperAdminCompanyListView(generics.ListAPIView):
    """List every company on the platform with member counts."""
    serializer_class   = CompanySerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return Company.objects.annotate(
            member_count_annot=Count('members', distinct=True)
        ).order_by('-created_at')


class SuperAdminCompanyDetailView(APIView):
    """
    Company detail + a richer per-user breakdown for the super admin drawer:
    - live status (online / idle / offline), based on activity in the last 2 min
    - task load (assigned / completed / in-progress for members, created for leads)
    - today's tracked hours + active %
    - last-seen timestamp
    """
    permission_classes = [IsSuperAdmin]

    def get(self, request, company_id):
        company = get_object_or_404(Company, id=company_id)
        users = CustomUser.objects.filter(company=company).order_by('-date_joined')

        today = timezone.localdate()
        recent_cutoff = timezone.now() - timedelta(minutes=2)

        users_data = []
        for u in users:
            last = (
                EmployeeActivity.objects
                .filter(user=u, timestamp__gte=recent_cutoff)
                .order_by('-timestamp')
                .first()
            )
            is_online = last is not None
            is_idle = (last.event_type == 'idle') if last else False

            active_s = idle_s = 0
            if u.role == 'team_member':
                active_s, idle_s, _logs = _compute_daily_totals(u, today)
            total_s = active_s + idle_s

            assigned_qs = u.assigned_tasks.all()
            assigned_count = assigned_qs.count()
            completed_count = assigned_qs.filter(status='complete').count()
            in_progress_count = assigned_qs.filter(status='in_progress').count()
            created_count = u.created_tasks.count()

            users_data.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': u.role,
                'is_online': is_online,
                'is_idle': is_idle,
                'last_seen': timezone.localtime(last.timestamp).strftime('%Y-%m-%d %H:%M:%S') if last else None,
                'today_active_seconds': active_s,
                'today_idle_seconds': idle_s,
                'today_active_formatted': _fmt(active_s),
                'today_active_pct': round((active_s / total_s) * 100, 1) if total_s else 0,
                'assigned_tasks_count': assigned_count,
                'completed_tasks_count': completed_count,
                'in_progress_tasks_count': in_progress_count,
                'created_tasks_count': created_count,
            })

        return Response({
            'company': CompanySerializer(company).data,
            'users': users_data,
        })


class SuperAdminToggleCompanyView(APIView):
    """Suspend / reactivate a company."""
    permission_classes = [IsSuperAdmin]

    def post(self, request, company_id):
        company = get_object_or_404(Company, id=company_id)
        company.is_active = not company.is_active
        company.save(update_fields=['is_active'])
        return Response(CompanySerializer(company).data)


class SuperAdminUpdatePlanView(APIView):
    """Change a company's plan / max_users."""
    permission_classes = [IsSuperAdmin]

    def patch(self, request, company_id):
        company = get_object_or_404(Company, id=company_id)
        plan = request.data.get('plan')
        max_users = request.data.get('max_users')
        if plan:
            company.plan = plan
        if max_users:
            company.max_users = int(max_users)
        company.save()
        return Response(CompanySerializer(company).data)


class SuperAdminStatsView(APIView):
    """Platform-wide totals for the SaaS admin dashboard header."""
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        total_companies  = Company.objects.count()
        active_companies = Company.objects.filter(is_active=True).count()
        total_users      = CustomUser.objects.exclude(role='super_admin').count()
        total_leads       = CustomUser.objects.filter(role='team_lead').count()
        total_members     = CustomUser.objects.filter(role='team_member').count()
        plan_breakdown = list(
            Company.objects.values('plan').annotate(count=Count('id')).order_by('plan')
        )
        return Response({
            'total_companies':  total_companies,
            'active_companies': active_companies,
            'suspended_companies': total_companies - active_companies,
            'total_users':      total_users,
            'total_leads':      total_leads,
            'total_members':    total_members,
            'plan_breakdown':   plan_breakdown,
        })
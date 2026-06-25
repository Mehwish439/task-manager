from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, date, timedelta
from django.db.models import Sum
from django.db import IntegrityError
import csv, os
from calendar import monthrange
from django.http import HttpResponse, FileResponse
from io import BytesIO

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
    CustomUser, Task, Comment, TaskStatus,
    Attendance, ChatMessage, Break,
    EmployeeActivity, AppTimeSession, DailyActivitySummary,
    BrowserActivity,
)
from .serializers import (
    RegisterSerializer, TaskSerializer, UserSerializer,
    MyTokenObtainPairSerializer, CommentSerializer,
    AttendanceSerializer, GroupChatSerializer, TaskCalendarSerializer,
    EmployeeActivitySerializer, AppTimeSessionSerializer,
    DailyActivitySummarySerializer,
    BrowserActivitySerializer,
)


# =============================================================
# AUTH
# =============================================================
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class CustomTokenRefreshView(APIView):
    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            return Response({'access': str(token.access_token)})
        except TokenError:
            return Response({'error': 'Invalid refresh token'}, status=401)

class RegisterView(generics.CreateAPIView):
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)

class TeamMemberListView(generics.ListAPIView):
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return CustomUser.objects.filter(role='team_member')

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
            users = CustomUser.objects.filter(id__in=assigned_to_ids)
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
        task  = get_object_or_404(Task, id=task_id)
        users = CustomUser.objects.filter(id__in=request.data.get('assigned_to', []))
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
        att = Attendance.objects.create(user=request.user, manual_check_in=request.data.get('manual_check_in'))
        return Response({'message': 'Checked in', 'attendance': AttendanceSerializer(att, context={'request': request}).data})

class CheckOutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        today = timezone.localdate()
        att   = Attendance.objects.filter(user=request.user, system_check_in__date=today, system_check_out__isnull=True).last()
        if not att:
            return Response({'error': 'No active check-in.'}, status=400)
        att.system_check_out = timezone.now()
        if request.data.get('manual_check_out'):
            att.manual_check_out = request.data['manual_check_out']
        att.save()
        return Response({'message': 'Checked out', 'attendance': AttendanceSerializer(att, context={'request': request}).data})

class AttendanceListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.role != 'team_lead':
            raise PermissionDenied('Only team leads.')
        records = Attendance.objects.select_related('user').order_by('-date')
        return Response(AttendanceSerializer(records, many=True).data)

class AttendanceCSVExportView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="attendance.csv"'
        writer = csv.writer(resp)
        writer.writerow(['User','Date','Clock In','Clock Out','Worked Hours'])
        for att in Attendance.objects.select_related('user').all():
            writer.writerow([att.user.username, att.date, att.system_check_in, att.system_check_out, att.worked_hours or 0])
        return resp

class PauseWorkView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        today = timezone.localdate()
        att   = Attendance.objects.filter(user=request.user, system_check_in__date=today, system_check_out__isnull=True).last()
        if not att: return Response({'error': 'No active session'}, status=400)
        Break.objects.create(attendance=att, break_start=timezone.now())
        return Response({'message': 'Break started'})

class ResumeWorkView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        today      = timezone.localdate()
        att        = Attendance.objects.filter(user=request.user, system_check_in__date=today, system_check_out__isnull=True).last()
        if not att: return Response({'error': 'No active session'}, status=400)
        last_break = Break.objects.filter(attendance=att, break_end__isnull=True).last()
        if not last_break: return Response({'error': 'No active break'}, status=400)
        last_break.break_end = timezone.now()
        last_break.save()
        return Response({'message': 'Work resumed'})


# =============================================================
# CHAT
# =============================================================
class GroupChatListCreateView(generics.ListCreateAPIView):
    serializer_class   = GroupChatSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return ChatMessage.objects.all().order_by('created_at')
    def perform_create(self, serializer):
        msg = self.request.data.get('message', '').strip()
        if msg:
            serializer.save(sender=self.request.user, message=msg)

class GroupChatClearView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if request.user.role != 'team_lead':
            return Response({'error': 'Only team leads can clear chat.'}, status=403)
        ChatMessage.objects.all().delete()
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
            tasks = Task.objects.filter(start_date__lte=last, end_date__gte=first)
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

def _update_daily_summary(user, target_date, active_s, idle_s, app_name=None, seconds=0):
    summary, _ = DailyActivitySummary.objects.get_or_create(user=user, date=target_date)
    summary.total_active_seconds += active_s
    summary.total_idle_seconds   += idle_s
    summary.total_pings          += 1
    if app_name and seconds > 0:
        sess, _ = AppTimeSession.objects.get_or_create(user=user, date=target_date, app_name=app_name)
        sess.seconds_spent += seconds
        sess.save(update_fields=['seconds_spent', 'last_seen'])
    top = (
        AppTimeSession.objects
        .filter(user=user, date=target_date)
        .order_by('-seconds_spent')
        .values_list('app_name', flat=True)
        .first()
    )
    summary.top_app = top
    summary.save(update_fields=['total_active_seconds', 'total_idle_seconds', 'total_pings', 'top_app'])


# =============================================================
# TRACK ACTIVITY  (desktop — unchanged)
# =============================================================
class TrackActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logs = request.data.get('logs', [])
        if not logs or not isinstance(logs, list):
            return Response({'error': 'logs array required'}, status=400)

        created = 0
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

            target_date = timezone.localtime(from_dt).date()

            EmployeeActivity.objects.create(
                user          = request.user,
                event_type    = ev_type,
                active_window = app_name,
                window_title  = win_title,
                seconds       = seconds,
                timestamp     = from_dt,
                ended_at      = to_dt,
            )

            active_s = seconds if ev_type == 'active' else 0
            idle_s   = seconds if ev_type == 'idle'   else 0
            _update_daily_summary(
                request.user, target_date,
                active_s, idle_s,
                app_name if ev_type == 'active' else None, seconds
            )
            created += 1

        return Response({'status': 'ok', 'saved': created}, status=201)


# =============================================================
# ACTIVITY LOGS
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

        logs = (
            EmployeeActivity.objects
            .filter(user_id=uid, timestamp__date=target_date)
            .order_by('timestamp')
        )

        rows = []
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

        total_active = sum(r['seconds'] for r in rows if r['type'] == 'active')
        total_idle   = sum(r['seconds'] for r in rows if r['type'] == 'idle')
        total_all    = total_active + total_idle

        app_totals = {}
        for r in rows:
            if r['type'] == 'active':
                app_totals[r['app']] = app_totals.get(r['app'], 0) + r['seconds']
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
            user = get_object_or_404(CustomUser, id=uid)

        try:
            summary      = DailyActivitySummary.objects.get(user=user, date=target_date)
            summary_data = DailyActivitySummarySerializer(summary).data
        except DailyActivitySummary.DoesNotExist:
            summary_data = None

        apps = AppTimeSession.objects.filter(user=user, date=target_date).order_by('-seconds_spent')

        return Response({
            'user':          user.username,
            'date':          target_date,
            'summary':       summary_data,
            'app_breakdown': AppTimeSessionSerializer(apps, many=True).data,
        })


# =============================================================
# TEAM ACTIVITY SUMMARY
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
        members       = CustomUser.objects.filter(role='team_member')
        result        = []

        for member in members:
            try:
                s        = DailyActivitySummary.objects.get(user=member, date=target_date)
                active_s = s.total_active_seconds
                idle_s   = s.total_idle_seconds
                top_app  = s.top_app
            except DailyActivitySummary.DoesNotExist:
                active_s = idle_s = 0
                top_app  = None

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
# MEMBER ACTIVITY DETAIL
# =============================================================
class MemberActivityDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.role != 'team_lead':
            raise PermissionDenied('Only team leads.')

        member      = get_object_or_404(CustomUser, id=user_id, role='team_member')
        target_date = timezone.localdate()
        if dp := request.query_params.get('date'):
            try:
                target_date = datetime.strptime(dp, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date'}, status=400)

        try:
            s            = DailyActivitySummary.objects.get(user=member, date=target_date)
            summary_data = DailyActivitySummarySerializer(s).data
        except DailyActivitySummary.DoesNotExist:
            summary_data = None

        logs = (
            EmployeeActivity.objects
            .filter(user=member, timestamp__date=target_date)
            .order_by('timestamp')
        )
        timeline = []
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

        total_active = sum(r['seconds'] for r in timeline if r['type'] == 'active')
        total_idle   = sum(r['seconds'] for r in timeline if r['type'] == 'idle')
        total_all    = total_active + total_idle

        app_totals = {}
        for r in timeline:
            if r['type'] == 'active':
                app_totals[r['app']] = app_totals.get(r['app'], 0) + r['seconds']
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
            user = get_object_or_404(CustomUser, id=uid)
        summaries = DailyActivitySummary.objects.filter(user=user).order_by('-date')[:days]
        return Response({
            'user':           user.username,
            'days_requested': days,
            'history':        DailyActivitySummarySerializer(summaries, many=True).data,
        })


# =============================================================
# APP TIME LEADERBOARD
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
            .filter(date=target_date)
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
# WEEKLY PDF REPORT
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
            members = [get_object_or_404(CustomUser, id=uid)]
        elif request.user.role == 'team_lead':
            members = list(CustomUser.objects.filter(role='team_member'))
        else:
            members = [request.user]

        buffer = BytesIO()
        doc    = SimpleDocTemplate(buffer, pagesize=A4,
                                   rightMargin=2*cm, leftMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story  = []
        date_range = [start_date + timedelta(days=i) for i in range(7)]

        story.append(Paragraph('QRM Weekly Activity Report',
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
            sums = {s.date: s for s in DailyActivitySummary.objects.filter(
                user=member, date__gte=start_date, date__lte=end_date)}

            rows = [['Date', 'Active', 'Idle', 'Active %', 'Top App']]
            wa = wi = 0
            for d in date_range:
                s = sums.get(d)
                if s:
                    tot = s.total_active_seconds + s.total_idle_seconds
                    pct = round(s.total_active_seconds / tot * 100, 1) if tot else 0
                    rows.append([d.strftime('%a %d %b'), _fmt(s.total_active_seconds),
                                  _fmt(s.total_idle_seconds), f'{pct}%', s.top_app or '—'])
                    wa += s.total_active_seconds
                    wi += s.total_idle_seconds
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
# MY LOGS
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

        logs = (
            EmployeeActivity.objects
            .filter(user=request.user, timestamp__date=target_date)
            .order_by('timestamp')
        )

        timeline = []
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

        total_active = sum(r['seconds'] for r in timeline if r['type'] == 'active')
        total_idle   = sum(r['seconds'] for r in timeline if r['type'] == 'idle')
        total_all    = total_active + total_idle

        app_totals = {}
        for r in timeline:
            if r['type'] == 'active':
                app_totals[r['app']] = app_totals.get(r['app'], 0) + r['seconds']
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
            'timeline':      timeline,
        })


# =============================================================
# BROWSER ACTIVITY  (FIXED)
# =============================================================
class BrowserActivityView(APIView):
    """
    POST /api/browser-activity/

    FIX 1: This is now the CORRECT target endpoint in browser-server.js.
           Previously browser-server.js was sending to /api/track-activity/
           which never wrote to BrowserActivity table, so the browser tab
           on the dashboard always showed empty.

    FIX 2: Full sub-URL is now stored. Previously only the domain was
           saved; now entry.get('url') contains the full URL like
           youtube.com/watch?v=abc123 sent from browser-server.js.

    Writes to TWO tables:
      1. EmployeeActivity  — existing desktop timeline still works
      2. BrowserActivity   — new browser tab reads from this
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logs = request.data.get('logs', [])
        if not logs or not isinstance(logs, list):
            return Response({'error': 'logs array required'}, status=400)

        created = 0
        for entry in logs:
            raw_title = (entry.get('title') or '').strip()
            app_name  = (entry.get('app')   or '').strip() or 'Browser'
            full_url  = (entry.get('url')   or '').strip()   # FIX 2: full sub-URL
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

            target_date = timezone.localtime(from_dt).date()

            # Strip the [Browser] prefix for clean storage in BrowserActivity
            clean_title = raw_title.replace('[Browser] ', '', 1) if raw_title.startswith('[Browser] ') else raw_title

            # Extract path+query from URL for display  (FIX 2)
            # e.g. "https://youtube.com/watch?v=abc" → "/watch?v=abc"
            try:
                from urllib.parse import urlparse
                parsed   = urlparse(full_url)
                sub_path = parsed.path
                if parsed.query:
                    sub_path += '?' + parsed.query
            except Exception:
                sub_path = full_url

            # 1. EmployeeActivity — existing dashboard reads this unchanged
            EmployeeActivity.objects.create(
                user          = request.user,
                event_type    = 'active',
                active_window = app_name,
                window_title  = raw_title,      # keeps [Browser] prefix for is_browser flag
                seconds       = seconds,
                timestamp     = from_dt,
                ended_at      = to_dt,
            )

            # 2. BrowserActivity — browser tab on dashboard reads this  (FIX 1 + FIX 2)
            BrowserActivity.objects.create(
                user          = request.user,
                url           = full_url or app_name,   # FIX 2: real URL stored
                domain        = app_name,
                title         = clean_title,
                timestamp     = from_dt,
                ended_at      = to_dt,
                seconds       = seconds,
                activity_type = 'browser',
            )

            _update_daily_summary(
                request.user, target_date,
                seconds, 0,
                app_name, seconds
            )
            created += 1

        return Response({'status': 'ok', 'saved': created}, status=201)


class BrowserActivityListView(APIView):
    """
    GET /api/browser-activity/list/?user_id=X&date=YYYY-MM-DD

    FIX: Now returns full sub-URL in each visit row so the dashboard
    shows "youtube.com/watch?v=abc123" not just "youtube.com".
    Visits are ordered by timestamp (chronological) not by seconds,
    so the lead sees them in the order they were visited.
    """
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

        # Order by timestamp so visits appear chronologically
        logs = (
            BrowserActivity.objects
            .filter(user_id=uid, timestamp__date=target_date)
            .order_by('timestamp')             # FIX: was order_by('-seconds')
        )

        # Domain breakdown for bar chart
        domain_totals = {}
        for l in logs:
            domain_totals[l.domain] = domain_totals.get(l.domain, 0) + l.seconds

        domain_breakdown = sorted(
            [{'domain': k, 'seconds': v, 'duration': _fmt(v)} for k, v in domain_totals.items()],
            key=lambda x: -x['seconds']
        )

        total_s = sum(domain_totals.values())

        # Build visits list with full sub-URL  (FIX 2)
        visits = []
        for l in logs:
            local_time = timezone.localtime(l.timestamp)

            # Extract readable path from stored URL
            try:
                from urllib.parse import urlparse
                parsed   = urlparse(l.url)
                sub_path = parsed.path
                if parsed.query:
                    sub_path += '?' + parsed.query
                if not sub_path or sub_path == '/':
                    sub_path = ''
            except Exception:
                sub_path = ''

            visits.append({
                'id':           l.id,
                'domain':       l.domain,
                'url':          l.url,          # full URL
                'sub_path':     sub_path,        # just the path part e.g. /watch?v=abc
                'title':        l.title,
                'timestamp':    l.timestamp.isoformat(),
                'time':         local_time.strftime('%H:%M:%S'),
                'seconds':      l.seconds,
                'time_formatted': _fmt(l.seconds),
            })

        return Response({
            'date':             str(target_date),
            'total_browser_s':  total_s,
            'total_browser':    _fmt(total_s),
            'domain_breakdown': domain_breakdown,
            'visits':           visits,
        })
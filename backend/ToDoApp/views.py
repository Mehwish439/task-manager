from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import CustomUser, Task, Comment, TaskStatus
from .serializers import (
    RegisterSerializer,
    TaskSerializer,
    UserSerializer,
    MyTokenObtainPairSerializer,
    CommentSerializer
)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class CustomTokenRefreshView(APIView):
    def post(self, request):
        refresh = request.data.get('refresh')
        try:
            token = RefreshToken(refresh)
            return Response({'access': str(token.access_token)})
        except TokenError:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class TeamMemberListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(role='team_member')

class CreateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        assigned_to_ids = request.data.get('assigned_to', [])

        if not all([title, description, start_date, end_date]):
            return Response({'error': 'All fields except assignment are required.'}, status=status.HTTP_400_BAD_REQUEST)

        task = Task.objects.create(
            title=title,
            description=description,
            created_by=request.user,
            start_date=start_date,
            end_date=end_date
        )

        if assigned_to_ids:
            users = CustomUser.objects.filter(id__in=assigned_to_ids)
            task.assigned_to.set(users)
            for user in users:
                TaskStatus.objects.create(task=task, user=user)

        return Response({'message': 'Task created successfully', 'task_id': task.id}, status=status.HTTP_201_CREATED)

class TaskDeleteView(generics.DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if instance.created_by != self.request.user:
            raise PermissionDenied("Only the creator can delete this task.")
        instance.delete()

class AssignTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        assigned_to_ids = request.data.get('assigned_to', [])
        task = get_object_or_404(Task, id=task_id)

        users = CustomUser.objects.filter(id__in=assigned_to_ids)
        task.assigned_to.add(*users)
        for user in users:
            TaskStatus.objects.get_or_create(task=task, user=user)

        return Response({'message': 'Users assigned successfully.'})

class AssignedTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)

class CreatedTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user).order_by('-start_date')

class TaskUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id, parent__isnull=True).order_by('created_at')

    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        user = self.request.user

        if user != task.created_by and user not in task.assigned_to.all():
            raise PermissionDenied("You are not allowed to comment on this task.")

        serializer.save(author=user, task=task)

class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("You can only delete your own comments.")
        instance.delete()

class TaskStatusBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        statuses = TaskStatus.objects.filter(task=task)

        breakdown = [
            {
                'user': status.user.username,
                'email': status.user.email,
                'status': status.status
            }
            for status in statuses
        ]
        return Response({'status_breakdown': breakdown})

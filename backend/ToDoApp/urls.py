from django.urls import path
from .views import (
    RegisterView,
    CreateTaskView,
    AssignedTaskListView,
    TaskUpdateView,
    TaskDeleteView,
    TeamMemberListView,
    MyTokenObtainPairView,
    MeView,
    CustomTokenRefreshView,
    CommentListCreateAPIView,
    CommentDetailAPIView,
    AssignTaskView,
    CreatedTaskListView,  # ✅ New import
    TaskStatusBreakdownView
)

urlpatterns = [
    # 🔐 Auth
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/me/', MeView.as_view(), name='me'),
    path('api/refresh-token/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    # 📋 Tasks
    path('api/create-task/', CreateTaskView.as_view(), name='create_task'),
    path('api/assigned-tasks/', AssignedTaskListView.as_view(), name='assigned_tasks'),
    path('api/created-tasks/', CreatedTaskListView.as_view(), name='created_tasks'),  # ✅ New endpoint
    path('api/update-task/<int:id>/', TaskUpdateView.as_view(), name='update_task'),
    path('api/delete-task/<int:id>/', TaskDeleteView.as_view(), name='delete_task'),
    path('api/assign-task/<int:task_id>/', AssignTaskView.as_view(), name='assign_task'),

    # 👥 Team Members
    path('api/team-members/', TeamMemberListView.as_view(), name='team_members'),

    # 💬 Comments
    path('api/tasks/<int:task_id>/comments/', CommentListCreateAPIView.as_view(), name='task_comments'),
    path('api/comments/<int:pk>/', CommentDetailAPIView.as_view(), name='comment_detail'),
    path('api/task-status/<int:task_id>/breakdown/', TaskStatusBreakdownView.as_view(), name='task_status_breakdown'),
]

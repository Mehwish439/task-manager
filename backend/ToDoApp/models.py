from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('team_lead', 'Team Lead'),
        ('team_member', 'Team Member'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username


class Task(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('testing', 'Testing'),
        ('complete', 'Complete'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    assigned_to = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='assigned_tasks'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TaskStatus(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_task_statuses')
    status = models.CharField(max_length=20, choices=Task.STATUS_CHOICES, default='in_progress')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('task', 'user')

    def __str__(self):
        return f"{self.task.title} - {self.user.username} ({self.status})"


class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on "{self.task.title}"'

    def is_reply(self):
        return self.parent is not None

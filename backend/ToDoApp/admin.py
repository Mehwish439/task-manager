from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Task, TaskStatus, Comment, Attendance, ChatMessage


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Task)
admin.site.register(TaskStatus)
admin.site.register(Comment)
admin.site.register(Attendance)
admin.site.register(ChatMessage)
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, Task, Comment


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token


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

# 🔁 Recursive Comment Replies
class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

# 💬 Comment Serializer with Nested Replies
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

# 📋 Task Serializer with Assigned Users and Comments
class TaskSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    assigned_to = UserBasicSerializer(many=True, read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'created_by',
            'assigned_to', 'start_date', 'end_date', 'created_at',
            'updated_at', 'comments'
        ]

    def get_comments(self, obj):
        top_level_comments = obj.comments.filter(parent__isnull=True)
        return CommentSerializer(top_level_comments, many=True, context=self.context).data

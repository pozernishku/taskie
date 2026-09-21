"""Serializers for tasks application."""

from typing import ClassVar

from django.contrib.auth import get_user_model
from rest_framework import serializers

from taskie.apps.accounts.serializers import UserSerializer
from taskie.apps.tasks.models import Comment, Task, TaskPriority, TaskStatus

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Task Comments."""

    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "task", "author", "content", "created_at", "updated_at")
        read_only_fields = ("id", "task", "author", "created_at", "updated_at")
        extra_kwargs: ClassVar[dict] = {
            "content": {"required": True},
        }

    def validate_content(self, value: str) -> str:
        """Validate comment content is not empty or whitespace."""
        trimmed = value.strip()
        if not trimmed:
            msg = "Comment content cannot be empty or only whitespace."
            raise serializers.ValidationError(msg)
        return trimmed


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task creation, detail, and updates."""

    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assigned_to",
        write_only=True,
        required=False,
        allow_null=True,
    )
    status = serializers.ChoiceField(choices=TaskStatus.choices, default=TaskStatus.TODO)
    priority = serializers.ChoiceField(choices=TaskPriority.choices, default=TaskPriority.MEDIUM)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "created_by",
            "assigned_to",
            "assigned_to_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")
        extra_kwargs: ClassVar[dict] = {
            "title": {"required": True},
            "description": {"required": False, "allow_blank": True},
        }

    def validate_title(self, value: str) -> str:
        """Validate title is not empty or whitespace only."""
        trimmed = value.strip()
        if not trimmed:
            msg = "Task title cannot be blank or only whitespace."
            raise serializers.ValidationError(msg)
        return trimmed


class TaskAssignSerializer(serializers.Serializer):
    """Serializer for assigning/reassigning a task to a user."""

    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True,
        required=True,
        help_text="User ID to assign the task to, or null to unassign.",
    )

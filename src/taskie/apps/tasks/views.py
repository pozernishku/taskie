"""Views for tasks application."""

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from taskie.apps.tasks.filters import TaskFilter
from taskie.apps.tasks.models import Comment, Task, TaskStatus
from taskie.apps.tasks.permissions import IsAuthorOrReadOnly
from taskie.apps.tasks.serializers import (
    CommentSerializer,
    TaskAssignSerializer,
    TaskSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["Tasks"], summary="List tasks with filtering, search, and ordering"),
    create=extend_schema(tags=["Tasks"], summary="Create a new task"),
    retrieve=extend_schema(tags=["Tasks"], summary="Retrieve task details"),
    update=extend_schema(tags=["Tasks"], summary="Update task"),
    partial_update=extend_schema(tags=["Tasks"], summary="Partially update task"),
    destroy=extend_schema(tags=["Tasks"], summary="Delete task"),
)
class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tasks."""

    queryset = Task.objects.select_related("created_by", "assigned_to").all()
    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = TaskFilter
    search_fields = ("title", "description")
    ordering_fields = ("created_at", "due_date", "priority", "status", "title")
    ordering = ("-created_at",)

    def perform_create(self, serializer: serializers.BaseSerializer) -> None:
        """Set task creator automatically from request user."""
        serializer.save(created_by=self.request.user)

    @extend_schema(
        tags=["Tasks"],
        summary="Mark task as completed (DONE)",
        request=None,
        responses={200: TaskSerializer},
    )
    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None) -> Response:
        """Custom action to mark task as completed."""
        task = self.get_object()
        task.status = TaskStatus.DONE
        task.save(update_fields=["status", "updated_at"])
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Tasks"],
        summary="Assign or reassign task to a user",
        request=TaskAssignSerializer,
        responses={200: TaskSerializer},
    )
    @action(detail=True, methods=["post"], url_path="assign", serializer_class=TaskAssignSerializer)
    def assign(self, request, pk=None) -> Response:
        """Custom action to assign or reassign task."""
        task = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task.assigned_to = serializer.validated_data["assigned_to"]
        task.save(update_fields=["assigned_to", "updated_at"])
        output_serializer = TaskSerializer(task, context=self.get_serializer_context())
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Comments"],
        summary="List all comments for a task",
        methods=["GET"],
        responses={200: CommentSerializer(many=True)},
    )
    @extend_schema(
        tags=["Comments"],
        summary="Add a comment to a task",
        methods=["POST"],
        request=CommentSerializer,
        responses={201: CommentSerializer},
    )
    @action(detail=True, methods=["get", "post"], url_path="comments", serializer_class=CommentSerializer)
    def comments(self, request, pk=None) -> Response:
        """Action to list and create comments on a specific task."""
        task = self.get_object()
        if request.method == "GET":
            task_comments = task.comments.select_related("author").all()
            serializer = CommentSerializer(task_comments, many=True, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(task=task, author=request.user)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    retrieve=extend_schema(tags=["Comments"], summary="Retrieve a single comment"),
    update=extend_schema(tags=["Comments"], summary="Update comment content"),
    partial_update=extend_schema(tags=["Comments"], summary="Partially update comment"),
    destroy=extend_schema(tags=["Comments"], summary="Delete comment"),
)
class CommentViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet for updating and deleting individual comments."""

    queryset = Comment.objects.select_related("author", "task").all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated, IsAuthorOrReadOnly)

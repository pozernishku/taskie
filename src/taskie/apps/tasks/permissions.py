"""Custom permissions for tasks application."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Allow read access to all authenticated users, write access to author or task creator."""

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check comment author
        if hasattr(obj, "author") and obj.author == request.user:
            return True

        # Check task creator when deleting a comment
        if hasattr(obj, "task") and obj.task.created_by == request.user and request.method == "DELETE":
            return True

        # Check task created_by
        if hasattr(obj, "created_by"):
            return obj.created_by == request.user

        return False

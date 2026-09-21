"""URL patterns for tasks app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from taskie.apps.tasks.views import CommentViewSet, TaskViewSet

app_name = "tasks"

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
]

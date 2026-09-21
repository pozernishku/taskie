"""Pytest fixtures and configuration."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Return an unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Factory fixture to create users."""

    def _create_user(
        username: str = "testuser",
        email: str = "testuser@example.com",
        password: str = "P@ssw0rd123!",
        **kwargs,
    ) -> User:
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **kwargs,
        )

    return _create_user


@pytest.fixture
def user(create_user) -> User:
    """Create and return a standard user."""
    return create_user()


@pytest.fixture
def other_user(create_user) -> User:
    """Create and return another user."""
    return create_user(
        username="otheruser",
        email="otheruser@example.com",
        password="OtherP@ssw0rd123!",
    )


@pytest.fixture
def auth_client(api_client, user) -> APIClient:
    """Return an API client authenticated with standard user via JWT."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def auth_client_for():
    """Return a function that generates an API client authenticated for any given user."""

    def _auth_client(u: User) -> APIClient:
        client = APIClient()
        refresh = RefreshToken.for_user(u)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return client

    return _auth_client


@pytest.fixture
def create_task(db):
    """Factory fixture to create tasks."""
    from taskie.apps.tasks.models import Task, TaskPriority, TaskStatus

    def _create_task(
        created_by: User,
        title: str = "Test Task",
        description: str = "Test Description",
        status: str = TaskStatus.TODO,
        priority: str = TaskPriority.MEDIUM,
        assigned_to: User | None = None,
        **kwargs,
    ) -> Task:
        return Task.objects.create(
            created_by=created_by,
            title=title,
            description=description,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            **kwargs,
        )

    return _create_task


@pytest.fixture
def task(user, create_task):
    """Create and return a sample task."""
    return create_task(created_by=user)


@pytest.fixture
def create_comment(db):
    """Factory fixture to create comments."""
    from taskie.apps.tasks.models import Comment, Task

    def _create_comment(
        task: Task,
        author: User,
        content: str = "This is a test comment.",
        **kwargs,
    ) -> Comment:
        return Comment.objects.create(
            task=task,
            author=author,
            content=content,
            **kwargs,
        )

    return _create_comment


@pytest.fixture
def comment(task, user, create_comment):
    """Create and return a sample comment."""
    return create_comment(task=task, author=user)

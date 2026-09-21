"""Tests for task management and lifecycle endpoints."""

import pytest
from rest_framework import status

from taskie.apps.tasks.models import Task, TaskPriority, TaskStatus


@pytest.mark.django_db
class TestTaskCRUD:
    """Test standard CRUD endpoints for tasks."""

    tasks_url = "/api/v1/tasks/"

    def test_create_task_unauthenticated(self, api_client):
        payload = {"title": "New Task"}
        response = api_client.post(self.tasks_url, payload, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_task_success(self, auth_client, user, other_user):
        payload = {
            "title": "Build API",
            "description": "Implement all endpoints",
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.TODO,
            "assigned_to_id": other_user.id,
        }
        response = auth_client.post(self.tasks_url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Build API"
        assert data["description"] == "Implement all endpoints"
        assert data["priority"] == TaskPriority.HIGH
        assert data["created_by"]["id"] == user.id
        assert data["assigned_to"]["id"] == other_user.id

    def test_create_task_invalid_title(self, auth_client):
        payload = {"title": "   ", "description": "Empty title"}
        response = auth_client.post(self.tasks_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title" in response.json()

    def test_list_tasks(self, auth_client, create_task, user, other_user):
        create_task(created_by=user, title="Task 1")
        create_task(created_by=other_user, title="Task 2")

        response = auth_client.get(self.tasks_url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        results = data.get("results", data)
        assert len(results) >= 2

    def test_retrieve_task(self, auth_client, task):
        response = auth_client.get(f"{self.tasks_url}{task.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == task.id
        assert response.json()["title"] == task.title

    def test_update_task(self, auth_client, task):
        payload = {
            "title": "Updated Task Title",
            "priority": TaskPriority.LOW,
        }
        response = auth_client.patch(f"{self.tasks_url}{task.id}/", payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == "Updated Task Title"
        assert task.priority == TaskPriority.LOW

    def test_delete_task(self, auth_client, task):
        response = auth_client.delete(f"{self.tasks_url}{task.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task.id).exists()


@pytest.mark.django_db
class TestTaskActions:
    """Test custom task actions (complete, assign)."""

    tasks_url = "/api/v1/tasks/"

    def test_complete_task(self, auth_client, task):
        assert task.status == TaskStatus.TODO
        response = auth_client.post(f"{self.tasks_url}{task.id}/complete/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == TaskStatus.DONE
        task.refresh_from_db()
        assert task.status == TaskStatus.DONE

    def test_assign_task_to_user(self, auth_client, task, other_user):
        payload = {"assigned_to": other_user.id}
        response = auth_client.post(f"{self.tasks_url}{task.id}/assign/", payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.assigned_to == other_user

    def test_unassign_task(self, auth_client, create_task, user, other_user):
        task_with_assignee = create_task(created_by=user, assigned_to=other_user)
        payload = {"assigned_to": None}
        response = auth_client.post(f"{self.tasks_url}{task_with_assignee.id}/assign/", payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        task_with_assignee.refresh_from_db()
        assert task_with_assignee.assigned_to is None

    def test_assign_task_invalid_user(self, auth_client, task):
        payload = {"assigned_to": 999999}
        response = auth_client.post(f"{self.tasks_url}{task.id}/assign/", payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTaskFilterAndSearch:
    """Test filtering, searching, and ordering of tasks."""

    tasks_url = "/api/v1/tasks/"

    def test_filter_by_status(self, auth_client, create_task, user):
        t1 = create_task(created_by=user, title="Todo Task", status=TaskStatus.TODO)
        _t2 = create_task(created_by=user, title="Done Task", status=TaskStatus.DONE)

        response = auth_client.get(f"{self.tasks_url}?status={TaskStatus.TODO}")
        assert response.status_code == status.HTTP_200_OK
        results = response.json().get("results", response.json())
        ids = [t["id"] for t in results]
        assert t1.id in ids
        assert _t2.id not in ids

    def test_filter_by_priority(self, auth_client, create_task, user):
        t1 = create_task(created_by=user, title="High Priority", priority=TaskPriority.HIGH)
        _t2 = create_task(created_by=user, title="Low Priority", priority=TaskPriority.LOW)

        response = auth_client.get(f"{self.tasks_url}?priority={TaskPriority.HIGH}")
        assert response.status_code == status.HTTP_200_OK
        results = response.json().get("results", response.json())
        ids = [t["id"] for t in results]
        assert t1.id in ids
        assert _t2.id not in ids

    def test_filter_by_assignee(self, auth_client, create_task, user, other_user):
        t1 = create_task(created_by=user, title="Assigned", assigned_to=other_user)
        _t2 = create_task(created_by=user, title="Unassigned", assigned_to=None)

        response = auth_client.get(f"{self.tasks_url}?assigned_to={other_user.id}")
        assert response.status_code == status.HTTP_200_OK
        results = response.json().get("results", response.json())
        ids = [t["id"] for t in results]
        assert t1.id in ids
        assert _t2.id not in ids

    def test_search_tasks(self, auth_client, create_task, user):
        t1 = create_task(created_by=user, title="Unique Keyword Title", description="Generic")
        t2 = create_task(created_by=user, title="Generic Title", description="Contains Unique Keyword Here")
        _t3 = create_task(created_by=user, title="Other", description="Nothing here")

        response = auth_client.get(f"{self.tasks_url}?search=Unique Keyword")
        assert response.status_code == status.HTTP_200_OK
        results = response.json().get("results", response.json())
        ids = [t["id"] for t in results]
        assert t1.id in ids
        assert t2.id in ids
        assert _t3.id not in ids

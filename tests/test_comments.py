"""Tests for comments subsystem and permissions."""

import pytest
from rest_framework import status

from taskie.apps.tasks.models import Comment


@pytest.mark.django_db
class TestTaskComments:
    """Test task comment creation and listing endpoints."""

    def test_list_comments_for_task(self, auth_client, task, user, other_user, create_comment):
        c1 = create_comment(task=task, author=user, content="First comment")
        c2 = create_comment(task=task, author=other_user, content="Second comment")

        url = f"/api/v1/tasks/{task.id}/comments/"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == c1.id
        assert data[0]["content"] == "First comment"
        assert data[0]["author"]["id"] == user.id
        assert data[1]["id"] == c2.id
        assert data[1]["author"]["id"] == other_user.id

    def test_create_comment_success(self, auth_client, task, user):
        url = f"/api/v1/tasks/{task.id}/comments/"
        payload = {"content": "Great progress so far!"}
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "Great progress so far!"
        assert data["author"]["id"] == user.id
        assert data["task"] == task.id
        assert Comment.objects.filter(id=data["id"]).exists()

    def test_create_comment_empty_content(self, auth_client, task):
        url = f"/api/v1/tasks/{task.id}/comments/"
        payload = {"content": "   "}
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "content" in response.json()

    def test_create_comment_nonexistent_task(self, auth_client):
        url = "/api/v1/tasks/999999/comments/"
        payload = {"content": "Comment on nothing"}
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_comment_unauthenticated(self, api_client, task):
        url = f"/api/v1/tasks/{task.id}/comments/"
        payload = {"content": "Unauth comment"}
        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCommentDetailAndPermissions:
    """Test updating, retrieving, and deleting individual comments."""

    def test_retrieve_comment(self, auth_client, comment):
        url = f"/api/v1/comments/{comment.id}/"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == comment.id
        assert response.json()["content"] == comment.content

    def test_update_own_comment(self, auth_client, comment):
        url = f"/api/v1/comments/{comment.id}/"
        payload = {"content": "Updated comment content"}
        response = auth_client.patch(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert comment.content == "Updated comment content"

    def test_update_other_user_comment_forbidden(self, auth_client_for, comment, other_user):
        other_client = auth_client_for(other_user)
        url = f"/api/v1/comments/{comment.id}/"
        payload = {"content": "Unauthorized edit attempt"}
        response = other_client.patch(url, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_own_comment(self, auth_client, comment):
        url = f"/api/v1/comments/{comment.id}/"
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(id=comment.id).exists()

    def test_delete_comment_by_task_creator(self, auth_client_for, user, other_user, create_task, create_comment):
        # Task created by `user`, comment authored by `other_user`
        task = create_task(created_by=user)
        comment = create_comment(task=task, author=other_user, content="Comment by other")

        # Creator of the task (`user`) can delete comments on their task
        creator_client = auth_client_for(user)
        url = f"/api/v1/comments/{comment.id}/"
        response = creator_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(id=comment.id).exists()

    def test_delete_comment_by_third_party_forbidden(
        self, auth_client_for, create_user, user, other_user, create_task, create_comment
    ):
        third_user = create_user(username="thirduser", email="third@example.com")
        task = create_task(created_by=user)
        comment = create_comment(task=task, author=other_user)

        third_client = auth_client_for(third_user)
        url = f"/api/v1/comments/{comment.id}/"
        response = third_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

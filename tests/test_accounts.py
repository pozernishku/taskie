"""Tests for user accounts, registration, and JWT authentication."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestRegistration:
    """Test user registration endpoint."""

    register_url = "/api/v1/auth/register/"

    def test_register_success(self, api_client):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post(self.register_url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data
        assert User.objects.filter(username="newuser").exists()
        user = User.objects.get(username="newuser")
        assert user.check_password("SecurePassword123!")

    def test_register_duplicate_username(self, api_client, user):
        payload = {
            "username": user.username,
            "email": "unique@example.com",
            "password": "SecurePassword123!",
        }
        response = api_client.post(self.register_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.json()

    def test_register_duplicate_email(self, api_client, user):
        payload = {
            "username": "differentusername",
            "email": user.email,
            "password": "SecurePassword123!",
        }
        response = api_client.post(self.register_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()

    def test_register_missing_fields(self, api_client):
        payload = {"username": "onlyuser"}
        response = api_client.post(self.register_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestJWTAuthentication:
    """Test JWT token obtain and refresh endpoints."""

    token_url = "/api/v1/auth/token/"
    refresh_url = "/api/v1/auth/token/refresh/"

    def test_token_obtain_success(self, api_client, user):
        payload = {
            "username": "testuser",
            "password": "P@ssw0rd123!",
        }
        response = api_client.post(self.token_url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access" in data
        assert "refresh" in data

    def test_token_obtain_invalid_credentials(self, api_client, user):
        payload = {
            "username": "testuser",
            "password": "WrongPassword!",
        }
        response = api_client.post(self.token_url, payload, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh_success(self, api_client, user):
        obtain_res = api_client.post(
            self.token_url,
            {"username": "testuser", "password": "P@ssw0rd123!"},
            format="json",
        )
        refresh_token = obtain_res.json()["refresh"]

        refresh_res = api_client.post(self.refresh_url, {"refresh": refresh_token}, format="json")
        assert refresh_res.status_code == status.HTTP_200_OK
        data = refresh_res.json()
        assert "access" in data

    def test_token_refresh_invalid(self, api_client):
        response = api_client.post(self.refresh_url, {"refresh": "invalid-token"}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserEndpoints:
    """Test user list and detail endpoints."""

    users_url = "/api/v1/auth/users/"

    def test_list_users_unauthenticated(self, api_client):
        response = api_client.get(self.users_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_users_authenticated(self, auth_client, user, other_user):
        response = auth_client.get(self.users_url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        results = data.get("results", data)
        usernames = [u["username"] for u in results]
        assert user.username in usernames
        assert other_user.username in usernames

    def test_retrieve_user(self, auth_client, user):
        response = auth_client.get(f"{self.users_url}{user.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == user.username

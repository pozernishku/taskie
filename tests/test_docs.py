"""Tests for OpenAPI documentation endpoints."""

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestAPIDocumentation:
    """Test schema and interactive documentation endpoints."""

    def test_schema_endpoint(self, api_client):
        response = api_client.get("/api/schema/")
        assert response.status_code == status.HTTP_200_OK

    def test_swagger_ui_endpoint(self, api_client):
        response = api_client.get("/api/docs/swagger/")
        assert response.status_code == status.HTTP_200_OK
        assert b"swagger-ui" in response.content.lower()

    def test_redoc_endpoint(self, api_client):
        response = api_client.get("/api/docs/redoc/")
        assert response.status_code == status.HTTP_200_OK
        assert b"redoc" in response.content.lower()

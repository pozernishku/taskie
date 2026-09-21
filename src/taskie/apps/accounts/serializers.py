"""Serializers for accounts application."""

from typing import ClassVar

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User details and list."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")
        read_only_fields = ("id",)


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name")
        read_only_fields = ("id",)
        extra_kwargs: ClassVar[dict] = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate_email(self, value: str) -> str:
        """Ensure email is unique."""
        if User.objects.filter(email__iexact=value).exists():
            msg = "A user with this email already exists."
            raise serializers.ValidationError(msg)
        return value.lower()

    def validate_password(self, value: str) -> str:
        """Validate password strength using Django validators."""
        validate_password(value)
        return value

    def create(self, validated_data: dict) -> User:
        """Create and return a new User instance with encrypted password."""
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

"""Views for accounts application."""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from taskie.apps.accounts.serializers import RegisterSerializer, UserSerializer

User = get_user_model()


@extend_schema(tags=["Authentication"], summary="Register a new user account")
class RegisterView(generics.CreateAPIView):
    """View to register a new user."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


@extend_schema_view(
    list=extend_schema(tags=["Users"], summary="List registered users for assignment"),
    retrieve=extend_schema(tags=["Users"], summary="Retrieve user profile"),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for reading user profiles."""

    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("username", "email", "first_name", "last_name")
    ordering_fields = ("id", "username", "date_joined")

"""Filters for tasks application."""

import django_filters
from django.contrib.auth import get_user_model

from taskie.apps.tasks.models import Task, TaskPriority, TaskStatus

User = get_user_model()


class TaskFilter(django_filters.FilterSet):
    """FilterSet for Task querying."""

    status = django_filters.ChoiceFilter(choices=TaskStatus.choices)
    priority = django_filters.ChoiceFilter(choices=TaskPriority.choices)
    assigned_to = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    created_by = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    due_date_after = django_filters.DateTimeFilter(field_name="due_date", lookup_expr="gte")
    due_date_before = django_filters.DateTimeFilter(field_name="due_date", lookup_expr="lte")

    class Meta:
        model = Task
        fields = ("status", "priority", "assigned_to", "created_by", "due_date")

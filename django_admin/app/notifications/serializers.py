# django_admin/app/notifications/serializers.py
from rest_framework import serializers

from .notification import Template


class TemplateSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Template."""

    class Meta:
        model = Template
        fields = ["slug", "title", "description", "content"]
        read_only_fields = ["slug"]  # slug нельзя изменять через API

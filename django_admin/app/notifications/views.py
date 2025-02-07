# django_admin/app/notifications/views.py
import logging

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .notification import Template
from .serializers import TemplateSerializer

logger = logging.getLogger(__name__)


@api_view(["GET"])
def get_template(request, template_id):
    """API endpoint для получения шаблона по ID."""
    try:
        if not template_id:
            return Response(
                {"error": "Template ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        template = Template.objects.get(slug=template_id)
        serializer = TemplateSerializer(template)
        return Response(serializer.data)

    except Template.DoesNotExist:
        logger.warning(f"Template not found: {template_id}")
        return Response(
            {"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND
        )

    except ValidationError as e:
        logger.error(f"Validation error for template {template_id}: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error fetching template {template_id}: {e}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

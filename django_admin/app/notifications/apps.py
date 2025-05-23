import os

from config.components import base as settings
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
    verbose_name = _("notifications")
    path = os.path.join(settings.BASE_DIR, "notifications")

import os

from config.components import base as settings
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "custom_auth"
    verbose_name = _("custom_auth")
    path = os.path.join(settings.BASE_DIR, "custom_auth")

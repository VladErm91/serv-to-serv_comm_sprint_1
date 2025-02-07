import os

from config.components import base as settings
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MoviesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movies"
    verbose_name = _("movies")
    path = os.path.join(settings.BASE_DIR, "custom_auth")

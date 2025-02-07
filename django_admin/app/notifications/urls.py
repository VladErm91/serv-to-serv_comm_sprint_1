# django_admin/app/notifications/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("templates/<str:template_id>/", views.get_template, name="get_template"),
]

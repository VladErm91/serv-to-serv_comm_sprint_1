# django_admin/app/notifications/admin.py
import logging

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from .notification import Notification, NotificationUser, Template, send_notifications

logger = logging.getLogger(__name__)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    """Админка шаблонов уведомлений."""

    list_display = ("slug", "title", "description")
    search_fields = ("slug", "title", "description", "content")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = ((None, {"fields": ("slug", "title", "description", "content")}),)


class NotificationUserInline(admin.TabularInline):
    """Инлайн для получателей уведомления."""

    model = NotificationUser
    extra = 1
    raw_id_fields = ("user",)
    readonly_fields = ("send_attempts", "status", "last_update")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Админка уведомлений."""

    list_display = (
        "title",
        "template",
        "delivery_type",
        "scheduled_time",
        "repeat_type",
    )
    list_filter = ("delivery_type", "scheduled_time")
    search_fields = ("title", "template__title")
    raw_id_fields = ("template",)
    inlines = [NotificationUserInline]

    fieldsets = (
        (None, {"fields": ("template", "title", "delivery_type")}),
        (
            _("Schedule"),
            {
                "fields": ("scheduled_time", "repeat_type"),
                "classes": ("collapse",),
                "description": _(
                    "Specify schedule for delayed or recurring notifications. "
                    "For recurring notifications, use cron format: * * * * * "
                    "(minute, hour, day of month, month, day of week)"
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """Отправляем уведомление в очередь при сохранении."""
        super().save_model(request, obj, form, change)
        try:
            obj.schedule()
            if obj.scheduled_time:
                if obj.repeat_type != "* * * * *":
                    messages.success(
                        request,
                        _(f'Notification "{obj}" scheduled for recurring delivery'),
                    )
                else:
                    messages.success(
                        request,
                        _(f'Notification "{obj}" scheduled for {obj.scheduled_time}'),
                    )
            else:
                messages.success(request, _(f'Notification "{obj}" sent to queue'))
        except Exception as e:
            logger.error(f"Failed to schedule notification: {e}")
            messages.error(request, _("Failed to schedule notification"))

    actions = ["send_notification"]

    @admin.action(description=_("Send selected notifications"))
    def send_notification(self, request, queryset):
        """Действие для отправки выбранных уведомлений."""
        for notification in queryset:
            try:
                send_notifications.delay(notification.id)
                messages.success(
                    request, _(f'Notification "{notification}" sent to queue')
                )
            except Exception as e:
                logger.error(f"Failed to send notification {notification}: {e}")
                messages.error(
                    request, _(f'Failed to send notification "{notification}"')
                )

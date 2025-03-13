# django_admin/app/notifications/notification.py

import json
import logging
from typing import Annotated

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from .enums import DeliveryType, Status

User = get_user_model()
logger = logging.getLogger(__name__)


class Template(models.Model):
    """
    Шаблон уведомления
    """

    slug = models.SlugField(_("slug"), max_length=50, primary_key=True)
    title = models.CharField(_("title"), max_length=100)
    description = models.CharField(_("description"), max_length=250)
    content = models.TextField(
        _("content"),
        help_text="Содержимое уведомления",
    )

    class Meta:
        verbose_name = _("template")
        verbose_name_plural = _("templates")

    def __str__(self):
        return f"Шаблон: {self.title}"


class Notification(models.Model):
    """
    Уведомление
    """

    template = models.ForeignKey("Template", on_delete=models.CASCADE)
    title = models.CharField(_("title"), max_length=50)
    delivery_type = models.CharField(
        _("delivery_type"),
        choices=DeliveryType.choice(),
        default=DeliveryType.EMAIL.value,
    )
    users = models.ManyToManyField(
        User, related_name=_("notifications"), through="NotificationUser"
    )

    scheduled_time = models.DateTimeField(_("scheduled_time"), null=True, blank=True)
    repeat_type = models.CharField(
        _("repeat_type"),
        max_length=50,
        null=True,
        blank=True,
        help_text="Введите интервал повторения в формате: '* * * * *' * - 1 * минута 2 * час 3 * день месяца 4 * месяц 5 * день недели",
        default="* * * * *",
    )

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")

    def __str__(self):
        return f"Notification: {self.title}"

    @property
    def recipients(self) -> User | list[User]:
        """
        Возвращает список адрессатов уведомления
        """
        return list(self.users.all())

    @property
    def recipients_ids(self) -> list[Annotated[str, "Id Группы пользователей"]]:
        """
        Возвращает список идентификаторов для адрессатов уведомления
        """
        return [str(user.id) for user in self.recipients]

    def schedule(self):
        """
        Формирование расписания отправки уведомлений
        """

        if self.scheduled_time:
            if self.repeat_type != "* * * * *":
                crontab = self.repeat_type.split(" ")
                crontab.extend(["*"] * (5 - len(crontab)))
                schedule, _ = CrontabSchedule.objects.get_or_create(
                    minute=crontab[0],
                    hour=crontab[1],
                    day_of_week=crontab[2],
                    day_of_month=crontab[3],
                    month_of_year=crontab[4],
                )
                PeriodicTask.objects.update_or_create(
                    name=f"notification_{self.id}",
                    defaults={
                        "crontab": schedule,
                        "task": "notifications.tasks.send_notification",
                        "args": json.dumps([self.id]),
                    },
                )
                logger.info(
                    f"Celery task created for notification {self.id} with repeat_type: {self.repeat_type}"
                )
            else:
                # Отложенная оправка
                send_notifications.apply_async(args=[self.id], eta=self.scheduled_time)
                logger.info(
                    f"Scheduled one-time notification {self.id} for {self.scheduled_time}"
                )
        else:
            # Мгновенная отправка
            send_notifications.delay(self.id)
            logger.info(f"Instant notification {self.id} sent to queue")


class NotificationUser(models.Model):
    """
    Уведомление пользователю
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    send_attempts = models.IntegerField(verbose_name="Query retries count", default=0)
    status = models.CharField(
        verbose_name=_("status"),
        max_length=10,
        choices=Status.choice(),
        default=Status.PENDING.value,
    )
    last_update = models.DateTimeField(verbose_name="Last update", auto_now=True)


@shared_task
def send_notifications(notification_id):
    """
    Задача Celery для отправки уведомления в сервис API.
    """
    try:
        from .services import send_notification_to_api

        send_notification_to_api(notification_id)
        logger.info(f"Notification {notification_id} sent to API")
    except Exception as e:
        logger.error(f"Failed to send notification {notification_id}: {e}")


@shared_task
def test_task():
    logger.info("Test task executed successfully")

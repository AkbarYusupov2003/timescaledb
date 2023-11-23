from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class TimescaleModel(models.Model):
    time = TimescaleDateTimeField(interval="1 day")
    objects = TimescaleManager()

    class Meta:
        abstract = True


# Content Statistic
class ContentHour(TimescaleModel):
    content_id = models.IntegerField()
    episode_id = models.IntegerField(blank=True, null=True)
    watched_users_count = models.PositiveIntegerField(default=0)
    watched_duration = models.PositiveIntegerField(default=0)
    age_group = models.JSONField(default=dict, blank=True, null=True)
    gender = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = "Контент за час"
        verbose_name_plural = "Контенты за час"
        db_table = "statistic_content_hour"


class ContentDay(TimescaleModel):
    content_id = models.IntegerField()
    episode_id = models.IntegerField(blank=True, null=True)
    watched_users_count = models.PositiveIntegerField(default=0)
    watched_duration = models.PositiveIntegerField(default=0)
    age_group = models.JSONField(default=dict, blank=True, null=True)
    gender = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = "Контент за день"
        verbose_name_plural = "Контенты за день"
        db_table = "statistic_content_day"


class ContentMonth(TimescaleModel):
    content_id = models.IntegerField()
    episode_id = models.IntegerField(blank=True, null=True)
    watched_users_count = models.PositiveIntegerField(default=0)
    watched_duration = models.PositiveIntegerField(default=0)
    age_group = models.JSONField(default=dict, blank=True, null=True)
    gender = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = "Контент за месяц"
        verbose_name_plural = "Контенты за месяц"
        db_table = "statistic_content_month"


# Broadcast Statistic
class BroadcastHour(TimescaleModel):
    broadcast_id = models.PositiveIntegerField()
    watched_users_count = models.PositiveIntegerField(default=0)
    watched_duration = models.PositiveIntegerField(default=0)
    age_group = models.JSONField(default=dict, blank=True, null=True)
    gender = models.JSONField(default=dict, blank=True, null=True)
    
    class Meta:
        verbose_name = "Телеканал за час"
        verbose_name_plural = "Телеканалы за час"
        db_table = "statistic_broadcast_hour"


class BroadcastDay(TimescaleModel):
    broadcast_id = models.PositiveIntegerField()
    watched_users_count = models.PositiveIntegerField(default=0)
    watched_duration = models.PositiveIntegerField(default=0)
    age_group = models.JSONField(default=dict, blank=True, null=True)
    gender = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = "Телеканал за день"
        verbose_name_plural = "Телеканалы за день"
        db_table = "statistic_broadcast_day"


class BroadcastMonth(TimescaleModel):
    broadcast_id = models.PositiveIntegerField()
    watched_users_count = models.PositiveIntegerField(default=0)
    watched_duration = models.PositiveIntegerField(default=0)
    age_group = models.JSONField(default=dict, blank=True, null=True)
    gender = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = "Телеканал за месяц"
        verbose_name_plural = "Телеканалы за месяц"
        db_table = "statistic_broadcast_month"


# --------------------------------------------------------------------
class History(TimescaleModel):
    
    AGE_GROUPS = (
        (0, ("0-6")),
        (1, ("7-12")),
        (2, ("13-16")),
        (3, ("17-18")),
        (4, ("19-21")),
        (5, ("22-28")),
        (6, ("29-36")),
        (7, ("37-46")),
        (8, ("47-54")),
        (9, ("55+")),
    )
    
    GENDERS = (
        ("M", "Мужчина"),
        ("W", "Женщина"),
    )
    
    slug = models.SlugField()
    content_id = models.PositiveIntegerField(blank=True, null=True)
    broadcast_id = models.PositiveIntegerField(blank=True, null=True)
    episode_id = models.PositiveIntegerField(blank=True, null=True)
    
    user_agent = models.CharField(max_length=128)
    ip_address = models.CharField(max_length=16)
    device = models.CharField(max_length=64)
    age_group = models.PositiveIntegerField(choices=AGE_GROUPS, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDERS, blank=True, null=True)
    duration = models.PositiveIntegerField(default=10)

    class Meta:
        verbose_name = "История просмотра"
        verbose_name_plural = "Истории просмотров"
        db_table = "statistic_history"


class Register(TimescaleModel):    
    count = models.IntegerField()

    class Meta:
        verbose_name = "Регистрация"
        verbose_name_plural = "Регистрации"
        db_table = "statistic_register"


class Subscription(TimescaleModel):
    sub_id = models.CharField(max_length=8)
    count = models.IntegerField()
    
    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        db_table = "statistic_subscription"


class Report(models.Model):
    STATUSES = (
        ("PENDING", "В ожидании"),
        ("STARTED", "В исполнении"),
        ("FAILURE", "Ошибка"),
        ("FINISHED", "Завершен")
    )

    status = models.CharField(choices=STATUSES, default="PENDING")
    section = models.CharField(max_length=128)
    lines_count = models.PositiveIntegerField(null=True, blank=True)
    data = models.JSONField(default=dict, blank=True, null=True)
    file = models.FileField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"

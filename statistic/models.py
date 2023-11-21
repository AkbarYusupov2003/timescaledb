from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class TimescaleModel(models.Model):
    time = TimescaleDateTimeField(interval="1 day")
    objects = TimescaleManager()

    class Meta:
        abstract = True


class ContentHour(TimescaleModel):
    # TODO age_group gender
    content_id = models.IntegerField()
    episode_id = models.IntegerField(blank=True, null=True)
    watched_users_count = models.PositiveIntegerField()
    watched_duration = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Контента за час"
        verbose_name_plural = "Контенты за час"

class BroadcastHour(TimescaleModel):
    # TODO age_group gender
    watched_users_count = models.PositiveIntegerField()
    watched_duration = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = "Прямой эфир за час"
        verbose_name_plural = "Прямые эфиры за час"


class Subscription(TimescaleModel):
    sub_id = models.CharField(max_length=8)
    count = models.IntegerField()
    
    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class Register(TimescaleModel):    
    count = models.IntegerField()

    class Meta:
        verbose_name = "Регистрация"
        verbose_name_plural = "Регистрации"


class History(TimescaleModel):
    slug = models.SlugField()
    content_id = models.IntegerField(blank=True, null=True)
    broadcast_id = models.IntegerField(blank=True, null=True)
    episode_id = models.IntegerField(blank=True, null=True)
    
    user_agent = models.CharField(max_length=128)
    ip_address = models.CharField(max_length=16)
    device = models.CharField(max_length=64)
    # age_group
    # gender
    duration = models.PositiveIntegerField(default=10)

    class Meta:
        verbose_name = "История просмотра"
        verbose_name_plural = "Истории просмотров"

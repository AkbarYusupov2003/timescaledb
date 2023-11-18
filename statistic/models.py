from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class TimescaleModel(models.Model):
    time = TimescaleDateTimeField(interval="1 day")
    objects = TimescaleManager()

    class Meta:
        abstract = True


# class ContentStat(TimescaleModel):
#     # owner = models.ForeignKey("Content")
#     age_group = 1
#     sex = 1
#     views = 1
#     duration = 1


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
    content_id = models.IntegerField(blank=True)
    broadcast_id = models.IntegerField(blank=True)
    episode_id = models.IntegerField(blank=True)
    
    user_agent = models.CharField(max_length=128)
    ip_address = models.CharField(max_length=16)
    device = models.CharField(max_length=64)

    duration = models.PositiveIntegerField()

    class Meta:
        verbose_name = "История просмотра"
        verbose_name_plural = "Истории просмотров"

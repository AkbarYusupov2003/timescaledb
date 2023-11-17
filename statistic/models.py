from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class TimescaleModel(models.Model):
    time = TimescaleDateTimeField(interval="1 day")
    objects = TimescaleManager()

    class Meta:
        abstract = True

# content_id int,episode_id int,watched_users_count int,watched_duration int, ts timestamp
class ContentStat(TimescaleModel):
    # owner = models.ForeignKey() #Content

    age_group = 1
    sex = 1
    
    watched_users_count = 1
    watched_duration = 1
    timestamp = 1
    # content
    

class Subscription(TimescaleModel):
    subscription_id = models.IntegerField()
    count = models.IntegerField()
    
    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class Register(TimescaleModel):    
    count = models.IntegerField()

    class Meta:
        verbose_name = "Регистрация"
        verbose_name_plural = "Регистрации"

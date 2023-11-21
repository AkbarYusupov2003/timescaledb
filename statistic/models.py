from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class TimescaleModel(models.Model):
    time = TimescaleDateTimeField(interval="1 day")
    objects = TimescaleManager()

    class Meta:
        abstract = True


class ContentHour(TimescaleModel):
    age_group_default = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
    gender_group_default = {"M": 0, "W": 0}
    #
    content_id = models.IntegerField()
    episode_id = models.IntegerField(blank=True, null=True)
    watched_users_count = models.PositiveIntegerField(default=0)
    watched_duration = models.PositiveIntegerField(default=0)
    age_group = models.JSONField(default=age_group_default, blank=True, null=True) # {"4": "25"}, 25 просмотров от возрастной группы 19-21
    gender = models.JSONField(default=gender_group_default, blank=True, null=True)
    
    class Meta:
        verbose_name = "Контент за час"
        verbose_name_plural = "Контенты за час"


class BroadcastHour(TimescaleModel):
    # TODO age_group gender
    broadcast_id = models.PositiveIntegerField()
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

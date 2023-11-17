from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class TimescaleModel(models.Model):
    time = TimescaleDateTimeField(interval="1 day")
    objects = TimescaleManager()

    class Meta:
        abstract = True


class Subscription(TimescaleModel):
    subscription_id = models.IntegerField()
    count = models.IntegerField()


class Register(TimescaleModel):    
    count = models.IntegerField()

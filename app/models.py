from django.db import models
from django.utils.timezone import now
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class TimescaleModel(models.Model):
    """
    A helper class for using Timescale within Django, has the TimescaleManager and
    TimescaleDateTimeField already present. This is an abstract class it should
    be inheritted by another class for use.
    """

    time = TimescaleDateTimeField(interval="1 day") #, default=now)
    objects = TimescaleManager()

    class Meta:
        abstract = True

# Subscriptions model: type, time
class Subscription(TimescaleModel):
    subscription_id = models.IntegerField()
    
    count = models.IntegerField()
    # time = TimescaleDateTimeField(interval="1 day") # interval????
    # objects = TimescaleManager()


class Transaction(TimescaleModel):
    transaction_id = models.IntegerField()
    
    count = models.IntegerField()
    # time = TimescaleDateTimeField(interval="1 day") # interval????
    # objects = TimescaleManager()
import datetime
from django.db import connection
from django.db.models import F
from celery import shared_task
from celery.schedules import crontab

from config.celery import app
from internal.models import Content, Broadcast
from statistic.utils import data_extractor, etc
from statistic import models


@shared_task(name='hourly-register-task')
def hourly_register_task():
    period = "hours"
    data = data_extractor.get_data(data_extractor.SIGNUP_URL, params={'period': period})
    time = datetime.datetime.now() - datetime.timedelta(hours=1)
    if type(data) == dict:
        models.Register.objects.create(count=data.get("count", 0), time=time)


@shared_task(name='hourly-subscription-task')
def hourly_subscription_task():
    period = "hours"
    data = data_extractor.get_data(data_extractor.TRANSACTION_URL, params={'period': period})
    time = datetime.datetime.now() - datetime.timedelta(hours=1)
    if type(data) == dict:
        for key, value in data.items():
            models.Subscription.objects.create(sub_id=key, count=value, time=time)


def hourly_history_task():
    to_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    from_time = to_time - datetime.timedelta(hours=1)
    histories = models.History.objects.filter(
        time__range=(from_time, to_time),
    )
    print("TIME: ", from_time, to_time)
    print("histories", histories)
    for history in histories:
        try:
            if history.content_id:
                print("content", history.content_id, history.episode_id)
                if etc.exists_or_create(
                    {"content_id": history.content_id, "episode_id": history.episode_id},
                    history.slug
                ):
                    content, _ = models.ContentHour.objects.get_or_create(
                        time=from_time, content_id=history.content_id, episode_id=history.episode_id
                    )
                    content.age_group[str(history.age_group)] += 1
                    content.gender[history.gender] += 1
                    content.watched_users_count = F("watched_users_count") + 1
                    content.watched_duration = F("watched_duration") + history.duration
                    content.save()
            elif history.broadcast_id:
                if Broadcast.objects.get(
                    broadcast_id=history.broadcast_id
                ):
                    broadcast, _ = models.BroadcastHour.objects.get_or_create(
                        time=from_time, broadcast_id=history.broadcast_id,
                    )
                    broadcast.age_group[str(history.age_group)] += 1
                    broadcast.gender[history.gender] += 1
                    broadcast.watched_users_count = F("watched_users_count") + 1
                    broadcast.watched_duration = F("watched_duration") + history.duration
                    broadcast.save()
        except Exception as e:
            print("Exception", e)


def synchronize_content_task():
    data = data_extractor.get_data(data_extractor.CONTENT_DATA_URL, params={"id_slugs": ""}) 
    print("DATA: ", data)


app.conf.beat_schedule = {
    'hourly-register-task': {
        'task': 'hourly-register-task',
        'schedule': crontab(minute='1', hour='*'),
    },
    'hourly-subscription-task': {
        'task': 'hourly-subscription-task',
        'schedule': crontab(minute='2', hour='*'),
    },
}

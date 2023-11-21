import datetime
from django.db import connection
from django.db.models import F
from celery import shared_task
from celery.schedules import crontab

from config.celery import app
from internal.models import Content
from statistic.utils import data_extractor
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
    ) #.annotate(a=Sum("duration"))
    print("TIME: ", from_time, to_time)
    print("histories", histories)
    for history in histories:
        print("history gender", history.gender)
        try:
            if history.content_id:
                if Content.objects.get(
                    content_id=history.content_id, episode_id=history.episode_id
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
                print("history broadcast", history.broadcast_id)
                # if Broadcast
        except Exception as e:
            print("Exception", e)

    # cursor = connection.cursor()
    # cursor.execute(
    #     f"""
    #         SELECT *
    #         FROM statistic_history
    #         WHERE (time BETWEEN '{from_time}' AND '{to_time}')
    #         ORDER BY time DESC;
    #     """
    # )
    # print("cursor.fetchall()", cursor.fetchall())


def synchronize_content_task():
    # params={"id_slugs": [123_null,456_654, contentid_episodeid]}
    #data = data_extractor.get_data(data_extractor.CONTENT_DATA_URL, params={"id_slugs": ["4632_12697"]}) 
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

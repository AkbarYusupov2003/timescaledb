import datetime
from collections import Counter
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


@shared_task(name='hourly-history-task')
def hourly_history_task():
    to_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    from_time = to_time - datetime.timedelta(hours=1)
    histories = models.History.objects.filter(
        time__range=(from_time, to_time),
    )
    print("Histories", histories, from_time, to_time)
    for history in histories:
        try:
            if history.content_id:
                if etc.exists_or_create(
                    {"content_id": history.content_id, "episode_id": history.episode_id},
                    history.slug
                ):
                    content, _ = models.ContentHour.objects.get_or_create(
                        time=to_time, content_id=history.content_id, episode_id=history.episode_id
                    )
                    content.age_group[str(history.age_group)] = content.age_group.get(str(history.age_group), 0) + 1
                    content.gender[str(history.gender)] = content.gender.get(str(history.gender), 0) + 1
                    content.watched_users_count += 1
                    content.watched_duration += history.duration
                    content.save()
            elif history.broadcast_id:
                if Broadcast.objects.get(
                    broadcast_id=history.broadcast_id
                ):
                    broadcast, _ = models.BroadcastHour.objects.get_or_create(
                        time=to_time, broadcast_id=history.broadcast_id,
                    )
                    broadcast.age_group[str(history.age_group)] = broadcast.age_group.get(str(history.age_group), 0) + 1
                    broadcast.gender[str(history.gender)] = broadcast.gender.get(str(history.gender), 0) + 1
                    broadcast.watched_users_count+= 1
                    broadcast.watched_duration += history.duration
                    broadcast.save()
        except Exception as e:
            print("Exception", e)


@shared_task(name='daily-history-task')
def daily_history_task():
    # to_time = datetime.date.today()
    # from_time = to_time - datetime.timedelta(days=1)
    from_time = datetime.date.today()
    to_time = from_time + datetime.timedelta(days=1)

    contents = Content.objects.all()
    for content in contents:
        histories = models.History.objects.filter(
            time__range=(from_time, to_time), content_id=content.content_id, episode_id=content.episode_id
        )
        daily = models.ContentDay.objects.create(
            time=from_time, content_id=content.content_id, episode_id=content.episode_id
        )
        for history in histories:
            daily.age_group[str(history.age_group)] = daily.age_group.get(str(history.age_group), 0) + 1
            daily.gender[str(history.gender)] = daily.gender.get(str(history.gender), 0) + 1
            daily.watched_users_count += 1
            daily.watched_duration += history.duration
            daily.save()

    dailies = models.ContentDay.objects.filter(
        time=from_time
    )
    for daily in dailies:
        monthly, _ = models.ContentMonth.objects.get_or_create(
            time=from_time, content_id=daily.content_id, episode_id=daily.episode_id
        )
        monthly.age_group = dict(Counter(monthly.age_group) + Counter(daily.age_group))
        monthly.gender = dict(Counter(monthly.gender) + Counter(daily.gender))
        monthly.watched_users_count += daily.watched_users_count
        monthly.watched_duration += daily.watched_duration
        monthly.save()

    # Broadcast
    broadcasts = Broadcast.objects.all()
    for broadcast in broadcasts:
        histories = models.History.objects.filter(
            time__range=(from_time, to_time), broadcast_id=broadcast.broadcast_id
        )
        daily = models.BroadcastDay.objects.create(
            time=from_time, broadcast_id=broadcast.broadcast_id
        )
        for history in histories:
            daily.age_group[str(history.age_group)] = daily.age_group.get(str(history.age_group), 0) + 1
            daily.gender[str(history.gender)] = daily.gender.get(str(history.gender), 0) + 1
            daily.watched_users_count += 1
            daily.watched_duration += history.duration
            daily.save()

# TODO
def synchronize_content_task():
    data = data_extractor.get_data(data_extractor.CONTENT_DATA_URL, params={"id_slugs": ""}) 
    print("DATA: ", data)


app.conf.beat_schedule = {
    'daily-history-task': {
        'task': 'hourly-register-task',
        'schedule': crontab(minute='5', hour='0'),
    },
    'hourly-history-task': {
        'task': 'hourly-history-task',
        'schedule': crontab(minute='0', hour='*'),
    },
    #
    'hourly-register-task': {
        'task': 'hourly-register-task',
        'schedule': crontab(minute='1', hour='*'),
    },
    'hourly-subscription-task': {
        'task': 'hourly-subscription-task',
        'schedule': crontab(minute='2', hour='*'),
    },
}

import datetime
from collections import Counter
from django.db import connection
from django.db.models import F
from celery import shared_task
from celery.schedules import crontab

from config.celery import app
from statistic import models
from internal import models as internal_models
from statistic.utils import data_extractor, etc


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
    # Hourly
    for history in histories:
        try:
            if history.content_id:
                if etc.exists_or_create(
                    {"content_id": history.content_id, "episode_id": history.episode_id},
                    history.slug
                ):
                    content, created = models.ContentHour.objects.get_or_create(
                        time=from_time, content_id=history.content_id, episode_id=history.episode_id,
                        sid=history.sid, age_group=history.age_group, gender=history.gender, country=history.country, device=history.device
                    )
                    
                    if created:
                        content.watched_users_count = 1

                    content.age_group_count += 1
                    content.gender_count += 1
                    content.watched_duration += history.duration
                    content.save()
            elif history.broadcast_id:
                if internal_models.Broadcast.objects.get(
                    broadcast_id=history.broadcast_id
                ):
                    broadcast, created = models.BroadcastHour.objects.get_or_create(
                        time=to_time, broadcast_id=history.broadcast_id,
                        sid=history.sid, age_group=history.age_group, gender=history.gender, country=history.country, device=history.device
                    )
                    
                    if created:
                        broadcast.watched_users_count = 1
                    
                    broadcast.age_group_count += 1
                    broadcast.gender_count += 1
                    broadcast.watched_duration += history.duration
                    broadcast.save()
        except Exception as e:
            print("Exception", e)
    # Hourly ended


@shared_task(name="daily-history-task")
def daily_history_task():
    # to_time = datetime.date.today()
    # from_time = to_time - datetime.timedelta(days=1) # Yesterday
    from_time = datetime.date.today() # Yesterday
    to_time = from_time + datetime.timedelta(days=1)
    
    # DAILY
    # Content
    contents = internal_models.Content.objects.all()
    for content in contents:
        histories = models.History.objects.filter(
            time__range=(from_time, to_time), content_id=content.content_id, episode_id=content.episode_id,
        )
        for history in histories:
            daily_c, created = models.ContentDay.objects.get_or_create(
                time=from_time, content_id=content.content_id, episode_id=content.episode_id,
                sid=history.sid, age_group=history.age_group, gender=history.gender, country=history.country, device=history.device
            )

            if created:
                daily_c.watched_users_count = 1

            daily_c.age_group_count += 1
            daily_c.gender_count += 1
            daily_c.watched_duration += history.duration
            daily_c.save()
    
    # Broadcast
    broadcasts = internal_models.Broadcast.objects.all()
    for broadcast in broadcasts:
        histories = models.History.objects.filter(
            time__range=(from_time, to_time), broadcast_id=broadcast.broadcast_id
        )
        for history in histories:
            daily_b, created = models.BroadcastDay.objects.get_or_create(
                time=from_time, broadcast_id=broadcast.broadcast_id,
                sid=history.sid, age_group=history.age_group, gender=history.gender, country=history.country, device=history.device
            )
            if created:
                daily_b.watched_users_count = 1

            daily_c.age_group_count += 1
            daily_c.gender_count += 1
            daily_b.watched_duration += history.duration
            daily_b.save()
    # Daily ended

    # MONTHLY
    # Content
    daily_contents = models.ContentDay.objects.filter(time=from_time)
    for content in daily_contents:
        monthly_c = models.ContentMonth.objects.create(
            time=from_time, content_id=content.content_id, episode_id=content.episode_id,
            sid=content.sid, age_group=content.age_group, gender=content.gender, country=content.country, device=content.device
        )

        monthly_c.age_group_count += content.age_group_count
        monthly_c.gender_count += content.gender_count
        monthly_c.watched_users_count += content.watched_users_count
        monthly_c.watched_duration += content.watched_duration
        monthly_c.save()

    # Broadcast
    daily_broadcasts = models.BroadcastDay.objects.filter(time=from_time)
    for broadcast in daily_broadcasts:
        monthly_b = models.BroadcastMonth.objects.create(
            time=from_time, broadcast_id=broadcast.broadcast_id,
            sid=broadcast.sid, age_group=broadcast.age_group, gender=broadcast.gender,  country=broadcast.country, device=broadcast.device
        )

        monthly_b.age_group_count += broadcast.age_group_count
        monthly_b.gender_count += broadcast.gender_count
        monthly_b.watched_users_count += broadcast.watched_users_count
        monthly_b.watched_duration += broadcast.watched_duration
        monthly_b.save()
    # Monthly ended


@shared_task(name="daily-data-update-task")
def daily_data_update_task():
    # update contents
    contents = internal_models.Content.objects.all().select_related(
        "category"
    ).prefetch_related("sponsors", "allowed_subscriptions")
    slugs = [{"slug": "7635_14946"}]
    for content in contents:
        # content
        slug = slugs[0]["slug"]
        data = data_extractor.get_data(data_extractor.CONTENT_DATA_URL, params={"id_slugs": slug}).get("results").get(slug)
        if data:
            content_dict = content.__dict__
            print("data", data)
            print("\n\n")
            print("content_dict", content_dict)
            print("\n\n")
            updated = False
            for key, value in data.items():
                if content_dict.get(key) != value:
                    updated = True
                    setattr(content, key, value)
            if updated:
                content.save()
        else:
            print("no result")
            continue
    
    # update broadcasts
    pass


# # TODO
# def synchronize_content_task():
#     data = data_extractor.get_data(data_extractor.CONTENT_DATA_URL, params={"id_slugs": ""}) 
#     print("DATA: ", data)


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
    'hourly-register-task ': {
        'task': 'hourly-register-task',
        'schedule': crontab(minute='1', hour='*'),
    },
    'hourly-subscription-task': {
        'task': 'hourly-subscription-task',
        'schedule': crontab(minute='2', hour='*'),
    },
    
}

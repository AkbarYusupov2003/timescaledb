import datetime
from collections import Counter
from django.db import connection
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from celery import shared_task
from celery.schedules import crontab

from config.celery import app
from statistic import models
from internal import models as internal_models
from statistic.utils import data_extractor, etc


# Register
@shared_task(name='hourly-register-task')
def hourly_register_task():
    period = "hours"
    data = data_extractor.get_data(data_extractor.SIGNUP_URL, params={'period': period})
    time = datetime.datetime.now() - datetime.timedelta(hours=1)
    if type(data) == dict:
        models.Register.objects.create(count=data.get("count", 0), time=time)


# Subscription
@shared_task(name='hourly-subscription-task')
def hourly_subscription_task():
    period = "hours"
    data = data_extractor.get_data(data_extractor.TRANSACTION_URL, params={'period': period})
    time = datetime.datetime.now() - datetime.timedelta(hours=1)
    if type(data) == dict:
        for key, value in data.items():
            models.Subscription.objects.create(sub_id=key, count=value, time=time)


# History
@shared_task(name='hourly-history-task') # TODO
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
                if internal_models.Broadcast.objects.get( # TODO exists_or_create for broadcast
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


# Data Update
@shared_task(name="daily-relations-update-task")
def daily_relations_update_task():
    # Update Categories
    url = data_extractor.CATEGORY_URL
    while True:
        data = data_extractor.get_data(
            url, {}
        )
        results = data.get("results")
        if results:
            bulk_create = []
            fields = ("name_ru", "name_en", "name_uz", "ordering")
            for category in results:
                try:
                    existing = internal_models.Category.objects.get(pk=category["id"])       
                    updated = False
                    for key, value in category.items():
                        if key in fields:
                            if existing.__dict__.get(key) != value:
                                updated = True
                                setattr(existing, key, value)
                    if updated:
                        existing.save()
                except internal_models.Category.DoesNotExist:
                    bulk_create.append(
                        internal_models.Category(
                            pk=category["id"], name_ru=category["name_ru"], name_en=category["name_en"], name_uz=category["name_uz"], ordering=category["ordering"]
                        )
                    )
            internal_models.Category.objects.bulk_create(bulk_create)

        next_url = data.get("next")
        if next_url:
            url = next_url
        else:
            break
    
    # Update Broadcast Categories
    url = data_extractor.BROADCAST_CATEGORY_URL
    while True:
        data = data_extractor.get_data(
            url, {}
        )
        results = data.get("results")
        if results:
            bulk_create = []
            fields = ("name_ru", "name_en", "name_uz")
            for b_category in results:
                try:
                    existing = internal_models.BroadcastCategory.objects.get(pk=b_category["id"])
                    for key, value in b_category.items():
                        if key in fields:
                            if existing.__dict__.get(key) != value:
                                updated = True
                                setattr(existing, key, value)
                    if updated:
                        existing.save()
                except internal_models.BroadcastCategory.DoesNotExist:
                    bulk_create.append(
                        internal_models.BroadcastCategory(
                            pk=b_category["id"], name_ru=b_category["name_ru"], name_en=b_category["name_en"], name_uz=b_category["name_uz"]
                        )
                    )
            internal_models.BroadcastCategory.objects.bulk_create(bulk_create)

        next_url = data.get("next")
        if next_url:
            url = next_url
        else:
            break
    
    # Update Subs
    url = data_extractor.SUBSCRIPTIONS_URL
    while True:
        data = data_extractor.get_data(
            url, {}
        )
        results = data.get("results")
        if results:
            bulk_create = []
            fields = ("title_ru", "title_en", "title_uz")
            for sub in results:
                try:
                    existing = internal_models.AllowedSubscription.objects.get(pk=sub["id"])
                    updated = False
                    for key, value in sub.items():
                        if key in fields:
                            if existing.__dict__.get(key) != value:
                                updated = True
                                setattr(existing, key, value)
                    if updated:
                        existing.save()
                except internal_models.AllowedSubscription.DoesNotExist:
                    bulk_create.append(
                        internal_models.AllowedSubscription(
                            pk=sub["id"], title_ru=sub["title_ru"], title_en=sub["title_en"], title_uz=sub["title_uz"]
                        )
                    )
            internal_models.AllowedSubscription.objects.bulk_create(bulk_create)    
        
        next_url = data.get("next")
        if next_url:
            url = next_url
        else:
            break
        
    # Update Sponsors
    url = data_extractor.SPONSORS_URL
    while True:
        data = data_extractor.get_data(
            url, {}
        )
        results = data.get("results")
        if results:
            bulk_create = []
            for sponsor in results:
                try:
                    existing = internal_models.Sponsor.objects.get(pk=sponsor["id"])
                    if existing.name != sponsor.get("name"):
                        existing.title = sponsor.get("name")
                        existing.save()
                except internal_models.Sponsor.DoesNotExist:
                    bulk_create.append(
                        internal_models.Sponsor(pk=sponsor["id"], name=sponsor["name"])
                    )
            internal_models.Sponsor.objects.bulk_create(set(bulk_create))
        
        next_url = data.get("next")
        if next_url:
            url = next_url
        else:
            break


@shared_task(name="daily-content-update-task")
def daily_content_update_task():
    contents = internal_models.Content.objects.all().select_related(
        "category"
    ).prefetch_related("sponsors", "allowed_subscriptions")
    
    id_slugs = contents.values_list("slug", flat=True)

    print("CONTENTS", id_slugs)
    
    # TODO ПЕРЕДЕЛАТЬ
    for content in contents:
        data = data_extractor.get_data(data_extractor.CONTENT_DATA_URL, params={"id_slugs": content.slug}).get("results").get(content.slug)
        if data:
            content_dict = content.__dict__
            updated = False
            for key, value in data.items():
                if content_dict.get(key) != value:
                    if not(key == "sponsors" or key == "allowed_subscriptions"): # TODO ADD CATEGORY
                        updated = True
                        setattr(content, key, value)
            
            content_sponsors = list(content.sponsors.all().values_list("pk", flat=True))
            content_subs = list(content.allowed_subscriptions.all().values_list("pk", flat=True))
            data_sponsors = data.get("sponsors")
            data_subs = data.get("allowed_subscriptions")
                        
            if content_sponsors != data_sponsors:
                # sponsors = etc.validate_sponsors(data_sponsors)
                content.sponsors.set(data_sponsors)
                updated = True
                
            if content_subs != data_subs:
                # subs = etc.validate_allowed_subscriptions()
                content.allowed_subscriptions.set(data_subs)
                updated = True

            if updated:
                content.save()
        else:
            print("no result")
            continue


app.conf.beat_schedule = {
    "daily-relations-update-task": {
        "task": "daily-relations-task",
        "schedule": crontab(hour="1", minute="5"),
    },
    "daily-content-update-task": { # 
        "task": "daily-content-update-task",
        "schedule": crontab(hour="0", minute="20"),
    },
    # TODO daily-broadcast-update-task
    #
    "daily-history-task": {
        "task": "hourly-register-task",
        "schedule": crontab(hour="0", minute="10"),
    },
    "hourly-history-task": {
        "task": "hourly-history-task",
        "schedule": crontab(hour="*", minute="0"),
    },
    #
    "hourly-register-task": {
        "task": "hourly-register-task",
        "schedule": crontab(hour="*", minute="1"),
    },
    "hourly-subscription-task": {
        "task": "hourly-subscription-task",
        "schedule": crontab(hour="*", minute="2"),
    },
}

import datetime
from django.db import connection
from django.db.models import Sum, Count
from celery import shared_task
from celery.schedules import crontab

from config.celery import app
from statistic import models
from internal import models as internal_models
from statistic.utils import data_extractor, etc, validators


# Register
@shared_task(name='hourly-register-task')
def hourly_register_task():
    period = "hours"
    time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=1)
    data = data_extractor.get_data(data_extractor.SIGNUP_URL, params={'period': period})
    if type(data) == dict:
        models.Register.objects.create(count=data.get("count", 0), time=time)


# Subscription
@shared_task(name='hourly-subscription-task')
def hourly_subscription_task():
    period = "hours"
    time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=1)
    data = data_extractor.get_data(data_extractor.TRANSACTION_URL, params={'period': period})
    if type(data) == dict:
        for key, value in data.items():
            models.Subscription.objects.create(sub_id=key, count=value, time=time)


# History
@shared_task(name='hourly-history-task')
def hourly_history_task():
    to_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    from_time = to_time - datetime.timedelta(hours=1)
    
    histories = models.History.objects.filter(
        time__range=(from_time, to_time),
    )
    print("Histories", histories, from_time, to_time)
    for history in histories:
        # Content
        if history.content_id:
            exists, category_id = etc.is_content_exists_or_create(
                {"content_id": history.content_id, "episode_id": history.episode_id},
                history.slug
            )
            if exists:
                content, _  = models.ContentHour.objects.get_or_create(
                    time=from_time, content_id=history.content_id, episode_id=history.episode_id,
                    sid=history.sid, age_group=history.age_group, gender=history.gender
                )
                content.watched_duration += history.duration
                content.save()
                # View Category

        # Broadcast
        elif history.broadcast_id:
            if etc.is_broadcast_exists_or_create(history.broadcast_id):
                broadcast, _ = models.BroadcastHour.objects.get_or_create(
                    time=from_time, broadcast_id=history.broadcast_id,
                    sid=history.sid, age_group=history.age_group, gender=history.gender
                )
                broadcast.watched_duration += history.duration
                broadcast.save()
                category_id = 5
        if category_id:
            view_category, _ = models.CategoryViewHour.objects.get_or_create(
                time=from_time, category_id=category_id, age_group=history.age_group, gender=history.gender
            )
            view_category.watched_users_count += 1
            view_category.save()


@shared_task(name="daily-history-task")
def daily_history_task():
    # to_time = datetime.datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
    # from_time = to_time - datetime.timedelta(days=1) # Yesterday
    from_time = datetime.datetime.now().replace(hour=12, minute=0, second=0, microsecond=0) # Yesterday
    to_time = from_time + datetime.timedelta(days=1)
    print("FROM TIME", from_time)
    # DAILY
    contents = internal_models.Content.objects.all()
    for content in contents:
        histories = models.History.objects.filter(
            time__range=(from_time, to_time), content_id=content.content_id, episode_id=content.episode_id,
        )
        for history in histories:
            daily_c, _ = models.ContentDay.objects.get_or_create(
                time=from_time, content_id=content.content_id, episode_id=content.episode_id,
                sid=history.sid, age_group=history.age_group, gender=history.gender
            )
            daily_c.watched_duration += history.duration
            daily_c.save()
            category_id = etc.category_by_content_id(daily_c.content_id)
            # View Category
            if category_id:
                view_category, _ = models.CategoryViewDay.objects.get_or_create(
                    time=from_time, category_id=category_id, age_group=history.age_group, gender=history.gender
                )
                view_category.watched_users_count += 1
                view_category.save()
            
    broadcasts = internal_models.Broadcast.objects.all()
    for broadcast in broadcasts:
        histories = models.History.objects.filter(
            time__range=(from_time, to_time), broadcast_id=broadcast.broadcast_id
        )
        for history in histories:
            daily_b, _ = models.BroadcastDay.objects.get_or_create(
                time=from_time, broadcast_id=broadcast.broadcast_id,
                sid=history.sid, age_group=history.age_group, gender=history.gender
            )
            daily_b.watched_duration += history.duration
            daily_b.save()
            # View Category
            view_category, _ = models.CategoryViewDay.objects.get_or_create(
                time=from_time, category_id=5, age_group=history.age_group, gender=history.gender
            )
            view_category.watched_users_count += 1
            view_category.save()
    # Daily ended

    # MONTHLY
    daily_contents = models.ContentDay.objects.filter(time=from_time)
    for content in daily_contents:
        monthly_c = models.ContentMonth.objects.create(
            time=from_time, content_id=content.content_id, episode_id=content.episode_id,
            sid=content.sid, age_group=content.age_group, gender=content.gender
        )
        monthly_c.watched_users_count += 1
        monthly_c.watched_duration += content.watched_duration
        monthly_c.save()
        category_id = etc.category_by_content_id(monthly_c.content_id)
        # View Category
        if category_id:
            view_category, _ = models.CategoryViewMonth.objects.get_or_create(
                time=from_time, category_id=category_id, age_group=history.age_group, gender=history.gender
            )
            view_category.watched_users_count += 1
            view_category.save()

    daily_broadcasts = models.BroadcastDay.objects.filter(time=from_time)
    for broadcast in daily_broadcasts:
        monthly_b = models.BroadcastMonth.objects.create(
            time=from_time, broadcast_id=broadcast.broadcast_id,
            sid=broadcast.sid, age_group=broadcast.age_group, gender=broadcast.gender
        )
        monthly_b.watched_users_count += 1
        monthly_b.watched_duration += broadcast.watched_duration
        monthly_b.save()
        # View Category
        view_category, _ = models.CategoryViewMonth.objects.get_or_create(
            time=from_time, category_id=5, age_group=history.age_group, gender=history.gender
        )
        view_category.watched_users_count += 1
        view_category.save()
    # Monthly ended
    
    cursor = connection.cursor()
    query = f"""SELECT content_id, SUM(watched_users_count), age_group, gender
                FROM statistic_content_month
                WHERE (time = '{from_time}')
                GROUP BY content_id, watched_users_count, age_group, gender"""
    cursor.execute(query)
    stat = cursor.fetchall()
    print("STAT", stat)
    
    for s in stat:
        # TODO add data to DailyDetailView also
        time, content_id, watched_users_count, age_group, gender = s
        exists, category_id = etc.is_content_exists_or_create({"content_id": content_id}, str(content_id))

        if exists:
            detail, _ = models.DailyTotalViews.objects.get_or_create(
                time=from_time, age_group=age_group, gender=gender
            )
            detail.total_views += watched_users_count
            detail.save()
            
            total, _ = models.DailyContentViews.objects.get_or_create(
                time=time, category_id=category_id, age_group=age_group, gender=gender
            )
            total.total_views += watched_users_count
            total.save()


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
def daily_content_update_task(update_relations=False):
    if update_relations:
        daily_relations_update_task()

    contents = internal_models.Content.objects.all().select_related(
        "category"
    ).prefetch_related("sponsors", "allowed_subscriptions")
    
    for content in contents:
        data = data_extractor.get_data(data_extractor.CONTENT_DATA_URL, params={"id_slugs": content.slug}).get("results").get(content.slug)
        content_dict = content.__dict__
        for key, value in data.items():
            if content_dict.get(key) != value:
                if not(key=="category_id" or key == "sponsors" or key == "allowed_subscriptions"):
                    setattr(content, key, value)

        content_sponsors = list(content.sponsors.all().values_list("pk", flat=True))
        content_subscriptions = list(content.allowed_subscriptions.all().values_list("pk", flat=True))
        
        if content_dict.get("category_id") != data.get("category_id"):
            if data.get("category_id"):
                if validators.is_category_valid(data.get("category_id")):
                    content.category_id = data.get("category_id")
            else:
                content.category = None

        if content_subscriptions != data.get("allowed_subscriptions"):
            if data.get("allowed_subscriptions"):
                content.allowed_subscriptions.set(validators.validate_subscriptions(data.get("allowed_subscriptions")))
            else:
                content.allowed_subscriptions.set([])

        if content_sponsors != data.get("sponsors"):
            if data.get("sponsors"):
                content.sponsors.set(validators.validate_sponsors(data.get("sponsors")))
            else:
                content.sponsors.set([])
        content.save()


@shared_task(name="daily-broadcast-update-task")
def daily_broadcast_update_task(update_relations=False):
    if update_relations:
        daily_relations_update_task()

    url = data_extractor.BROADCAST_DATA_URL
    while True:
        data = data_extractor.get_data(
            url, {}
        )
        results = data.get("results")
        if results:
            for broadcast in results:
                try:
                    existing = internal_models.Broadcast.objects.get(broadcast_id=broadcast["tv_id"])  
                    existing_subscriptions = list(existing.allowed_subscriptions.all().values_list("pk", flat=True))
                    title = broadcast.get("title")
                    quality = broadcast.get("quality")
                    category_id = broadcast.get("category")
                    allowed_subscriptions = broadcast.get("allowed_subscriptions")

                    if title:
                        existing.title = title
                    if quality:
                        existing.quality = quality

                    if existing.__dict__.get("category_id") != category_id:
                        if category_id:
                            if validators.is_broadcast_category_valid(category_id):
                                existing.category_id = category_id
                            else:
                                existing.category = None
                    
                    if existing_subscriptions != allowed_subscriptions:
                        if allowed_subscriptions:
                            existing.allowed_subscriptions.set(validators.validate_subscriptions(allowed_subscriptions))
                        else:
                            existing.allowed_subscriptions.set([])
                    
                    existing.save()
                except internal_models.Broadcast.DoesNotExist:
                    instance = {"broadcast_id": broadcast["tv_id"], "title": broadcast["title"], "quality": broadcast.get("quality")}
                    category_id = broadcast.get("category")
                    allowed_subscriptions = broadcast.get("allowed_subscriptions")

                    if category_id:
                        if validators.is_broadcast_category_valid(category_id):
                            instance["category_id"] = category_id

                    existing = internal_models.Broadcast.objects.create(**instance)
                    
                    if allowed_subscriptions:
                        existing.allowed_subscriptions.set(validators.validate_subscriptions(allowed_subscriptions))
                        existing.save()

        next_url = data.get("next")
        if next_url:
            url = next_url
        else:
            break
#


app.conf.beat_schedule = {
    # Data Update
    "daily-relations-update-task": {
        "task": "daily-relations-update-task",
        "schedule": crontab(hour="0", minute="0"),
    },
    "daily-content-update-task": {
        "task": "daily-content-update-task",
        "schedule": crontab(hour="0", minute="10"),
    },
    "daily-broadcast-update-task": {
        "task": "daily-broadcast-update-task",
        "schedule": crontab(hour="0", minute="15"),
    },
    "daily-total-views-task": {
        "task": "daily-total-views-task",
        "schedule": crontab(hour="0", minute="30"),
    },
    #
    "daily-history-task": {
        "task": "daily-history-task",
        "schedule": crontab(hour="0", minute="20"),
    },
    "hourly-history-task": {
        "task": "hourly-history-task",
        "schedule": crontab(hour="*", minute="5"),
    },
    #
    "hourly-register-task": {
        "task": "hourly-register-task",
        "schedule": crontab(hour="*", minute="1"),
    },
    "hourly-subscription-task": {
        "task": "hourly-subscription-task",
        "schedule": crontab(hour="*", minute="1"),
    },
}

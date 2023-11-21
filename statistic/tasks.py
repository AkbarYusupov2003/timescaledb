import datetime
from django.db import connection
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


def hourly_content_history_task():
    to_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    from_time = to_time - datetime.timedelta(hours=1)
    
    print("TIME: ", from_time, to_time)

    histories = models.History.objects.filter(
        time__range=(from_time, to_time),
    ) #.annotate(a=Sum("duration"))
    
    # histories.filter(contend_id__isnull=False)
    
    for history in histories:
        try:
            if history.content_id:
                print("history content", history.content_id, history.episode_id)
                content = Content.objects.get(
                    content_id=history.content_id, episode_id=history.episode_id
                )
                print("Content: ", content)
                # add history to contenthour
                models.ContentHour.objects.get_or_create
                
            elif history.broadcast_id:
                print("history broadcast", history.broadcast_id)
        except:
            print("Exception")
        
    print("histories", histories)  
    
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

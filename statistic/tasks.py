import datetime
from celery import shared_task
from celery.schedules import crontab

from config.celery import app
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


def synchronize_content_task():
    
    data = data_extractor.get_data(data_extractor.CONTENT_DATA_URL)
    print("DATA: ", data)
    
    # def get_content_data(params):
    # data = get_request(CONTENT_DATA_URL, params=params).get('results')
    # return data


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

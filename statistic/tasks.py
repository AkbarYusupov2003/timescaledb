from datetime import datetime, timedelta, timezone
from celery import shared_task
from celery.schedules import crontab

from config.celery import app
from statistic.utils import main


@shared_task(name='hourly-register-task')
def hourly_register_task():
    main.execute_register_task("hours")
    # stat.execute_content_task(stat.HOURLY)


app.conf.beat_schedule = {
    'hourly-register-task': {
        'task': 'hourly-register-task',
        'schedule': crontab(minute='0', hour='*'),
    },
}

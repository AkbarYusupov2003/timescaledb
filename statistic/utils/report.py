import os
from datetime import datetime
import tablib
from celery import shared_task

from api.v1 import utils
from internal import models as internal_models
from statistic import models


@shared_task
def generate_content_report(pk, data, from_date, to_date):
    try:
        report = models.Report.objects.get(pk=pk)
        table = tablib.Dataset(headers=("С", "До", "ID Контента", "ID Эпизода", "Название", "Категория", "Количество просмотров", "Время просмотров", "Длительность", "Язык"))
        step = len(data) // 10
        for count, val in enumerate(data):
            category = val.get("category").get("name_ru") if val.get("category") else "Отсутствует"
            is_russian = "Русский" if val.get("is_russian") else "Узбекский"
            table.append(
                row=(
                    from_date, to_date, val["content_id"], val["episode_id"], val["title_ru"], category, 
                    val["watched_users"], val["watched_duration"], val["duration"], is_russian
                )
            )
            if step != 0:
                if count % step == 0:
                    report.progress = count // step
                    report.save()
        file_path = get_file_path()
        with open(file_path, "wb") as f:
            f.write(table.export("xlsx"))
        report.file = file_path.replace("media/", "")
        report.progress = 100
        report.status = models.Report.StatusChoices.finished
        report.save()
    except:
        models.Report.objects.filter(pk=pk).update(status=models.Report.StatusChoices.failed)


@shared_task
def generate_broadcast_report(pk, data, from_date, to_date):
    try:
        report = models.Report.objects.get(pk=pk)
        table = tablib.Dataset(headers=("С", "До", "ID Телеканала", "Название", "Категория", "Количество просмотров", "Время просмотров", "Язык"))
        step = len(data) // 10
        for count, val in enumerate(data):
            category = val.get("category").get("name_ru") if val.get("category") else "Отсутствует"
            table.append(
                row=(
                    from_date, to_date, val["broadcast_id"], val["title"], category, 
                    val["watched_users"], val["watched_duration"], "Неизвестен"
                )
            )
            if step != 0:
                if count % step == 0:
                    report.progress = count // step
                    report.save()
        file_path = get_file_path()
        with open(file_path, "wb") as f:
            f.write(table.export("xlsx"))
        report.file = file_path.replace("media/", "")
        report.progress = 100
        report.status = models.Report.StatusChoices.finished
        report.save()
    except:
        models.Report.objects.filter(pk=pk).update(status=models.Report.StatusChoices.failed)


#------------------------------------------------------------------------------------------------------------
@shared_task
def generate_register_report(pk, data, period):
    try:
        report = models.Report.objects.get(pk=pk)
        table = tablib.Dataset(headers=("Период", "Время", "Количество регистраций"))
        translated_period = utils.TRANSLATE_ALLOWED_PERIODS[period]
        step = len(data) // 10
        for count, val in enumerate(data):
            time = str(val[0]) if period == "hours" else str(val[0]).split(" ")[0]
            table.append(row=(translated_period, time, val[1]))
            if step != 0:
                if count % step == 0:
                    report.progress = count // step
                    report.save()
        file_path = get_file_path()
        with open(file_path, "wb") as f:
            f.write(table.export("xlsx"))
        report.file = file_path.replace("media/", "")
        report.progress = 100
        report.status = models.Report.StatusChoices.finished
        report.save()
    except:
        models.Report.objects.filter(pk=pk).update(status=models.Report.StatusChoices.failed)


@shared_task
def generate_subscription_report(pk, data, period, sub_id):
    try:
        report = models.Report.objects.get(pk=pk)
        sub_name = internal_models.AllowedSubscription.objects.get(pk=sub_id).title_ru
        table = tablib.Dataset(headers=("Период", f"Время", f"Количество подписок ( {sub_name} )"))
        translated_period = utils.TRANSLATE_ALLOWED_PERIODS[period]
        step = len(data) // 10
        for count, val in enumerate(data):
            time = str(val[0]) if period == "hours" else str(val[0]).split(" ")[0]
            table.append(row=(translated_period, time, val[1]))
            if step != 0:
                if count % step == 0:
                    report.progress = count // step
                    report.save()
        file_path = get_file_path()
        with open(file_path, "wb") as f:
            f.write(table.export("xlsx"))
        report.file = file_path.replace("media/", "")
        report.progress = 100
        report.status = models.Report.StatusChoices.finished
        report.save()
    except:
        models.Report.objects.filter(pk=pk).update(status=models.Report.StatusChoices.failed)


#------------------------------------------------------------------------------------------------------------
@shared_task
def generate_category_views_report(pk, data, category, age_group, period):
    try:
        report = models.Report.objects.get(pk=pk)
        table = tablib.Dataset(
            headers=("Фильтр по категории", "Фильтр по возрастным группам", "Период", "Время", "Просмотры детей", "Просмотры женщин", "Просмотры мужчин")
        )
        translated_period = utils.TRANSLATE_ALLOWED_PERIODS[period]
        step = len(data) // 10
        for count, val in enumerate(data):
            table.append(
                row=(
                    category, age_group, translated_period, str(val["time"]), val["children"], val["women"], val["men"]
                )
            )
            if step != 0:
                if count % step == 0:
                    report.progress = count // step
                    report.save()
        file_path = get_file_path()
        with open(file_path, "wb") as f:
            f.write(table.export("xlsx"))
        report.file = file_path.replace("media/", "")
        report.progress = 100
        report.status = models.Report.StatusChoices.finished
        report.save()
    except:
        models.Report.objects.filter(pk=pk).update(status=models.Report.StatusChoices.failed)


#------------------------------------------------------------------------------------------------------------

def get_file_path():
    time = datetime.now()
    path = f"media/reports/{time.year}/{time.month}/{time.day}"
    if not os.path.exists(path):
        os.makedirs(path)
    return f"{path}/stat_{time.microsecond}.xlsx"

from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


AGE_GROUPS = (
    ("0", "0-6"),
    ("1", "7-12"),
    ("2", "13-15"),
    ("3", "16-18"),
    ("4", "19-21"),
    ("5", "22-28"),
    ("6", "29-36"),
    ("7", "37-46"),
    ("8", "47-54"),
    ("9", "55+"),
)

GENDERS = (
    ("M", "Мужчина"),
    ("W", "Женщина"),
)

AGE_GROUPS_LIST = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
GENDERS_LIST = ("M", "W")


class TimescaleModel(models.Model):
    time = TimescaleDateTimeField(verbose_name="Создано", interval="1 day")
    objects = TimescaleManager()

    class Meta:
        abstract = True


# Content Statistic
class ContentHour(TimescaleModel): 
    content_id = models.PositiveIntegerField(
        verbose_name="ID Контента"
    )
    episode_id = models.PositiveIntegerField(
        verbose_name="ID Эпизода", blank=True, null=True
    )
    sid = models.CharField(verbose_name="Сессия", max_length=128)
    #
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    age_group_count = models.PositiveIntegerField(
        verbose_name="Количество возрастной группы", default=0
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    gender_count = models.PositiveIntegerField(
        verbose_name="Количество пола", default=0
    )
    #
    country = models.CharField(
        verbose_name="Страна", max_length=32
    )
    device = models.CharField(
        verbose_name=("Устройство"), max_length=64
    )
    watched_users_count = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )
    
    class Meta:
        verbose_name = "Контент за час"
        verbose_name_plural = "Контенты за час"
        db_table = "statistic_content_hour"
        ordering = ("time",)


class ContentDay(TimescaleModel):
    content_id = models.PositiveIntegerField(
        verbose_name="ID Контента"
    )
    episode_id = models.PositiveIntegerField(
        verbose_name="ID Эпизода", blank=True, null=True
    )
    sid = models.CharField(verbose_name="Сессия", max_length=128)
    #
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    age_group_count = models.PositiveIntegerField(
        verbose_name="Количество возрастной группы", default=0
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    gender_count = models.PositiveIntegerField(
        verbose_name="Количество пола", default=0
    )
    #
    country = models.CharField(
        verbose_name="Страна", max_length=32
    )
    device = models.CharField(
        verbose_name=("Устройство"), max_length=64
    )
    watched_users_count = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )

    class Meta:
        verbose_name = "Контент за день"
        verbose_name_plural = "Контенты за день"
        db_table = "statistic_content_day"
        ordering = ("-time",)


class ContentMonth(TimescaleModel):
    content_id = models.PositiveIntegerField(
        verbose_name="ID Контента"
    )
    episode_id = models.PositiveIntegerField(
        verbose_name="ID Эпизода", blank=True, null=True
    )
    sid = models.CharField(verbose_name="Сессия", max_length=128)
    #
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    age_group_count = models.PositiveIntegerField(
        verbose_name="Количество возрастной группы", default=0
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    gender_count = models.PositiveIntegerField(
        verbose_name="Количество пола", default=0
    )
    #
    country = models.CharField(
        verbose_name="Страна", max_length=32
    )
    device = models.CharField(
        verbose_name=("Устройство"), max_length=64
    )
    watched_users_count = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )

    class Meta:
        verbose_name = "Контент за месяц"
        verbose_name_plural = "Контенты за месяц"
        db_table = "statistic_content_month"
        ordering = ("-time",)


# Broadcast Statistic
class BroadcastHour(TimescaleModel):
    broadcast_id = models.PositiveIntegerField(
        verbose_name="ID Телеканала"
    )
    sid = models.CharField(verbose_name="Сессия", max_length=128)
    #
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    age_group_count = models.PositiveIntegerField(
        verbose_name="Количество возрастной группы", default=0
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    gender_count = models.PositiveIntegerField(
        verbose_name="Количество пола", default=0
    )
    #
    country = models.CharField(
        verbose_name="Страна", max_length=32
    )
    device = models.CharField(
        verbose_name=("Устройство"), max_length=64
    )
    watched_users_count = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )
    
    class Meta:
        verbose_name = "Телеканал за час"
        verbose_name_plural = "Телеканалы за час"
        db_table = "statistic_broadcast_hour"
        ordering = ("-time",)


class BroadcastDay(TimescaleModel):
    broadcast_id = models.PositiveIntegerField(
        verbose_name="ID Телеканала"
    )
    sid = models.CharField(verbose_name="Сессия", max_length=128)
    #
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    age_group_count = models.PositiveIntegerField(
        verbose_name="Количество возрастной группы", default=0
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    gender_count = models.PositiveIntegerField(
        verbose_name="Количество пола", default=0
    )
    #
    country = models.CharField(
        verbose_name="Страна", max_length=32
    )
    device = models.CharField(
        verbose_name=("Устройство"), max_length=64
    )
    watched_users_count = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )

    class Meta:
        verbose_name = "Телеканал за день"
        verbose_name_plural = "Телеканалы за день"
        db_table = "statistic_broadcast_day"
        ordering = ("-time",)


class BroadcastMonth(TimescaleModel):
    broadcast_id = models.PositiveIntegerField(
        verbose_name="ID Телеканала"
    )
    sid = models.CharField(verbose_name="Сессия", max_length=128)
    #
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    age_group_count = models.PositiveIntegerField(
        verbose_name="Количество возрастной группы", default=0
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    gender_count = models.PositiveIntegerField(
        verbose_name="Количество пола", default=0
    )
    #
    country = models.CharField(
        verbose_name="Страна", max_length=32
    )
    device = models.CharField(
        verbose_name=("Устройство"), max_length=64
    )
    watched_users_count = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )

    class Meta:
        verbose_name = "Телеканал за месяц"
        verbose_name_plural = "Телеканалы за месяц"
        db_table = "statistic_broadcast_month"
        ordering = ("-time",)


# --------------------------------------------------------------------
class History(TimescaleModel):
    slug = models.SlugField()
    sid = models.CharField(verbose_name="Сессия", max_length=128)
    content_id = models.PositiveIntegerField(
        verbose_name="ID Контента", blank=True, null=True
    )
    broadcast_id = models.PositiveIntegerField(
        verbose_name="ID Телеканала", blank=True, null=True
    )
    episode_id = models.PositiveIntegerField(
        verbose_name="ID Эпизода", blank=True, null=True
    )
    user_agent = models.CharField(max_length=128)
    ip_address = models.CharField(
        verbose_name=("IP адрес"), max_length=16
    )
    country = models.CharField(
        verbose_name=("Страна"),
        max_length=32
    )
    device = models.CharField(
        verbose_name=("Устройство"), max_length=64
    )
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    duration = models.PositiveIntegerField(
        verbose_name="Длительность", default=10
    )

    class Meta:
        verbose_name = "История просмотра"
        verbose_name_plural = "Истории просмотров"
        db_table = "statistic_history"
        ordering = ("-time",)


class Register(TimescaleModel):    
    count = models.IntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Регистрация"
        verbose_name_plural = "Регистрации"
        db_table = "statistic_register"
        ordering = ("-time",)


class Subscription(TimescaleModel):
    sub_id = models.CharField(verbose_name="ID Подписки", max_length=8)
    count = models.IntegerField(verbose_name="Количество")
    
    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        db_table = "statistic_subscription"
        ordering = ("-time",)


class Report(models.Model):
    STATUSES = (
        ("PENDING", "В ожидании"),
        ("STARTED", "В исполнении"),
        ("FAILURE", "Ошибка"),
        ("FINISHED", "Завершен")
    )

    status = models.CharField(verbose_name="Статус", choices=STATUSES, default="PENDING")
    group = models.CharField(verbose_name="Группа", max_length=128)
    rows_count = models.PositiveIntegerField(verbose_name="Количество строк", null=True, blank=True)
    data = models.JSONField(verbose_name="Данные", default=dict, blank=True, null=True)
    file = models.FileField(
        verbose_name="Файл", upload_to="reports/%Y/%m/%d", null=True, blank=True
    )
    created_at = models.DateTimeField(
        verbose_name="Создано", auto_now_add=True
    )

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"
        ordering = ("-created_at",)

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
APP_TYPES_LIST = ("app", "tv", "web")


class TimescaleModel(models.Model):
    time = TimescaleDateTimeField(verbose_name="Создано", interval="3 month") # TODO обсудить chunk size
    objects = TimescaleManager()

    class Meta:
        abstract = True


class History(models.Model):
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
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    duration = models.PositiveIntegerField(
        verbose_name="Длительность", default=10
    )
    time = TimescaleDateTimeField(verbose_name="Создано", interval="1 month")
    objects = TimescaleManager()

    class Meta:
        verbose_name = "История просмотра"
        verbose_name_plural = "01. Истории просмотров"
        db_table = "statistic_history"
        ordering = ("-time",)


# -------------------------------------------------------------------------------------------------
class RegisterHour(TimescaleModel):    
    count = models.IntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Регистрации в час"
        verbose_name_plural = "02. Регистрации в часы"
        db_table = "statistic_register_hour"
        ordering = ("-time",)


class RegisterDay(TimescaleModel):
    count = models.IntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Регистрации в день"
        verbose_name_plural = "03. Регистрации в дни"
        db_table = "statistic_register_day"
        ordering = ("-time",)


class SubscriptionHour(TimescaleModel):
    sub_id = models.CharField(verbose_name="ID Подписки", max_length=8)
    count = models.IntegerField(verbose_name="Количество")
    
    class Meta:
        verbose_name = "Подписки в час"
        verbose_name_plural = "04. Подписки в часы"
        db_table = "statistic_subscription_hour"
        ordering = ("-time",)


class SubscriptionDay(TimescaleModel):
    sub_id = models.CharField(verbose_name="ID Подписки", max_length=8)
    count = models.IntegerField(verbose_name="Количество")
    
    class Meta:
        verbose_name = "Подписки в день"
        verbose_name_plural = "05. Подписки в дни"
        db_table = "statistic_subscription_day"
        ordering = ("-time",)


# -------------------------------------------------------------------------------------------------
class DeviceVisitsHour(TimescaleModel):
    APP_TYPES = (
        ("app", "app"),
        ("tv", "tv"),
        ("web", "web")
    )
    DEVICE_TYPES = (
        ("Smartphone", "Smartphone"),
        ("Tablet", "Tablet"),
        ("SmartTV", "SmartTV"),
        ("Desktop", "Desktop"),
    )
    OS_TYPES = (
        # "Other",
        ("Android", "Android"),
        ("iOS", "iOS"),
        ("Windows", "Windows"),
        ("Linux", "Linux"),
        ("Tizen", "Tizen"),
        ("Web0S", "Web0S"),
        ("Mac OS X", "Mac OS X"),
        ("Chrome OS", "Chrome OS"),
        ("FreeBSD", "FreeBSD"),
        ("Ubuntu", "Ubuntu"),
    )
    
    app_type = models.CharField(choices=APP_TYPES)
    device_type = models.CharField(choices=DEVICE_TYPES)
    os_type = models.CharField(choices=OS_TYPES)
    country = models.CharField(max_length=32)

    class Meta:
        verbose_name = "Посещения с девайсов в час"
        verbose_name_plural = "06. Посещения с девайсов за час"
        db_table = "statistic_device_visits_hour"
        ordering = ("-time",)


class DeviceVisitsDay(TimescaleModel):
    APP_TYPES = (
        ("app", "app"),
        ("tv", "tv"),
        ("web", "web")
    )
    DEVICE_TYPES = (
        ("Smartphone", "Smartphone"),
        ("Tablet", "Tablet"),
        ("SmartTV", "SmartTV"),
        ("Desktop", "Desktop"),
    )
    OS_TYPES = (
        ("Android", "Android"),
        ("iOS", "iOS"),
        ("Windows", "Windows"),
        ("Linux", "Linux"),
        ("Tizen", "Tizen"),
        ("Web0S", "Web0S"),
        ("Mac OS X", "Mac OS X"),
        ("Chrome OS", "Chrome OS"),
        ("FreeBSD", "FreeBSD"),
        ("Ubuntu", "Ubuntu"),
    )

    app_type = models.CharField(choices=APP_TYPES)
    device_type = models.CharField(choices=DEVICE_TYPES)
    os_type = models.CharField(choices=OS_TYPES)
    country = models.CharField(max_length=32)

    class Meta:
        verbose_name = "Посещения с девайсов день"
        verbose_name_plural = "07. Посещения с девайсов за день"
        db_table = "statistic_device_visits_day"
        ordering = ("-time",)


class DeviceVisitsMonth(TimescaleModel):
    APP_TYPES = (
        ("app", "app"),
        ("tv", "tv"),
        ("web", "web")
    )
    DEVICE_TYPES = (
        ("Smartphone", "Smartphone"),
        ("Tablet", "Tablet"),
        ("SmartTV", "SmartTV"),
        ("Desktop", "Desktop"),
    )
    OS_TYPES = (
        ("Android", "Android"),
        ("iOS", "iOS"),
        ("Windows", "Windows"),
        ("Linux", "Linux"),
        ("Tizen", "Tizen"),
        ("Web0S", "Web0S"),
        ("Mac OS X", "Mac OS X"),
        ("Chrome OS", "Chrome OS"),
        ("FreeBSD", "FreeBSD"),
        ("Ubuntu", "Ubuntu"),
    )

    app_type = models.CharField(choices=APP_TYPES)
    device_type = models.CharField(choices=DEVICE_TYPES)
    os_type = models.CharField(choices=OS_TYPES)
    country = models.CharField(max_length=32)

    class Meta:
        verbose_name = "Посещения с девайсов за месяц"
        verbose_name_plural = "08. Посещения с девайсов за месяц"
        db_table = "statistic_device_visits_month"
        ordering = ("-time",)


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
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    #
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )
    
    class Meta:
        verbose_name = "Контент за час"
        verbose_name_plural = "09. Контенты за час"
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
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    #
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )

    class Meta:
        verbose_name = "Контент за день"
        verbose_name_plural = "10. Контенты за день"
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
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    #
    watched_users_count = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )

    class Meta:
        verbose_name = "Контент за месяц"
        verbose_name_plural = "11. Контенты за месяц"
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
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    #
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )
    
    class Meta:
        verbose_name = "Телеканал за час"
        verbose_name_plural = "12. Телеканалы за час"
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
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    #
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )

    class Meta:
        verbose_name = "Телеканал за день"
        verbose_name_plural = "13. Телеканалы за день"
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
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    #
    watched_users_count = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )
    watched_duration = models.PositiveIntegerField(
        verbose_name="Время просмотров", default=0
    )

    class Meta:
        verbose_name = "Телеканал за месяц"
        verbose_name_plural = "14. Телеканалы за месяц"
        db_table = "statistic_broadcast_month"
        ordering = ("-time",)


# --------------------------------------------------------------------
class AdsView(TimescaleModel):
    
    class Meta:
        verbose_name = "Просмотр рекламы"
        verbose_name_plural = "17. Просмотры реклам"
        db_table = "statistic_ads_view"
        ordering = ("-time",)


# --------------------------------------------------------------------
class CategoryViewHour(TimescaleModel):
    category_id = models.PositiveSmallIntegerField(verbose_name="ID Категории")
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    watched_users_count = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )

    class Meta:
        verbose_name = "Просмотр категории за час"
        verbose_name_plural = "18. Просмотры категорий за час"
        db_table = "statistic_category_view_hour"
        ordering = ("-time",)


class CategoryViewDay(TimescaleModel):
    category_id = models.PositiveSmallIntegerField(verbose_name="ID Категории")
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    watched_users_count = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )

    class Meta:
        verbose_name = "Просмотр категории за день"
        verbose_name_plural = "19. Просмотры категорий за день"
        db_table = "statistic_category_view_day"
        ordering = ("-time",)


class CategoryViewMonth(TimescaleModel):
    category_id = models.PositiveSmallIntegerField(verbose_name="ID Категории")
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    watched_users_count = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )

    class Meta:
        verbose_name = "Просмотр категории за месяц"
        verbose_name_plural = "20. Просмотры категорий за месяц"
        db_table = "statistic_category_view_month"
        ordering = ("-time",)


# --------------------------------------------------------------------
class DailyTotalViews(TimescaleModel):
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    total_views = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )
    
    class Meta:
        verbose_name = "Общий просмотр"
        verbose_name_plural = "15. Общие просмотры"
        db_table = "statistic_daily_total_views"
        ordering = ("-time",)


class DailyContentViews(TimescaleModel):
    content_id = models.PositiveIntegerField(
        verbose_name="ID Контента", blank=True, null=True
    )
    episode_id = models.PositiveIntegerField(
        verbose_name="ID Эпизода", blank=True, null=True
    )
    #
    category_id = models.PositiveSmallIntegerField(verbose_name="ID Категории", default=1)
    age_group = models.CharField(
        verbose_name="Возрастная группа", choices=AGE_GROUPS
    )
    gender = models.CharField(
        verbose_name="Пол", choices=GENDERS
    )
    total_views = models.PositiveIntegerField(
        verbose_name="Количество просмотров", default=0
    )

    class Meta:
        verbose_name = "Детальные просмотры"
        verbose_name_plural = "16. Детальные просмотры"
        db_table = "statistic_daily_content_views"
        ordering = ("-time",)


# ---------------------------------------------------------------------
class Report(models.Model):
    class SectionChoices(models.TextChoices):
        content = "CONTENT", "Контент"
        broadcast = "BROADCAST", "Телеканалы"
        register = "REGISTER", "Регистрации"
        subscriptions = "SUBSCRIPTIONS", "Подписки"
        visits = "VISITS", "Посещения с девайсов" # TODO
        category_views = "CATEGORY_VIEWS", "Просмотры категорий"
        ads = "ADS", "Реклама" # TODO

    class StatusChoices(models.TextChoices):
        generating = "GENERATING", "Генерируется"
        failed = "FAILED", "Ошибка"
        finished = "FINISHED", "Завершен"

    section = models.CharField(verbose_name="Раздел", choices=SectionChoices.choices)
    status = models.CharField(verbose_name="Статус", choices=StatusChoices.choices, default="GENERATING")
    additional_data = models.JSONField(verbose_name="Дополнительные данные", default=dict, blank=True, null=True)
    file = models.FileField(verbose_name="Файл", upload_to="reports/%Y/%m/%d", null=True, blank=True)
    progress = models.PositiveSmallIntegerField(verbose_name="Прогресс генерации", default=0)
    is_downloaded = models.BooleanField(verbose_name="Скачан ли", default=False)
    created_at = models.DateTimeField(verbose_name="Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"
        ordering = ("-created_at",)
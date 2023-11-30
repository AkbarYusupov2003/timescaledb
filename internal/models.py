from django.db import models


class AllowedSubscription(models.Model):
    title_ru = models.CharField(
        verbose_name="Название", max_length=128
    )
    title_en = models.CharField(
        verbose_name="Название на английском", max_length=128, blank=True
    )
    title_uz = models.CharField(
        verbose_name="Название на узбекском", max_length=128, blank=True
    )

    def __str__(self):
        return self.title_ru

    class Meta:
        verbose_name = "Разрешенная подписка"
        verbose_name_plural = "Разрешенные подписки"


class Sponsor(models.Model):
    name = models.CharField(verbose_name="Название", max_length=255)
    is_chosen = models.BooleanField(verbose_name="Выбран", default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Спонсор"
        verbose_name_plural = "Спонсоры"


class Category(models.Model):
    name_ru = models.CharField(
        verbose_name="Название на русском", max_length=255
    )
    name_en = models.CharField(
        verbose_name="Название на английском", max_length=255, blank=True
    )
    name_uz = models.CharField(
        verbose_name="Название на узбекском", max_length=255, blank=True
    )
    ordering = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name_ru

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("ordering",)


class BroadcastCategory(models.Model):
    name_ru = models.CharField(
        verbose_name="Название на русском", max_length=255
    )
    name_en = models.CharField(
        verbose_name="Название на английском", max_length=255, blank=True
    )
    name_uz = models.CharField(
        verbose_name="Название на узбекском", max_length=255, blank=True
    )

    def __str__(self):
        return self.name_ru

    class Meta:
        verbose_name = "Категория телеканалов"
        verbose_name_plural = "Категории телеканалов"


class Content(models.Model):
    title_ru = models.CharField(
        verbose_name="Название на русском", max_length=255
    )
    title_en = models.CharField(
        verbose_name="Название на английском", max_length=255, blank=True
    )
    title_uz = models.CharField(
        verbose_name="Название на узбекском", max_length=255, blank=True
    )
    #
    content_id = models.PositiveIntegerField(verbose_name="ID Контента")
    episode_id = models.PositiveIntegerField(verbose_name="ID Эпизода", null=True, blank=True)
    #
    is_russian = models.BooleanField(verbose_name="На русском", default=True)
    category = models.ForeignKey(
        Category, verbose_name="Категории", on_delete=models.PROTECT, null=True, blank=True
    )
    sponsors = models.ManyToManyField(
        Sponsor, verbose_name="Спонсоры", blank=True
    )
    allowed_subscriptions = models.ManyToManyField(
        AllowedSubscription, verbose_name="Разрешенные подписки", blank=True
    )
    #
    duration = models.PositiveIntegerField(
        verbose_name="Длительность", null=True, blank=True
    )
    slug = models.SlugField(unique=True)
    year = models.PositiveSmallIntegerField(
        verbose_name="Год", null=True, blank=True
    )

    class Meta:
        verbose_name = "Контент"
        verbose_name_plural = "Контенты"
        unique_together = ("content_id", "episode_id")


class Broadcast(models.Model):
    QUALITIES = (
        ("sd", "SD"),
        ("hd", "HD"),
        ("fhd", "FULL HD")
    )
    
    broadcast_id = models.PositiveBigIntegerField(
        verbose_name="ID Телеканала", unique=True
    )
    title = models.CharField(
        verbose_name="Название", max_length=255, null=True, blank=True
    )
    quality = models.CharField(
        verbose_name="Качество", choices=QUALITIES, null=True, blank=True
    )
    category = models.ForeignKey(
        BroadcastCategory, verbose_name="Категории", on_delete=models.CASCADE, null=True, blank=True
    )
    allowed_subscriptions = models.ManyToManyField(
        AllowedSubscription, verbose_name="Разрешенные подписки", blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Телеканал"
        verbose_name_plural = "Телеканалы"
        ordering = ("-broadcast_id",)

from django.db import models


class AllowedSubscription(models.Model):
    sub_id = models.CharField(unique=True, max_length=8)    
    description = models.CharField(max_length=512)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "Разрешенная подписка"
        verbose_name_plural = "Разрешенные подписки"

    
class AllowedPeriod(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Разрешенный период"
        verbose_name_plural = "Разрешенные периоды"


class Sponsor(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Спонсор"
        verbose_name_plural = "Спонсоры"


class Category(models.Model):
    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True)
    title_uz = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title_ru

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class BroadcastCategory(models.Model):
    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True)
    title_uz = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title_ru

    class Meta:
        verbose_name = "Категория телеканалов"
        verbose_name_plural = "Категории телеканалов"


class Content(models.Model):
    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True)
    title_uz = models.CharField(max_length=255, blank=True)
    #
    content_id = models.PositiveIntegerField(unique=True)
    episode_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    #
    is_russian = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)
    sponsors = models.ManyToManyField(Sponsor, blank=True)
    allowed_subscriptions = models.ManyToManyField(AllowedSubscription, blank=True)
    #
    duration = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(unique=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Контент"
        verbose_name_plural = "Контенты"


class Broadcast(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    quality = models.CharField(max_length=255, null=True, blank=True)
    broadcast_id = models.PositiveBigIntegerField(unique=True)
    category = models.ForeignKey(BroadcastCategory, on_delete=models.CASCADE, null=True, blank=True)
    allowed_subscriptions = models.ManyToManyField(AllowedSubscription, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Телеканал"
        verbose_name_plural = "Телеканалы"

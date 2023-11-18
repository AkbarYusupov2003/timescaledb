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
        return self.title_ru
    
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


class Content(models.Model):
    title_ru = models.CharField(max_length=255, blank=True)
    title_en = models.CharField(max_length=255, blank=True)
    title_uz = models.CharField(max_length=255, blank=True)
    episode_id = models.PositiveIntegerField(blank=True)
    content_id = models.PositiveIntegerField(blank=True)
    is_russian = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    sponsors = models.ManyToManyField(Sponsor)
    allowed_subscriptions = models.ManyToManyField(AllowedSubscription)
    movie_duration = models.PositiveIntegerField()
    slug = models.SlugField(unique=True)
    year = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        verbose_name = "Контент"
        verbose_name_plural = "Контенты"

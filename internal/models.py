from django.db import models


class AllowedSubscription(models.Model):
    sub_id = models.CharField(max_length=8)    
    description = models.CharField(max_length=512)
    
    def __str__(self):
        return self.sub_id

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

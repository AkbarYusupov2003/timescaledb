from django.contrib import admin

from app import models


admin.site.register(models.Subscription)
admin.site.register(models.Transaction)

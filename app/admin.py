from django.contrib import admin

from app import models


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "subscription_id", "count", "time")


@admin.register(models.Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ("pk", "count", "time")

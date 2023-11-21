from django.contrib import admin

from statistic import models


@admin.register(models.ContentHour)
class ContentHourAdmin(admin.ModelAdmin):
    list_display = ("watched_users_count", "watched_duration")


@admin.register(models.BroadcastHour)
class BroadcastHourAdmin(admin.ModelAdmin):
    list_display = ("watched_users_count", "watched_duration")


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "sub_id", "count", "time")


@admin.register(models.Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ("pk", "count", "time")


@admin.register(models.History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "content_id", "broadcast_id", "episode_id", "ip_address", "device", "time")

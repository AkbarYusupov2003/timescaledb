from django.contrib import admin

from statistic import models


# Content Statistic
@admin.register(models.ContentHour)
class ContentHourAdmin(admin.ModelAdmin):
    list_display = ("content_id", "episode_id", "watched_users_count", "watched_duration", "time")


@admin.register(models.ContentDay)
class ContentDayAdmin(admin.ModelAdmin):
    list_display = ("content_id", "episode_id", "watched_users_count", "watched_duration", "time")


@admin.register(models.ContentMonth)
class ContentMonthAdmin(admin.ModelAdmin):
    list_display = ("content_id", "episode_id", "watched_users_count", "watched_duration", "time")


# Broadcast Statistic
@admin.register(models.BroadcastHour)
class BroadcastHourAdmin(admin.ModelAdmin):
    list_display = ("broadcast_id", "watched_users_count", "watched_duration", "time")


@admin.register(models.BroadcastDay)
class BroadcastDayAdmin(admin.ModelAdmin):
    list_display = ("broadcast_id", "watched_users_count", "watched_duration", "time")


@admin.register(models.BroadcastMonth)
class BroadcastMonthAdmin(admin.ModelAdmin):
    list_display = ("broadcast_id", "watched_users_count", "watched_duration", "time")


# -------------------------------------------------------------------------------------------------
@admin.register(models.History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "content_id", "broadcast_id", "episode_id", "ip_address", "device", "time")


@admin.register(models.Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ("pk", "count", "time")


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "sub_id", "count", "time")


@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("status", "section", "lines_count", "created_at")

from django.contrib import admin

from statistic import models


class AgeGroupAdmin(admin.ModelAdmin):
    
    @admin.display(description="Возрастная группа")
    def age_group_display(self, obj):
        return obj.get_age_group_display()


# Content Statistic
@admin.register(models.ContentHour)
class ContentHourAdmin(AgeGroupAdmin):
    list_display = ("content_id", "episode_id", "sid", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


@admin.register(models.ContentDay)
class ContentDayAdmin(AgeGroupAdmin):
    list_display = ("content_id", "episode_id", "sid", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


@admin.register(models.ContentMonth)
class ContentMonthAdmin(AgeGroupAdmin):
    list_display = ("content_id", "episode_id", "sid", "watched_users_count", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


# Broadcast Statistic
@admin.register(models.BroadcastHour)
class BroadcastHourAdmin(AgeGroupAdmin):
    list_display = ("broadcast_id", "sid", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


@admin.register(models.BroadcastDay)
class BroadcastDayAdmin(AgeGroupAdmin):
    list_display = ("broadcast_id", "sid", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


@admin.register(models.BroadcastMonth)
class BroadcastMonthAdmin(AgeGroupAdmin):
    list_display = ("broadcast_id", "sid", "watched_users_count", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


# -------------------------------------------------------------------------------------------------
@admin.register(models.History)
class HistoryAdmin(AgeGroupAdmin):
    list_display = ("slug", "content_id", "broadcast_id", "episode_id", "sid", "age_group", "gender", "time")
    list_filter = ("time",)


@admin.register(models.Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ("pk", "count", "time")
    list_filter = ("time",)


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "sub_id", "count", "time")
    list_filter = ("time",)


@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("status", "group", "rows_count", "created_at")
    list_filter = ("created_at",)

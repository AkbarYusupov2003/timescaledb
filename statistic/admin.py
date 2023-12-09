from django.contrib import admin

from statistic import models


@admin.register(models.History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "content_id", "broadcast_id", "episode_id", "sid", "age_group", "gender", "time")
    list_filter = ("time",)


# -------------------------------------------------------------------------------------------------
@admin.register(models.RegisterHour)
class RegisterHourAdmin(admin.ModelAdmin):
    list_display = ("pk", "count", "time")
    list_filter = ("time",)


@admin.register(models.RegisterDay)
class RegisterDayAdmin(admin.ModelAdmin):
    list_display = ("pk", "count", "time")
    list_filter = ("time",)


@admin.register(models.SubscriptionHour)
class SubscriptionHourAdmin(admin.ModelAdmin):
    list_display = ("pk", "sub_id", "count", "time")
    list_filter = ("time",)


@admin.register(models.SubscriptionDay)
class SubscriptionDayAdmin(admin.ModelAdmin):
    list_display = ("pk", "sub_id", "count", "time")
    list_filter = ("time",)


# -------------------------------------------------------------------------------------------------
@admin.register(models.DeviceVisitsHour)
class DeviceVisitHourAdmin(admin.ModelAdmin):
    list_display = ("time", "app_type", "device_type", "os_type", "country", "count")


@admin.register(models.DeviceVisitsDay)
class DeviceVisitDayAdmin(admin.ModelAdmin):
    list_display = ("time", "app_type", "device_type", "os_type", "country", "count")


@admin.register(models.DeviceVisitsMonth)
class DeviceVisitMonthAdmin(admin.ModelAdmin):
    list_display = ("time", "app_type", "device_type", "os_type", "country", "count")


# Content Statistic
@admin.register(models.ContentHour)
class ContentHourAdmin(admin.ModelAdmin):
    list_display = ("content_id", "episode_id", "sid", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


@admin.register(models.ContentDay)
class ContentDayAdmin(admin.ModelAdmin):
    list_display = ("content_id", "episode_id", "sid", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


@admin.register(models.ContentMonth)
class ContentMonthAdmin(admin.ModelAdmin):
    list_display = ("content_id", "episode_id", "sid", "watched_users_count", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


# Broadcast Statistic
@admin.register(models.BroadcastHour)
class BroadcastHourAdmin(admin.ModelAdmin):
    list_display = ("broadcast_id", "sid", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


@admin.register(models.BroadcastDay)
class BroadcastDayAdmin(admin.ModelAdmin):
    list_display = ("broadcast_id", "sid", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


@admin.register(models.BroadcastMonth)
class BroadcastMonthAdmin(admin.ModelAdmin):
    list_display = ("broadcast_id", "sid", "watched_users_count", "watched_duration", "age_group", "gender", "time")
    list_filter = ("time",)


# -------------------------------------------------------------------------------------------------
@admin.register(models.AdsView)
class AdsViewAdmin(admin.ModelAdmin):
    list_display = ("time",)


# -------------------------------------------------------------------------------------------------
@admin.register(models.CategoryViewHour)
class ViewCategoryHour(admin.ModelAdmin):    
    list_display = ("category_id", "watched_users_count", "age_group", "gender", "time")
    list_filter = ("category_id", )


@admin.register(models.CategoryViewDay)
class ViewCategoryDay(admin.ModelAdmin):    
    list_display = ("category_id", "watched_users_count", "age_group", "gender", "time")
    list_filter = ("category_id", )


@admin.register(models.CategoryViewMonth)
class ViewCategoryMonth(admin.ModelAdmin):    
    list_display = ("category_id", "watched_users_count", "age_group", "gender", "time")
    list_filter = ("category_id", )


# -------------------------------------------------------------------------------------------------
@admin.register(models.DailyTotalViews)
class DailyTotalViewsAdmin(admin.ModelAdmin):
    list_display = ("age_group", "gender", "total_views", "time")
    list_filter = ("age_group", "gender")


@admin.register(models.DailyContentViews)
class DailyContentViewsAdmin(admin.ModelAdmin):
    list_display = ("content_id", "episode_id", "category_id", "age_group", "gender", "total_views", "time")
    list_filter = ("category_id", "age_group", "gender")


# -------------------------------------------------------------------------------------------------
@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("section",  "status", "created_at")
    list_filter = ("created_at",)

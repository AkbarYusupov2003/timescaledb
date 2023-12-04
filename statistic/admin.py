from django.contrib import admin

from statistic import models


@admin.register(models.History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "content_id", "broadcast_id", "episode_id", "sid", "age_group", "gender", "time")
    list_filter = ("time",)


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
@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("section",  "status", "created_at")
    list_filter = ("created_at",)


# -------------------------------------------------------------------------------------------------
@admin.register(models.Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ("pk", "count", "time")
    list_filter = ("time",)


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "sub_id", "count", "time")
    list_filter = ("time",)

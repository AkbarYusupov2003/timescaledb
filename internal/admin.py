from django.contrib import admin

from internal import models


@admin.register(models.AllowedSubscription)
class AllowedSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "title_ru")


@admin.register(models.AllowedPeriod)
class AllowedPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", )


@admin.register(models.Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ("name", "is_chosen")


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name_ru", "ordering")


@admin.register(models.BroadcastCategory)
class BroadcastCategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name_ru", )


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("pk", "title_ru", "content_id", "episode_id", "slug", "is_russian")
    filter_horizontal = ("sponsors", "allowed_subscriptions")


@admin.register(models.Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "broadcast_id")

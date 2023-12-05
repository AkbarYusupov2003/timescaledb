from django.http.request import HttpRequest
from django.urls import path
from django.contrib import admin
from django.http import HttpResponseRedirect

from statistic import tasks
from internal import models


@admin.register(models.AllowedSubscription)
class AllowedSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "title_ru")
    search_fields = ("title_ru", )


@admin.register(models.Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ("name", "is_chosen")
    list_filter = ("is_chosen",)
    search_fields = ("name",)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name_ru", "ordering")
    search_fields = ("name",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.BroadcastCategory)
class BroadcastCategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name_ru",)
    search_fields = ("name_ru",)


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("pk", "title_ru", "content_id", "episode_id", "slug", "is_russian")
    list_filter = ("is_russian", "category", "allowed_subscriptions")
    search_fields = ("title_ru",)
    autocomplete_fields = ("category", "sponsors", "allowed_subscriptions")
    change_list_template = "update_list.html"

    def get_urls(self):
        return [path('full-update/', self.full_update)] + super().get_urls()

    def full_update(self, request):   
        tasks.daily_content_update_task.delay(update_relations=True)
        self.message_user(request, "Создана задача для обновления контента")
        return HttpResponseRedirect("../")


@admin.register(models.Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ("broadcast_id", "title", "quality")
    list_filter = ("category", "quality", "allowed_subscriptions")
    search_fields = ("title",)
    autocomplete_fields = ("category", "allowed_subscriptions")
    change_list_template = "update_list.html"

    def get_urls(self):
        return [path('full-update/', self.full_update)] + super().get_urls()

    def full_update(self, request):
        tasks.daily_broadcast_update_task.delay(update_relations=True)
        self.message_user(request, "Создана задача для обновления телеканалов")
        return HttpResponseRedirect("../")

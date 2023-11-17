from django.contrib import admin

from internal import models


@admin.register(models.AllowedSubscription)
class AllowedSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("sub_id", "description")


@admin.register(models.AllowedPeriod)
class AllowedPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", )
    
    # def has_add_permission(self, request):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False
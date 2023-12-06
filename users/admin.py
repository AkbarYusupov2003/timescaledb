from django.contrib import admin
from users import models


@admin.register(models.MultiToken)
class MultiTokenAdmin(admin.ModelAdmin):
    pass

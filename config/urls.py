from django.contrib import admin
from django.urls import path, include

from config.yasg import urlpatterns as yasg_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("api.urls", namespace="api")),
]

urlpatterns += yasg_urls

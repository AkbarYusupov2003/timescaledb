from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from config.yasg import urlpatterns as yasg_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("api.urls", namespace="api")),
]

urlpatterns.extend(yasg_urls)

if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))

from rest_framework.authtoken.models import Token
from django.db import models
from django.conf import settings


class MultiToken(Token):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='tokens',
        on_delete=models.CASCADE, verbose_name="User"
    )
    my_key = models.CharField("Демо Токен", max_length=50, unique=True)

    os_info = models.CharField("OS Info", max_length=255, null=True, blank=True)
    device_info = models.CharField("Device Info", max_length=255, null=True, blank=True)
    browser_info = models.CharField("Browser Info", max_length=255, null=True, blank=True)

    jti = models.CharField("JWT ID", max_length=512, blank=True, null=True)
    ua_name = models.CharField("User-Agent name", max_length=255, blank=True, null=True)
    ua_model_name = models.CharField("User-Agent model name", max_length=255, blank=True, null=True)
    ua_os_name = models.CharField("User-Agent os name", max_length=255, blank=True, null=True)
    ua_os_version = models.CharField("User-Agent os version", max_length=255, blank=True, null=True)
    ua_browser_name = models.CharField("User-Agent browser name", max_length=255, blank=True, null=True)
    ua_browser_version = models.CharField("User-Agent browser version", max_length=255, blank=True, null=True)
    ua_device_type = models.CharField("User-Agent device type", max_length=255, blank=True, null=True)
    ua_app_type = models.CharField("User-Agent App type", max_length=255, blank=True, null=True)
    ua_c_code = models.CharField("User-Agent Country Code", max_length=255, blank=True, null=True)

    user_agent = models.CharField("User Agent", max_length=1024, null=True, blank=True)
    cuser_agent = models.CharField("CUser Agent", max_length=1024, null=True, blank=True)

    is_active = models.BooleanField(default=False)
    updated = models.DateTimeField("Updated", auto_now=True)
    ip_address = models.GenericIPAddressField('IP', blank=True, null=True)
    
    class Meta:
        db_table = "users_multitoken"
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

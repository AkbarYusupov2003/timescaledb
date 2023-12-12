from django.conf import settings
from rest_framework import permissions


# class SecretKeyPermission(permissions.BasePermission):
#     def has_permission(self, request, view):
#         api_key = request.META.get('HTTP_API_KEY') # API-KEY -> HTTP_API_KEY
#         if settings.SPLAY_STAT_SECRET_KEY == api_key:
#             return True
#         return False

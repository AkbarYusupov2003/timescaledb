from rest_framework import serializers

from app import models


class RegisterSerializer(serializers.Serializer):
    time = serializers.SerializerMethodField(source="get_time")
    count = serializers.SerializerMethodField(source="get_count")
    
    def get_time(self, obj):
        return obj[0]
    
    def get_count(self, obj):
        return obj[1]


class SubscriptionSerializer(serializers.Serializer):
    time = serializers.SerializerMethodField(source="get_time")
    count = serializers.SerializerMethodField(source="get_count")
    
    def get_time(self, obj):
        return obj[0]
    
    def get_count(self, obj):
        return obj[1]

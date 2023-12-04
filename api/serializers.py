from rest_framework import serializers

from internal import models as internal_models
from statistic import models


# Internal
class SponsorSerializer(serializers.ModelSerializer):

    class Meta:
        model = internal_models.Sponsor
        fields = ("id", "name")


class AllowedSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = internal_models.AllowedSubscription
        fields = ("id", "title_ru")


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = internal_models.Category
        fields = ("id", "name_ru")


class BroadcastCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = internal_models.BroadcastCategory
        fields = ("id", "name_ru")
# Internal ended


class ContentSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    sponsors = SponsorSerializer(many=True)
    allowed_subscriptions = AllowedSubscriptionSerializer(many=True)

    class Meta:
        model = internal_models.Content
        fields = (
            "title_ru", "content_id", "episode_id", "is_russian", "category", 
            "sponsors", "allowed_subscriptions", "duration", "slug", "year"
        )


class BroadcastSerializer(serializers.ModelSerializer):
    category = BroadcastCategorySerializer()
    
    class Meta:
        model = internal_models.Broadcast
        fields = ("broadcast_id", "title", "quality", "category")


# ------------------------------------------------------------------------------------
class PerformingReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Report
        fields = ("id", "section", "progress")


class PerformedReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Report
        fields = ("id", "section", "file", "additional_data", "is_downloaded", "created_at")


# ------------------------------------------------------------------------------------
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

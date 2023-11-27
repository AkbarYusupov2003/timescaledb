from rest_framework import serializers

from internal import models


# Internal
class SponsorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Sponsor
        fields = ("id", "title")


class AllowedSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AllowedSubscription
        fields = ("sub_id", "title")


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = ("id", "name_ru")


class BroadcastCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BroadcastCategory
        fields = ("id", "title_ru")
# Internal ended


class ContentSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    sponsors = SponsorSerializer(many=True)
    allowed_subscriptions = AllowedSubscriptionSerializer(many=True)

    class Meta:
        model = models.Content
        fields = (
            "title_ru", "content_id", "episode_id", "is_russian", "category", 
            "sponsors", "allowed_subscriptions", "duration", "slug", "year"
        )


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

from rest_framework import serializers

from internal.models import Content, Category, Sponsor, AllowedSubscription


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ("title_ru",)


class SponsorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Sponsor
        fields = ("title",)


class AllowedSubscriptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AllowedSubscription
        fields = ("sub_id", )
    

class ContentSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    sponsors = SponsorSerializer(many=True)
    allowed_subscriptions = AllowedSubscriptionSerializer(many=True)
    
    class Meta:
        model = Content
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

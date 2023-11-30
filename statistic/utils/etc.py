from statistic.utils import data_extractor, validators
from internal import models


def is_content_exists_or_create(data, slug):
    try:
        models.Content.objects.get(**data)
        return True
    except models.Content.DoesNotExist:
        response = data_extractor.get_data(
            data_extractor.CONTENT_DATA_URL,
            params={"id_slugs": slug}
        )
        result = response.get("results").get(slug)
        if result:
            result["content_id"] = data.get("content_id")
            result["episode_id"] = data.get("episode_id")
            result["slug"] = slug
            allowed_subscriptions = result.pop("allowed_subscriptions", [])
            sponsors = result.pop("sponsors", [])
            if validators.is_category_valid(result.get("category_id")):
                result["category_id"] = result.get("category_id")
            else:
                result["category_id"] = None
            content = models.Content.objects.create(**result)
            if allowed_subscriptions:
                content.allowed_subscriptions.set(validators.validate_subscriptions(allowed_subscriptions))    
            if sponsors:
                content.sponsors.set(validators.validate_sponsors(sponsors))
            content.save()
            return True
        else:
            return False


def is_broadcast_exists_or_create(broadcast_id):
    try:
        models.Broadcast.objects.get(broadcast_id=broadcast_id)
        return True
    except models.Broadcast.DoesNotExist:
        response = data_extractor.get_data(
            data_extractor.BROADCAST_DETAIL_URL.format(broadcast_id),
            params={"id_slugs": broadcast_id}
        )
        tv_id = response.get("tv_id")
        title = response.get("title")
        quality = response.get("quality")
        category_id = response.get("category")
        allowed_subscriptions = response.get("allowed_subscriptions")
        if tv_id and title:
            data = {"broadcast_id": tv_id, "title": title, "quality": quality}
            if validators.is_broadcast_category_valid(category_id):
                data["category_id"] = category_id
            broadcast = models.Broadcast.objects.create(**data)
            if allowed_subscriptions:
                broadcast.allowed_subscriptions.set(validators.validate_subscriptions(allowed_subscriptions))            
                broadcast.save()
            return True
        else:
            return False

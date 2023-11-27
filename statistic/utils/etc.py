from statistic.utils import data_extractor
from internal import models


def is_category_valid(pk):
    try:
        models.Category.objects.get(pk=pk)
        return True
    except:
        return False


def validate_subscriptions(pks):
    existing_pks = list(models.AllowedSubscription.objects.filter(pk__in=pks).values_list("pk", flat=True))
    return set(existing_pks).intersection(pks)


def validate_sponsors(pks):
    existing_pks = list(models.Sponsor.objects.filter(pk__in=pks).values_list("pk", flat=True))
    return set(existing_pks).intersection(pks)


def exists_or_create(data, slug): # TODO
    instance = models.Content.objects.filter(**data).first()
    if instance:
        return True
    else:
        response = data_extractor.get_data(
            data_extractor.CONTENT_DATA_URL,
            params={"id_slugs": slug}
        )
        results = response.get("results").get(slug)
        if results:
            results["content_id"] = data.get("content_id")
            results["episode_id"] = data.get("episode_id")
            results["slug"] = slug
            results["category"] = models.Category.objects.get(pk=results.pop("category_id")) # validate category
            models.Content.objects.create(**results)
            return True
        else:
            return False



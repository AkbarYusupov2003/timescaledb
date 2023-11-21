from statistic.utils import data_extractor
from internal.models import Content, Category


def exists_or_create(data, slug):
    instance = Content.objects.filter(**data).first()
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
            results["category"] = Category.objects.get(pk=results.pop("category_id"))
            Content.objects.create(**results)
            return True
        else:
            return False

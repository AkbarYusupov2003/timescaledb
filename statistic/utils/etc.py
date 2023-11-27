from statistic.utils import data_extractor
from internal import models


# def validate_category(pk):
#     pass


# def validate_sponsors(sponsor_pks):
#     res = []
#     existing_pks = list(models.Sponsor.objects.filter(pk__in=sponsor_pks).values_list("pk", flat=True))
#     diff = list(set(sponsor_pks) - set(existing_pks))
#     print("diff", diff)
    
#     data = data_extractor.get_data(
#         data_extractor.SPONSORS_URL, {"ids": diff}
#     ).get("results")
#     if data:
#         models.Sponsor.objects.bulk_create(
#             [
#                 models.Sponsor(
#                     pk=s["id"], title=s["name"]
#                 ) for s in data 
#             ]
#         )
#     return res


# def validate_subscriptions(sub_pks):
#     pass


def exists_or_create(data, slug):
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



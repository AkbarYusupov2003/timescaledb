from internal import models


def is_category_valid(pk):
    try:
        models.Category.objects.get(pk=pk)
        return True
    except models.Category.DoesNotExist:
        return False


def is_broadcast_category_valid(pk):
    try:
        models.BroadcastCategory.objects.get(pk=pk)
        return True
    except models.BroadcastCategory.DoesNotExist:
        return False


def validate_subscriptions(pks):
    existing_pks = list(models.AllowedSubscription.objects.filter(pk__in=pks).values_list("pk", flat=True))
    return set(existing_pks).intersection(pks)


def validate_sponsors(pks):
    existing_pks = list(models.Sponsor.objects.filter(pk__in=pks).values_list("pk", flat=True))
    return set(existing_pks).intersection(pks)

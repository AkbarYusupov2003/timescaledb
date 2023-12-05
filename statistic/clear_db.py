from statistic import models


clear = [
    # models.History,
    models.Register, models.Subscription,
    models.ContentHour, models.ContentDay, models.ContentMonth,
    models.BroadcastHour, models.BroadcastDay, models.BroadcastMonth,
    models.CategoryViewHour, models.CategoryViewDay, models.CategoryViewMonth,
    # models.DailyTotalViews, models.DailyContentViews,
    models.Report
]

def main():
    for model in clear:
        model.objects.all().delete()

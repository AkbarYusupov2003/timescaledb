from django.urls import path

from api import views


app_name = "api"

urlpatterns = [
    # Internal
    path("sponsor-list/", views.SponsorListAPIView.as_view()), # DONE
    path("subscription-list/", views.SubscriptionListAPIView.as_view()), # DONE
    path("category-list/", views.CategoryListAPIView.as_view()), # DONE
    path("broadcast-category-list/", views.BroadcastCategoryListAPIView.as_view()), # DONE
    # Internal ended
    path("create-history/", views.CreateHistoryAPIView.as_view()), # TODO
    #
    path("content-stat/", views.ContentStatAPIView.as_view()),
    # path("broadcast-stat/", views.BroadcastListAPIView.as_view()),
    #
    path("register-stat/", views.RegisterStatAPIView.as_view()), # DONE
    path("register-stat/total/", views.RegisterTotalStatAPIView.as_view()), # DONE
    #
    path("subscriptions-stat/", views.SubscriptionStatAPIView.as_view()), # DONE
    path("subscriptions-stat/total/", views.SubscriptionTotalStatAPIView.as_view()), # DONE
    #
    # path("report/create/", views.ReportCreateView.as_view()),
]

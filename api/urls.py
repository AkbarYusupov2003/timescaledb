from django.urls import path

from api import views


app_name = "api"

urlpatterns = [
    # Internal
    path("internal/sponsor-list/", views.SponsorListAPIView.as_view()),
    path("internal/allowed-subscription-list/", views.AllowedSubscriptionListAPIView.as_view()),
    path("internal/category-list/", views.CategoryListAPIView.as_view()),
    path("internal/broadcast-category-list/", views.BroadcastCategoryListAPIView.as_view()),
    # Internal ended
    path("create-history/", views.CreateHistoryAPIView.as_view()), # TODO
    #
    path("content-stat/", views.ContentStatAPIView.as_view()),
    path("content-stat/<slug:slug>/", views.ContentStatDetailAPIView.as_view()),
    path("broadcast-stat/", views.BroadcastStatAPIView.as_view()), # TODO
    path("broadcast-stat/<int:pk>/", views.BroadcastStatDetailAPIView.as_view()),
    #
    path("register-stat/", views.RegisterStatAPIView.as_view()),
    path("register-stat/total/", views.RegisterTotalStatAPIView.as_view()),
    #
    path("subscriptions-stat/", views.SubscriptionStatAPIView.as_view()),
    path("subscriptions-stat/total/", views.SubscriptionTotalStatAPIView.as_view()),
    #
    path("report/create/", views.ReportCreateView.as_view()),
]

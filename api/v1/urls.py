from django.urls import path

from api.v1 import views


app_name = "api.v1"

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
    #
    path("broadcast-stat/", views.BroadcastStatAPIView.as_view()),
    path("broadcast-stat/<int:pk>/", views.BroadcastStatDetailAPIView.as_view()),
    #
    path("category-views/", views.CategoryViewsStatAPIView.as_view()),
    #
    # _____________________________________________________________________________________
    path("register-stat/", views.RegisterStatAPIView.as_view()),  # HERE
    path("register-stat/total/", views.RegisterTotalStatAPIView.as_view()),
    #
    path("subscription-stat/", views.SubscriptionStatAPIView.as_view()),
    path("subscription-stat/total/", views.SubscriptionTotalStatAPIView.as_view()),
    #
    path("report/performing/", views.PerformingReportAPIView.as_view()),
    path("report/performed/", views.PerformedReportAPIView.as_view()),
    path("report/<int:pk>/downloaded/", views.ReportDownloadedAPIView.as_view()),
    #
    path("most-viewed-content/", views.MostViewedContentAPIView.as_view()),
]

from django.urls import path

from api import views


app_name = "api"

urlpatterns = [ 
    path("update-history/", views.UpdateHistoryAPIView.as_view()),
    #
    path('content-stat/', views.ContentListAPIView.as_view()),
    #
    path("register-stat/", views.RegisterListAPIView.as_view()),
    path("register-stat/total/", views.RegisterTotalAPIView.as_view()),
    #
    path("subscriptions-stat/", views.SubscriptionListAPIView.as_view()),
    path("subscriptions-stat/total/", views.SubscriptionTotalAPIView.as_view()),
    #
    path("load-daily-register/", views.LoadDailyRegisterView.as_view()),
    #
]

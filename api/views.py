import json
import datetime
from django.views import View
from django.db import connection
from django.db.models import Sum
from django.shortcuts import render, HttpResponse
from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from api import serializers
from statistic import models
from internal.models import AllowedSubscription, AllowedPeriod


# http://127.0.0.1:8000/subscriptions-stat/?period=day&from_date=2023-12-16+00:00:00.000Z&to_date=2023-12-17+00:00:00.000Z&sub_type=1

# TODO доделать
class UpdateHistoryAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        content_id = int(request.data.get('content_id', 0))
        broadcast_id = int(request.data.get('broadcast_id', 0))
        episode_id = int(request.data.get('episode_id', 0))
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ipaddress = x_forwarded_for.split(',')[-1].strip()
        else:
            ipaddress = request.META.get('REMOTE_ADDR')

        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        
        
        return HttpResponse("Ok")


# Content
class ContentListAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        # get list of content
        return Response({"worked": "yes"},status=200)

# Register
class RegisterListAPIView(APIView):
    serializer_class = serializers.RegisterSerializer
    
    def get_queryset(self):
        from_date = self.request.GET.get("from_date")
        to_date = self.request.GET.get("to_date")
        period = self.request.GET.get("period")
        # validation
        allowed_periods = ["hour", "day", "month"]
        
        if not(period in allowed_periods):
            return []
        
        try:
            date_format = "%Y-%m-%d %H:%M:%S.%fZ"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format)
        except:
            return []
        # -----------
        cursor = connection.cursor()
        cursor.execute(
            f"""
                SELECT time_bucket('1 {period}', time) AS interval, SUM(count)
                FROM statistic_register
                WHERE (time BETWEEN '{from_date}' AND '{to_date}')
                GROUP BY interval
                ORDER BY interval DESC;
            """
        )
        return cursor.fetchall()
        
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        res = self.serializer_class(queryset, many=True)
        return Response(res.data, status=200)


class RegisterTotalAPIView(APIView):

    def get_queryset(self):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        cursor = connection.cursor()
        cursor.execute(
            f"""
                SELECT time_bucket('1 day', time) AS interval, SUM(count)
                FROM statistic_register
                WHERE (time BETWEEN '{today}' AND '{tomorrow}' )
                GROUP BY interval
                ORDER BY interval DESC;
            """
        )
        return cursor.fetchone()

    def get(self, request, *args, **kwargs):
        total = models.Register.objects.all().aggregate(Sum("count"))["count__sum"]
        today = self.get_queryset()
        res = {"total": total if total else 0, "today": today[1] if today else 0}
        return Response(res, status=200)


# Subscriptions
class SubscriptionListAPIView(APIView):
    serializer_class = serializers.SubscriptionSerializer

    def get_queryset(self):
        from_date = self.request.GET.get("from_date")
        to_date = self.request.GET.get("to_date")
        period = self.request.GET.get("period")
        sub_type = self.request.GET.get("sub_type")
        
        # allowed_periods = ["hour", "day", "month"]
        # allowed_subs = ["1", "2"]
        allowed_periods = AllowedPeriod.objects.all().values_list("name", flat=True)
        allowed_subs = AllowedSubscription.objects.all().values_list("sub_id", flat=True)

        if not(period in allowed_periods):
            return []
        
        if sub_type and not(sub_type in allowed_subs):
            return []
        
        try:
            date_format = "%Y-%m-%d %H:%M:%S.%fZ"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format)
        except:
            return []
        # -----------
        
        cursor = connection.cursor()
        cursor.execute(
            f"""
                SELECT time_bucket('1 {period}', time) AS interval, SUM(count)
                FROM statistic_subscription
                WHERE (time BETWEEN '{from_date}' AND '{to_date}') AND (subscription_id = {sub_type})
                GROUP BY interval
                ORDER BY interval DESC;
            """
        )
        return cursor.fetchall()
        

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        res = self.serializer_class(queryset, many=True)
        return Response(res.data, status=200)


class SubscriptionTotalAPIView(APIView):
    def get_queryset(self):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        cursor = connection.cursor()
        cursor.execute(
            f"""
                SELECT time_bucket('1 day', time) AS interval, SUM(count)
                FROM statistic_subscription
                WHERE (time BETWEEN '{today}' AND '{tomorrow}' )
                GROUP BY interval
                ORDER BY interval DESC;
            """
        )
        return cursor.fetchone()
    
    def get(self, request, *args, **kwargs):
        total = models.Subscription.objects.all().aggregate(Sum("count"))["count__sum"]
        today = self.get_queryset()
        res = {"total": total if total else 0, "today": today[1] if today else 0}
        return Response(res, status=200)


# Load data to db
# class LoadDailyRegisterView(View):
#     SIGNUP_URL = "https://api.splay.uz/en/api/v2/sevimlistat/account_registration/"
    
#     def get(self, *args, **kwargs):
#         period = "hours" # ["hours", "days", "months"]
#         data = utils.get_splay_data(self.SIGNUP_URL, params={'period': period})
#         print("DATA: ", data)
#         return HttpResponse("loaded daily register data")

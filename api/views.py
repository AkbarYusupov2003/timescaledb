import json
import datetime
from django.views import View
from django.db import connection
from django.db.models import Sum
from django.shortcuts import HttpResponse
from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from api import serializers
from statistic import models
from internal.models import AllowedSubscription, AllowedPeriod, Content


# http://127.0.0.1:8000/subscriptions-stat/?period=day&from_date=2023-12-16+00:00:00.000Z&to_date=2023-12-17+00:00:00.000Z&sub_type=1

# TODO доделать
class CreateHistoryAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            content_id = int(request.data.get('content_id', 0))
            broadcast_id = int(request.data.get('broadcast_id', 0))
            episode_id = int(request.data.get('episode_id', 0))
        except:
            return Response(status=400)
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[-1].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        user_agent = request.META.get('HTTP_USER_AGENT', '')
        device = "device" # self.request.auth.payload.get("device", "not available")
        data = {"ip_address": ip_address, "user_agent": user_agent, "device": device, "time": datetime.datetime.now()}
        if content_id:
            data["content_id"] = content_id
            if episode_id:
                data["episode_id"] = episode_id
        elif broadcast_id:
            data["broadcast_id"] = broadcast_id
        else:
            return Response(status=400)
            
        models.History.objects.create(**data)
        return Response("Ok")


# Content
class ContentListAPIView(generics.GenericAPIView):
    queryset = Content.objects.all()
    serializer_class = serializers.ContentSerializer
    pagination_class = LimitOffsetPagination
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        res = []
        for content in queryset:
            stats = models.History.objects.filter(
                content_id=content.content_id, 
                episode_id=content.episode_id,
            )
            content = self.serializer_class(content).data
            content["watched_users"] = stats.count()
            content["watched_duration"] = stats.aggregate(Sum("duration"))["duration__sum"] or 0
            res.append(content)

        return Response(res, status=200)


# Register
class RegisterListAPIView(APIView):
    serializer_class = serializers.RegisterSerializer
    
    def get_queryset(self):
        from_date = self.request.GET.get("from_date")
        to_date = self.request.GET.get("to_date")
        period = self.request.GET.get("period")
        # validation
        allowed_periods = AllowedPeriod.objects.all().values_list("name", flat=True)
        
        if not(period in allowed_periods):
            return []
        
        try:
            date_format = "%Y-%m-%d"
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
        sub_id = self.request.GET.get("sub_id")
        # validation
        allowed_periods = AllowedPeriod.objects.all().values_list("name", flat=True)
        allowed_subs = AllowedSubscription.objects.all().values_list("sub_id", flat=True)

        if not(period in allowed_periods):
            return []
        
        if sub_id and not(sub_id in allowed_subs):
            return []
        
        try:
            date_format = "%Y-%m-%d"
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
                WHERE (time BETWEEN '{from_date}' AND '{to_date}') AND (sub_id = '{sub_id}')
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

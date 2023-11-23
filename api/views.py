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
from api import utils
from statistic import models
from internal.models import AllowedSubscription, AllowedPeriod, Category, Content


# Content: http://127.0.0.1:8000/content-stat/?period=day&from_date=2023-11-22-0:00&to_date=2023-11-30-00:00
# Subscription: http://127.0.0.1:8000/subscriptions-stat/?period=day&from_date=2022-12-16&to_date=2023-12-17&sub_id=1
# Register: http://127.0.0.1:8000/register-stat/?period=day&from_date=2022-12-16&to_date=2023-12-17


# class CreateHistoryAPIView(APIView):
    
    # def post(self, request, *args, **kwargs):
    #     try:
    #         content_id = int(request.data.get('content_id', 0))
    #         broadcast_id = int(request.data.get('broadcast_id', 0))
    #         episode_id = int(request.data.get('episode_id', 0))
    #     except:
    #         return Response(status=400)
        
    #     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    #     if x_forwarded_for:
    #         ip_address = x_forwarded_for.split(',')[-1].strip()
    #     else:
    #         ip_address = request.META.get('REMOTE_ADDR')

    #     user_agent = request.META.get('HTTP_USER_AGENT', '')
    #     device = "device" # self.request.auth.payload.get("device", "not available")
    #     data = {"ip_address": ip_address, "user_agent": user_agent, "device": device, "time": datetime.datetime.now()}
    #     if content_id:
    #         data["content_id"] = content_id
    #         if episode_id:
    #             data["episode_id"] = episode_id
    #     elif broadcast_id:
    #         data["broadcast_id"] = broadcast_id
    #     else:
    #         return Response(status=400)
            
    #     models.History.objects.create(**data)
    #     return Response("Ok")


class CreateHistoryAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        print("create history")
        try:
            content_id = int(request.data.get('content_id', 0))
            broadcast_id = int(request.data.get('broadcast_id', 0))
            episode_id = int(request.data.get('episode_id', 0))
            gender = "M" # self.request.auth.payload.get("gender")
            age = utils.get_group_by_age(19) # self.request.auth.payload.get("age")
        except Exception as e:
            return Response({"Error": e}, status=400)

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[-1].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        user_agent = request.META.get('HTTP_USER_AGENT', '')

        device = "device" # self.request.auth.payload.get("device")
        data = {
            "ip_address": ip_address, "user_agent": user_agent, "device": device, 
            "time": datetime.datetime.now(), "gender": gender, "age_group": age
        }
        if content_id:
            data["content_id"] = content_id
            if episode_id:
                data["episode_id"] = episode_id
                data["slug"] = f"{content_id}_{episode_id}"
            else:
                data["slug"] = f"{content_id}_null"
        elif broadcast_id:
            data["broadcast_id"] = broadcast_id
            data["slug"] = str(broadcast_id)
        else:
            return Response({"error": "id validation"}, status=400)
        print("data: ", data)
        models.History.objects.create(**data)
        print("create history ended")
        return Response("Ok")


# Content
class ContentListAPIView(generics.GenericAPIView):
    queryset = Content.objects.all().select_related(
        "category"
    ).prefetch_related("sponsors", "allowed_subscriptions")
    serializer_class = serializers.ContentSerializer
    pagination_class = LimitOffsetPagination
    
    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get("from_date")
        to_date = self.request.GET.get("to_date")
        period = self.request.GET.get("period")
        sub_id = self.request.GET.get("sub_id")
        sponsors = self.request.GET.get("sponsors", "")
        category = self.request.GET.get("category")
        is_russian = self.request.GET.get("is_russian")
        ordering = self.request.GET.get("ordering")
        # ------------------------------------------------------------------------------------------
        allowed_periods = AllowedPeriod.objects.all().values_list("name", flat=True)
        allowed_subscriptions = AllowedSubscription.objects.all().values_list("sub_id", flat=True)
        allowed_orderings = ("watched_users", "watched_duration", "content_duration", "id", "title")
        qs_filter = {}

        try:
            limit = int(request.GET.get("limit", 20))
            offset = int(request.GET.get("offset", 0))
        except:
            return Response({"error": "limit, offset validation"}, status=400)
        
        if not(period in allowed_periods):
            return Response({"error": "period validation"}, status=400)

        if sub_id:
            if sub_id in allowed_subscriptions:
                qs_filter["allowed_subscriptions__in"] = (sub_id,)
            else:
                return Response({"error": "sub_id validation"}, status=400)

        if sponsors.isnumeric():
            qs_filter["sponsors__in"] = (sponsors,)

        if category.isnumeric():
            qs_filter["category__pk"] = category

        if is_russian == "True":
            qs_filter["is_russian"] = True
        elif is_russian == "False":
            qs_filter["is_russian"] = False

        if ordering:
            if not(ordering in allowed_orderings):
                return Response({"error": "ordering validation"}, status=400)

        try:
            date_format = "%Y-%m-%d-%H:%M"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format)
            if period == "hours":
                table_name = "statistic_content_hour"
            elif period == "day":
                table_name = "statistic_content_day"
            elif period == "month":
                table_name = "statistic_content_month"
            else:
                return Response({"error": "period validation"}, status=400)
        except Exception as e:
            return Response({"error": e}, status=400)

        queryset = self.queryset.filter(**qs_filter)
        if not qs_filter:
            # paginate
            queryset = queryset[offset:limit+offset]

        res = []

        for content in queryset:
            cursor = connection.cursor()
            cursor.execute(
                f"""
                    SELECT time_bucket('1 {period}', time) AS interval, watched_users_count, watched_duration, age_group::json, gender::json
                    FROM {table_name}
                    WHERE (time BETWEEN '{from_date}' AND '{to_date}') AND
                          (content_id = '{content.content_id}')
                          {f"AND (episode_id = '{content.episode_id}')" if content.episode_id else ""}
                """
            )
            stat =  cursor.fetchone()

            content = self.serializer_class(content).data
            print("\n\n")
            print("content", content, type(content))
            print("\n\n")
            content.update({"watched_users": 0, "watched_duration": 0, "age_group": {}, "gender": {}})
            if stat:
                content["watched_users"] = stat[1]
                content["watched_duration"] = stat[2]
                content["age_group"] = stat[3]
                content["gender"] = stat[4]
            # get best 30 stats and return
            res.append(content)

        if qs_filter:
            # paginate
            pass
        
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

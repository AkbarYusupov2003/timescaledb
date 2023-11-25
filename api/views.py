import json
import datetime
from django.db import connection
from django.db.models import Sum, Q
from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from api import serializers
from api import utils
from statistic import models
from internal import models as internal_models


# Content: http://127.0.0.1:8000/content-stat/?period=day&from_date=2023-11-22-0:00&to_date=2023-11-30-00:00
# Subscription: http://127.0.0.1:8000/content-stat/?period=month&from_date=2023-11-22-0:00&to_date=2023-11-30-00:00&country=UZ&device=PC&gender=M&country=UZ
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

# Internal
class SponsorListAPIView(generics.ListAPIView):
    queryset = internal_models.Sponsor.objects.filter(is_chosen=True)
    serializer_class = serializers.SponsorSerializer


class SubscriptionListAPIView(generics.ListAPIView):
    queryset = internal_models.AllowedSubscription.objects.all()
    serializer_class = serializers.AllowedSubscriptionSerializer


class CategoryListAPIView(generics.ListAPIView):
    queryset = internal_models.Category.objects.all()
    serializer_class = serializers.CategorySerializer


class BroadcastCategoryListAPIView(generics.ListAPIView):
    queryset = internal_models.BroadcastCategory.objects.all()
    serializer_class = serializers.BroadcastCategorySerializer
# Internal ended


# History
class CreateHistoryAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        print("create history")
        try:
            splay_data = utils.get_data_from_token(self.request.data.get("token"))
            if not splay_data:
                return Response({"Error": "token validation"}, status=400)
            content_id = int(request.data.get('content_id', 0))
            broadcast_id = int(request.data.get('broadcast_id', 0))
            episode_id = int(request.data.get('episode_id', 0))
            sid = splay_data["sid"]# "sdgt21gknmg'l3kwgnnk"
            country = splay_data["c_code"]["country_code"] # "UZ"
            gender = splay_data.get("gender", "M") # splay_data["gender"] # "M"
            age = utils.get_group_by_age(splay_data["age"]) # utils.get_group_by_age(19)
            device = splay_data.get("device", "PC") # splay_data["device"]
        except Exception as e:
            return Response({"Error": e}, status=400)

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[-1].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        user_agent = request.META.get('HTTP_USER_AGENT', '')

        data = {
            "sid": sid, "ip_address": ip_address, "user_agent": user_agent, "device": device, 
            "time": datetime.datetime.now(), "gender": gender, "age_group": age, "country": country
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
class ContentStatAPIView(generics.GenericAPIView):
    queryset = internal_models.Content.objects.all().select_related(
        "category"
    ).prefetch_related("sponsors", "allowed_subscriptions")
    serializer_class = serializers.ContentSerializer
    pagination_class = LimitOffsetPagination
    
    def get(self, request, *args, **kwargs):
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        period = request.GET.get("period")
        search = request.GET.get("search")
        sub_id = request.GET.get("sub_id")
        sponsors = request.GET.get("sponsors", "")
        category = request.GET.get("category", "")
        is_russian = request.GET.get("is_russian")
        ordering = request.GET.get("ordering")
        age_group = request.GET.get("age_group")
        gender = request.GET.get("gender")
        country = request.GET.get("country")
        device = request.GET.get("device")
        # ------------------------------------------------------------------------------------------
        allowed_periods = internal_models.AllowedPeriod.objects.all().values_list("name", flat=True)
        allowed_subscriptions = internal_models.AllowedSubscription.objects.all().values_list("sub_id", flat=True)
        qs_filter = {}

        raw_filter = []
        try:
            limit = int(request.GET.get("limit", 20))
            offset = int(request.GET.get("offset", 0))
        except:
            return Response({"error": "limit, offset validation"}, status=400)

        if not(period in allowed_periods):
            return Response({"error": "period validation"}, status=400)

        if search:
            qs_filter["title_ru__icontains"] = search

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
        
        if age_group in models.AGE_GROUPS_LIST:
            raw_filter.append(f"AND (age_group = '{age_group}')")
            
        if gender in models.GENDERS_LIST:
            raw_filter.append(f"AND (gender = '{gender}')")

        if country:
            raw_filter.append(f"AND (country = '{country}')")

        if device:
            raw_filter.append(f"AND (device = '{device}')")

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

        order_after_execution = (
            "watched_users", "-watched_users", "watched_duration", "-watched_duration"
        )

        if ordering:
            if (ordering == "duration" or ordering == "-duration") or \
               (ordering == "id" or ordering == "-id") or \
               (ordering == "title" or ordering == "-title"):
                    queryset = queryset.order_by(ordering)

        if ordering not in order_after_execution:
            queryset = queryset[offset:limit+offset]

        res = []

        for content in queryset:
            cursor = connection.cursor()
            raw_filter = " ".join(raw_filter) if raw_filter else ""
            episode_id = f"AND (episode_id = '{content.episode_id}')" if content.episode_id else ""
            print("raw", raw_filter)
            
            query = f"""SELECT time_bucket('1 {period}', time) AS interval, Sum(watched_users_count), Sum(watched_duration)
                        FROM {table_name}
                        WHERE (time BETWEEN '{from_date}' AND '{to_date}') AND (content_id = '{content.content_id}') {episode_id} {raw_filter}
                        GROUP BY interval, watched_users_count, watched_duration"""
            
            print("query", query)
            cursor.execute(query)
            stat =  cursor.fetchall()
            print("STAT: ", stat)
            print("\n")
            content = self.serializer_class(content).data

            watched_users = watched_duration = 0
            for s in stat:
                watched_users += s[1]
                watched_duration += s[2]

            content.update({"watched_users": watched_users, "watched_duration": watched_duration})
            res.append(content)

        # for content in queryset:
        #     cursor = connection.cursor()
        #     cursor.execute(
        #         f"""
        #             SELECT time_bucket('1 {period}', time) AS interval, watched_users_count, watched_duration, age_group::json, gender::json
        #             FROM {table_name}
        #             WHERE (time BETWEEN '{from_date}' AND '{to_date}') AND
        #                   (content_id = '{content.content_id}')
        #                   {f"AND (episode_id = '{content.episode_id}')" if content.episode_id else ""}
        #         """
        #     )
        #     stat =  cursor.fetchone()
        #     content = self.serializer_class(content).data
        #     content.update({"watched_users": 0, "watched_duration": 0, "age_group": {}, "gender": {}})
        #     if stat:
        #         content["watched_users"] = stat[1]
        #         content["watched_duration"] = stat[2]
        #         content["age_group"] = stat[3]
        #         content["gender"] = stat[4]
        #     res.append(content)

        if ordering == "watched_users":
            res = sorted(res, key=lambda d: d["watched_users"])[offset:limit+offset]
        elif ordering == "-watched_users":
            res = sorted(res, key=lambda d: d["watched_users"], reverse=True)[offset:limit+offset]
        elif ordering == "watched_duration":
            res = sorted(res, key=lambda d: d["watched_duration"])[offset:limit+offset]
        elif ordering == "-watched_duration":
            res = sorted(res, key=lambda d: d["watched_duration"], reverse=True)[offset:limit+offset]

        return Response(res, status=200)


# Register
class RegisterStatAPIView(APIView):
    serializer_class = serializers.RegisterSerializer
        
    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get("from_date")
        to_date = self.request.GET.get("to_date")
        period = self.request.GET.get("period")
        # validation
        allowed_periods = internal_models.AllowedPeriod.objects.all().values_list("name", flat=True)
        if not(period in allowed_periods):
            return Response({"error": "period validation"}, status=400)
        try:
            date_format = "%Y-%m-%d"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format)
        except:
            return Response({"error": "date validation"}, status=400)
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
        queryset = cursor.fetchall()
        res = self.serializer_class(queryset, many=True)
        return Response(res.data, status=200)


class RegisterTotalStatAPIView(APIView):

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
class SubscriptionStatAPIView(APIView):
    serializer_class = serializers.SubscriptionSerializer

    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get("from_date")
        to_date = self.request.GET.get("to_date")
        period = self.request.GET.get("period")
        sub_id = self.request.GET.get("sub_id")
        # validation
        allowed_periods = internal_models.AllowedPeriod.objects.all().values_list("name", flat=True)
        allowed_subs = internal_models.AllowedSubscription.objects.all().values_list("sub_id", flat=True)
        if not(period in allowed_periods):
            return Response({"error": "period validation"}, status=400)
        if sub_id and not(sub_id in allowed_subs):
            return Response({"error": "sub_id validation"}, status=400)
        try:
            date_format = "%Y-%m-%d"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format)
        except:
            return Response({"error": "date validation"}, status=400)
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
        queryset = cursor.fetchall()
        res = self.serializer_class(queryset, many=True)
        return Response(res.data, status=200)


class SubscriptionTotalStatAPIView(APIView):
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

# TODO 
# Report
class ReportCreateView(APIView):
    # GET https://legacy.glob.uz/ru/api/v1/report/make/content?offset=0&limit=20&period=hour&page=0&search=серебро
    # allowed_reports = content, broadcast
    def get(self, request, *args, **kwargs):
        group = request.GET.get("group")
        if group == "content":
            print("creating report for content")
            data_for_file = 1
            qs = 1
            # ...
            # models.Report.objects.create(
            #     section="content", lines_count=qs.count()
            # )
            return Response({"worked": 1})
        elif group == "broadcast":
            print("creating report for broadcast")
            return Response({"worked": 2})
        else:
            return Response({"error": "report group validation"}, status=400)

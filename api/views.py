import json
import datetime
from decimal import Decimal, getcontext
from django.db import connection
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from api import serializers
from api import utils
from statistic import models
from internal import models as internal_models


# Content: http://127.0.0.1:8000/content-stat/?period=day&from_date=2023-11-22-0:00&to_date=2023-11-30-00:00
# Content Detail: http://127.0.0.1:8000/content-stat/2635_9903/?period=day&from_date=2022-02-12-16:00&to_date=2023-12-11-17:00
# Subscription: 
# Register: http://127.0.0.1:8000/register-stat/?period=day&from_date=2022-12-16&to_date=2023-12-17


# Internal
class SponsorListAPIView(generics.ListAPIView):
    queryset = internal_models.Sponsor.objects.filter(is_chosen=True)
    serializer_class = serializers.SponsorSerializer


class AllowedSubscriptionListAPIView(generics.ListAPIView):
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
            gender = "M" # splay_data["gender"] # "M"
            age = utils.get_group_by_age(splay_data["age"]) # utils.get_group_by_age(19)
        except Exception as e:
            return Response({"Error": e}, status=400)

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[-1].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        user_agent = request.META.get('HTTP_USER_AGENT', '')

        data = {
            "sid": sid, "ip_address": ip_address, "user_agent": user_agent,
            "time": datetime.datetime.now(), "gender": gender, "age_group": age,
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
class ContentStatAPIView(APIView):
    queryset = internal_models.Content.objects.all().select_related(
        "category"
    ).prefetch_related("sponsors", "allowed_subscriptions")
    serializer_class = serializers.ContentSerializer
    
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
        # ------------------------------------------------------------------------------------------
        allowed_subscriptions = internal_models.AllowedSubscription.objects.all().values_list("pk", flat=True)
        qs_filter = {}

        raw_filter = []
        try:
            limit = int(request.GET.get("limit", 20))
            offset = int(request.GET.get("offset", 0))
        except:
            return Response({"error": "limit, offset validation"}, status=400)

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

        try:
            date_format = "%Y-%m-%d-%H:%M"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format)
            only_month_select = ""
            if period == "hours":
                table_name = "statistic_content_hour"
            elif period == "day":
                table_name = "statistic_content_day"
            elif period == "month":
                table_name = "statistic_content_month"
                only_month_select = ", SUM(watched_users_count)"
            else:
                return Response({"error": "period validation"}, status=400)
        except:
            return Response({"error": "date validation"}, status=400)

        queryset = self.queryset.filter(**qs_filter)

        if search:
            queryset = queryset.filter(
                Q(title_ru__icontains=search) |
                Q(title_uz__icontains=search) |
                Q(title_en__icontains=search)
            )
        
        order_before_execution = (
            "duration", "-duration", "id", "-id", "title", "-title"
        )
        order_after_execution = (
            "watched_users", "-watched_users", "watched_duration", "-watched_duration"
        )

        if ordering in order_before_execution:
            queryset = queryset.order_by(ordering)
        elif not (ordering in order_after_execution):
            queryset = queryset[offset:limit+offset]

        res = []

        for content in queryset:
            cursor = connection.cursor()
            raw_filter = " ".join(raw_filter) if raw_filter else ""
            content_id = f"AND (content_id = '{content.content_id}')"
            episode_id = f"AND (episode_id = '{content.episode_id}')" if content.episode_id else ""
            # TODO CHECK IF MONTH OR NOT, ( проверять через if написать 2 query и 2 for s in stat )
            query = f"""SELECT time_bucket('1 {period}', time) AS interval {only_month_select} , SUM(watched_duration)
                        FROM {table_name}
                        WHERE (time BETWEEN '{from_date}' AND '{to_date}') {content_id} {episode_id} {raw_filter}
                        GROUP BY interval, watched_users_count, watched_duration"""
            cursor.execute(query)
            stat =  cursor.fetchall()
            content = self.serializer_class(content).data
            total_watched_users = total_watched_duration = 0
            for s in stat:
                total_watched_users += s[1]
                total_watched_duration += s[2]
            content["watched_users"] = total_watched_users
            content["watched_duration"] = total_watched_duration
            res.append(content)

        if ordering == "watched_users":
            res = sorted(res, key=lambda d: d["watched_users"])[offset:limit+offset]
        elif ordering == "-watched_users":
            res = sorted(res, key=lambda d: d["watched_users"], reverse=True)[offset:limit+offset]
        elif ordering == "watched_duration":
            res = sorted(res, key=lambda d: d["watched_duration"])[offset:limit+offset]
        elif ordering == "-watched_duration":
            res = sorted(res, key=lambda d: d["watched_duration"], reverse=True)[offset:limit+offset]

        return Response(res, status=200)


class ContentStatDetailAPIView(APIView):
    serializer_class = serializers.ContentSerializer

    def get(self, request, *args, **kwargs):
        content = get_object_or_404(
            internal_models.Content.objects.select_related("category").prefetch_related("sponsors", "allowed_subscriptions"),
            slug=kwargs["slug"]
        )
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        period = request.GET.get("period")

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
        except:
            return Response({"error": "date validation"}, status=400)

        gender_counter = f"""SUM(watched_users_count) FILTER (WHERE gender = 'M') AS men,
                             SUM(watched_users_count) FILTER (WHERE gender = 'W') AS women"""
        cursor = connection.cursor()
        content_id = f"(content_id = '{content.content_id}')"
        episode_id = f"AND (episode_id = '{content.episode_id}')" if content.episode_id else ""
        query = f"""SELECT time_bucket('1 {period}', time) AS interval, SUM(watched_users_count), {gender_counter}, age_group
                    FROM {table_name}
                    WHERE (time BETWEEN '{from_date}' AND '{to_date}') AND {content_id} {episode_id}
                    GROUP BY interval, watched_users_count, age_group"""

        cursor.execute(query)
        stat =  cursor.fetchall()
        content = self.serializer_class(content).data

        data = []        
        
        children = {"percentage": 0, "0": 0, "1": 0, "2": 0}
        men = {"percentage": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0}
        women = {"percentage": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0}
        total_watched_users = 0
        
        for s in stat:
            exists = False
            for val in data:
                if val.get("time") == s[0]:
                    val["watched_users"] +=  s[1]
                    exists = True
            if not exists:
                data.append({"time": s[0], "watched_users": s[1],})
            age_group = s[4]
            if age_group in children.keys():
                children[age_group] += s[1]
            else:
                if s[2]:
                    men[age_group] += s[2]
                if s[3]:
                    women[age_group] += s[3]
            total_watched_users += s[1]

        content["data"] = data
        content["total"] = total_watched_users
        content["all-time"] = 0
        
        getcontext().prec = 3
        men["total"] = sum(men.values())
        women["total"] = sum(women.values())
        children["total"] = sum(children.values())
        if total_watched_users:
            men["percentage"] = Decimal(men["total"]) / Decimal(total_watched_users) * 100
            women["percentage"] = Decimal(women["total"]) / Decimal(total_watched_users) * 100
            children["percentage"] = Decimal(children["total"]) / Decimal(total_watched_users) * 100
        content["men"] = men
        content["women"] = women
        content["children"] = children
        query = f"""SELECT SUM(watched_users_count)
                    FROM statistic_broadcast_day
                    WHERE {content_id} {episode_id}"""
        cursor.execute(query)
        all_time = cursor.fetchone()
        if all_time:
            content["all-time"] = all_time[0]
        else:
            content["all-time"] = 0
        return Response(content, status=200)


class BroadcastStatAPIView(APIView):
    queryset = internal_models.Broadcast.objects.all().select_related(
        "category"
    )
    serializer_class = serializers.BroadcastSerializer

    def get(self, request, *args, **kwargs):
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        period = request.GET.get("period")
        category = request.GET.get("category", "")
        lang = request.GET.get("lang") # TODO
        ordering = request.GET.get("ordering")
        # ------------------------------------------------------------------------------------------
        try:
            limit = int(request.GET.get("limit", 20))
            offset = int(request.GET.get("offset", 0))
        except:
            return Response({"error": "limit, offset validation"}, status=400)

        qs_filter = {}

        try:
            date_format = "%Y-%m-%d-%H:%M"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format)
            if period == "hours":
                table_name = "statistic_broadcast_hour"
            elif period == "day":
                table_name = "statistic_broadcast_day"
            elif period == "month":
                table_name = "statistic_broadcast_month"
            else:
                return Response({"error": "period validation"}, status=400)
        except:
            return Response({"error": "date validation"}, status=400)

        if category.isnumeric():
            qs_filter["category__pk"] = category
        
        queryset = self.queryset.filter(**qs_filter)

        order_before_execution = (
            "duration", "-duration", "id", "-id", "title", "-title"
        )
        order_after_execution = (
            "watched_users", "-watched_users", "watched_duration", "-watched_duration"
        )

        if ordering in order_before_execution:
            if ordering == "id":
                queryset = queryset.order_by("broadcast_id")
            elif ordering == "-id":
                queryset = queryset.order_by("-broadcast_id")
            else:
                queryset = queryset.order_by(ordering)
        elif not (ordering in order_after_execution):
            queryset = queryset[offset:limit+offset]

        res = []
        for broadcast in queryset:
            broadcast_id = f"AND (broadcast_id = '{broadcast.broadcast_id}')"
            cursor = connection.cursor()
            query = f"""SELECT time_bucket('1 {period}', time) AS interval, SUM(watched_users_count), SUM(watched_duration)
                         FROM {table_name}
                         WHERE (time BETWEEN '{from_date}' AND '{to_date}') {broadcast_id}
                         GROUP BY interval, watched_users_count, watched_duration"""
            cursor.execute(query)
            stat = cursor.fetchall()
            broadcast = self.serializer_class(broadcast).data
            total_watched_users = total_watched_duration = 0
            for s in stat:
                total_watched_users += s[1]
                total_watched_duration += s[2]
            broadcast["watched_users"] = total_watched_users
            broadcast["watched_duration"] = total_watched_duration
            res.append(broadcast)

        if ordering == "watched_users":
            res = sorted(res, key=lambda d: d["watched_users"])[offset:limit+offset]
        elif ordering == "-watched_users":
            res = sorted(res, key=lambda d: d["watched_users"], reverse=True)[offset:limit+offset]
        elif ordering == "watched_duration":
            res = sorted(res, key=lambda d: d["watched_duration"])[offset:limit+offset]
        elif ordering == "-watched_duration":
            res = sorted(res, key=lambda d: d["watched_duration"], reverse=True)[offset:limit+offset]

        return Response(res, status=200)


class BroadcastStatDetailAPIView(APIView):
    serializer_class = serializers.BroadcastSerializer

    def get(self, request, *args, **kwargs):
        broadcast = get_object_or_404(
            internal_models.Broadcast.objects.select_related("category"),
            broadcast_id=self.kwargs["pk"]
        )
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        period = request.GET.get("period")
        try:
            date_format = "%Y-%m-%d-%H:%M"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format)
            if period == "hours":
                table_name = "statistic_broadcast_hour"
            elif period == "day":
                table_name = "statistic_broadcast_day"
            elif period == "month":
                table_name = "statistic_broadcast_month"
            else:
                return Response({"error": "period validation"}, status=400)
        except:
            return Response({"error": "date validation"}, status=400)
        cursor = connection.cursor()
        broadcast_id = f"(broadcast_id = '{broadcast.broadcast_id}')"
        query = f"""SELECT time_bucket('1 {period}', time) AS interval, SUM(watched_users_count), SUM(watched_duration)
                    FROM {table_name}
                    WHERE (time BETWEEN '{from_date}' AND '{to_date}') AND {broadcast_id}
                    GROUP BY interval, watched_users_count, watched_duration"""
        cursor.execute(query)
        stat = cursor.fetchall()
        broadcast = self.serializer_class(broadcast).data

        data = []
        total_watched_users = 0

        for s in stat:
            exists = False
            for val in data:
                if val.get("time") == s[0]:
                    val["watched_users"] +=  s[1]
                    val["watched_duration"] +=  s[2]
                    exists = True
            if not exists:
                data.append({"time": s[0], "watched_users": s[1], "watched_duration": s[2]})
            total_watched_users += s[1]

        broadcast["data"] = data
        broadcast["total"] = total_watched_users
        
        query = f"""SELECT SUM(watched_users_count)
                    FROM statistic_broadcast_day
                    WHERE {broadcast_id}"""
        cursor.execute(query)
        all_time = cursor.fetchone()
        if all_time:
            broadcast["all-time"] = all_time[0]
        else:
            broadcast["all-time"] = 0

        return Response(broadcast, status=200)


# Register
class RegisterStatAPIView(APIView):
    serializer_class = serializers.RegisterSerializer
        
    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get("from_date")
        to_date = self.request.GET.get("to_date")
        period = self.request.GET.get("period")
        if not(period in utils.ALLOWED_PERIODS):
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
        allowed_subs = internal_models.AllowedSubscription.objects.all().values_list("pk", flat=True)
        if not(period in utils.ALLOWED_PERIODS):
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


# TODO Report
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


# ------------------------------------------------
class ProfileHourView(APIView):
    
    def get(self, request, *args, **kwargs):
        print("GET")
        return Response({"worked": True}, status=200)

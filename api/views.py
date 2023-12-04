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
from statistic.utils import report
from statistic import models
from internal import models as internal_models


# Contents: http://127.0.0.1:8000/content-stat/?period=hours&from_date=2023-11-30-11h&to_date=2023-12-11-0h
# Content detail: http://127.0.0.1:8000/content-stat/3555_10796/?period=hours&from_date=2023-11-30-11h&to_date=2023-12-11-0h

# Subscription: http://127.0.0.1:8000/subscription-stat/?period=day&from_date=2022-12-16&to_date=2023-12-17
# Register: http://127.0.0.1:8000/register-stat/?period=day&from_date=2022-12-16&to_date=2023-12-17

# TODO add next and previous pages params to Content and Broadcast list


# Internal
class SponsorListAPIView(generics.ListAPIView):
    queryset = internal_models.Sponsor.objects.filter(is_chosen=True)
    serializer_class = serializers.SponsorSerializer


class AllowedSubscriptionListAPIView(generics.ListAPIView):
    queryset = internal_models.AllowedSubscription.objects.all()
    serializer_class = serializers.AllowedSubscriptionSerializer


class CategoryListAPIView(generics.ListAPIView):
    queryset = internal_models.Category.objects.filter(ordering__isnull=False)
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
        report_param = request.GET.get("report")
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
            date_format = "%Y-%m-%d-%Hh"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format).replace(minute=59, second=59)
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

        queryset = self.queryset.filter(**qs_filter)

        if search:
            queryset = queryset.filter(
                Q(title_ru__icontains=search) |
                Q(title_uz__icontains=search) |
                Q(title_en__icontains=search)
            )
        
        contents_number = queryset.count()
        
        order_before_execution = (
            "duration", "-duration", "id", "-id", "title", "-title"
        )
        order_after_execution = (
            "watched_users", "-watched_users", "watched_duration", "-watched_duration"
        )

        if ordering in order_before_execution:
            queryset = queryset.order_by(ordering)

        if not (ordering in order_after_execution):
            queryset = queryset[offset:limit+offset]

        res = []

        for content in queryset:
            cursor = connection.cursor()
            raw_filter = " ".join(raw_filter) if raw_filter else ""
            content_id = f"AND (content_id = '{content.content_id}')"
            episode_id = f"AND (episode_id = '{content.episode_id}')" if content.episode_id else ""

            if table_name == "statistic_content_month":
                query = f"""SELECT time_bucket('1 {period}', time) AS interval, SUM(watched_users_count), SUM(watched_duration)
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
                content["watched_duration"] = total_watched_duration
                content["watched_users"] = total_watched_users
            else:
                query = f"""SELECT time_bucket('1 {period}', time) AS interval, SUM(watched_duration)
                            FROM {table_name}
                            WHERE (time BETWEEN '{from_date}' AND '{to_date}') {content_id} {episode_id} {raw_filter}
                            GROUP BY interval, watched_duration"""
                cursor.execute(query)
                stat =  cursor.fetchall()
                content = self.serializer_class(content).data
                watched_duration = watched_users = 0
                for s in stat:
                    watched_duration += s[1]
                    watched_users += 1
                content["watched_duration"] = watched_duration
                content["watched_users"] = watched_users

            res.append(content)

        if ordering == "watched_users":
            res = sorted(res, key=lambda d: d["watched_users"])[offset:limit+offset]
        elif ordering == "-watched_users":
            res = sorted(res, key=lambda d: d["watched_users"], reverse=True)[offset:limit+offset]
        elif ordering == "watched_duration":
            res = sorted(res, key=lambda d: d["watched_duration"])[offset:limit+offset]
        elif ordering == "-watched_duration":
            res = sorted(res, key=lambda d: d["watched_duration"], reverse=True)[offset:limit+offset]

        if report_param == "True":
            if res:
                validate_filters = {
                    "search": search, "sub_id": sub_id, "sponsors": sponsors, "category": category, 
                    "is_russian": is_russian, "age_group": age_group, "gender": gender,"ordering": ordering
                }
                additional_data = {"count": len(res), "period": period, "from_date": str(from_date), "to_date": str(to_date)}
                for key, value in validate_filters.items():
                    if value:
                        additional_data[key] = value

                instance = models.Report.objects.create(
                    section=models.Report.SectionChoices.content, status=models.Report.StatusChoices.generating, additional_data=additional_data
                )
                report.generate_content_report.delay(instance.pk, res, str(from_date), str(to_date))
                return Response({"message": "The task for report created"}, status=201)
            else:
                return Response({"message": "The result of filtration is empty, report will not be created"}, status=417)

        return Response({"count": contents_number, "results": res}, status=200)


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
            date_format = "%Y-%m-%d-%Hh"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format).replace(minute=59, second=59)
            if period == "hours":
                table_name = "statistic_content_hour"
            elif period == "day":
                table_name = "statistic_content_day"
            elif period == "month":
                table_name = "statistic_content_month"
            else:
                return Response({"error": "period validation"}, status=400)
        except Exception as e:
            print("exception", e)
            return Response({"error": "date validation"}, status=400)
        
        content_id = f"(content_id = '{content.content_id}')"
        episode_id = f"AND (episode_id = '{content.episode_id}')" if content.episode_id else ""
        
        children = {"percentage": 0, "0": 0, "1": 0, "2": 0}
        men = {"percentage": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0}
        women = {"percentage": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0}
        total_watched_users = 0
        
        data = []
        cursor = connection.cursor()
        if table_name == "statistic_content_month":
            gender_counter = f"""SUM(watched_users_count) FILTER (WHERE gender = 'M') AS men,
                                 SUM(watched_users_count) FILTER (WHERE gender = 'W') AS women"""
            query = f"""SELECT time_bucket('1 {period}', time) AS interval, SUM(watched_users_count), {gender_counter}, age_group
                        FROM {table_name}
                        WHERE (time BETWEEN '{from_date}' AND '{to_date}') AND {content_id} {episode_id}
                        GROUP BY interval, watched_users_count, age_group"""
            cursor.execute(query)
            stat =  cursor.fetchall()
            content = self.serializer_class(content).data        
            for s in stat:
                exists = False
                for val in data:
                    if val.get("time") == s[0]:
                        val["watched_users"] +=  s[1]
                        exists = True
                if not exists:
                    data.append({"time": s[0], "watched_users": s[1],})
                age_group = s[4]
                if age_group in utils.CHILDREN_AGE_GROUPS:
                    children[age_group] += s[1]
                else:
                    if s[2]:
                        men[age_group] += s[2]
                    if s[3]:
                        women[age_group] += s[3]
                total_watched_users += s[1]
        else:
            gender_counter = f"""COUNT(*) FILTER (WHERE gender = 'M') AS men,
                                 COUNT(*) FILTER (WHERE gender = 'W') AS women"""
            query = f"""SELECT time_bucket('1 {period}', time) AS interval, {gender_counter}, age_group
                        FROM {table_name}
                        WHERE (time BETWEEN '{from_date}' AND '{to_date}') AND {content_id} {episode_id}
                        GROUP BY interval, age_group"""
            cursor.execute(query)
            stat =  cursor.fetchall()
            content = self.serializer_class(content).data
            for s in stat:
                time = s[0]
                exists = False
                watched_users = s[1] + s[2]
                for val in data:
                    if val.get("time") == time:
                        val["watched_users"] += watched_users
                        exists = True
                if not exists:
                    data.append({"time": time, "watched_users": watched_users,})

                age_group = s[3]
                if age_group in utils.CHILDREN_AGE_GROUPS:
                    children[age_group] += watched_users
                else:
                    if s[1]:
                        men[age_group] += s[1]
                    if s[2]:
                        women[age_group] += s[2]
                total_watched_users += watched_users

        content["data"] = data
        content["total"] = total_watched_users
        content["all-time"] = 0
        
        getcontext().prec = 3
        men["count"] = sum(men.values())
        women["count"] = sum(women.values())
        children["count"] = sum(children.values())
        if total_watched_users:
            men["percentage"] = Decimal(men["count"]) / Decimal(total_watched_users) * 100
            women["percentage"] = Decimal(women["count"]) / Decimal(total_watched_users) * 100
            children["percentage"] = Decimal(children["count"]) / Decimal(total_watched_users) * 100
        content["men"] = men
        content["women"] = women
        content["children"] = children
        query = f"""SELECT COUNT(*)
                    FROM statistic_content_day
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
        report_param = request.GET.get("report")
        # ------------------------------------------------------------------------------------------
        try:
            limit = int(request.GET.get("limit", 20))
            offset = int(request.GET.get("offset", 0))
        except:
            return Response({"error": "limit, offset validation"}, status=400)

        qs_filter = {}

        try:
            date_format = "%Y-%m-%d-%Hh"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format).replace(minute=59, second=59)
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
        broadcasts_number = queryset.count()
        
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

        if not (ordering in order_after_execution) and not (report_param == "True"):
            queryset = queryset[offset:limit+offset]

        res = []
        for broadcast in queryset:
            broadcast_id = f"AND (broadcast_id = '{broadcast.broadcast_id}')"
            cursor = connection.cursor()
            if table_name == "statistic_broadcast_month":
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
            else:
                query = f"""SELECT time_bucket('1 {period}', time) AS interval, SUM(watched_duration)
                            FROM {table_name}
                            WHERE (time BETWEEN '{from_date}' AND '{to_date}') {broadcast_id}
                            GROUP BY interval, watched_duration"""
                cursor.execute(query)
                stat = cursor.fetchall()
                broadcast = self.serializer_class(broadcast).data
                total_watched_users = total_watched_duration = 0
                for s in stat:
                    total_watched_users += 1
                    total_watched_duration += s[1]
                broadcast["watched_users"] = total_watched_users
                broadcast["watched_duration"] = total_watched_duration

            res.append(broadcast)
        if report_param == "True":
            if ordering == "watched_users":
                res = sorted(res, key=lambda d: d["watched_users"])
            elif ordering == "-watched_users":
                res = sorted(res, key=lambda d: d["watched_users"], reverse=True)
            elif ordering == "watched_duration":
                res = sorted(res, key=lambda d: d["watched_duration"])
            elif ordering == "-watched_duration":
                res = sorted(res, key=lambda d: d["watched_duration"], reverse=True)
            if res:
                validate_filters = {"category": category, "ordering": ordering}
                additional_data = {"count": len(res), "period": period, "from_date": str(from_date), "to_date": str(to_date)}
                for key, value in validate_filters.items():
                    if value:
                        additional_data[key] = value

                instance = models.Report.objects.create(
                    section=models.Report.SectionChoices.broadcast, status=models.Report.StatusChoices.generating, additional_data=additional_data
                )
                report.generate_broadcast_report.delay(instance.pk, res, str(from_date), str(to_date))
                return Response({"message": "The task for report created"}, status=201)
            else:
                return Response({"message": "The result of filtration is empty, report will not be created"}, status=417)
        else:
            pass
            if ordering == "watched_users":
                res = sorted(res, key=lambda d: d["watched_users"])[offset:limit+offset]
            elif ordering == "-watched_users":
                res = sorted(res, key=lambda d: d["watched_users"], reverse=True)[offset:limit+offset]
            elif ordering == "watched_duration":
                res = sorted(res, key=lambda d: d["watched_duration"])[offset:limit+offset]
            elif ordering == "-watched_duration":
                res = sorted(res, key=lambda d: d["watched_duration"], reverse=True)[offset:limit+offset]

        return Response({"count": broadcasts_number, "results": res}, status=200)


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
            date_format = "%Y-%m-%d-%Hh"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format).replace(minute=59, second=59)
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
        if table_name == "statistic_broadcast_month":
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
        else:
            broadcast_id = f"(broadcast_id = '{broadcast.broadcast_id}')"
            query = f"""SELECT time_bucket('1 {period}', time) AS interval, SUM(watched_duration)
                        FROM {table_name}
                        WHERE (time BETWEEN '{from_date}' AND '{to_date}') AND {broadcast_id}
                        GROUP BY interval, watched_duration"""
            cursor.execute(query)
            stat = cursor.fetchall()
            broadcast = self.serializer_class(broadcast).data
            data = []
            total_watched_users = 0
            for s in stat:
                exists = False
                for val in data:
                    if val.get("time") == s[0]:
                        val["watched_users"] +=  1
                        val["watched_duration"] +=  s[1]
                        exists = True
                if not exists:
                    data.append({"time": s[0], "watched_users": 1, "watched_duration": s[1]})
                total_watched_users += 1

        broadcast["data"] = data
        broadcast["total"] = total_watched_users
        
        query = f"""SELECT COUNT(*)
                    FROM statistic_broadcast_day
                    WHERE {broadcast_id}"""
        cursor.execute(query)
        all_time = cursor.fetchone()
        if all_time:
            broadcast["all-time"] = all_time[0]
        else:
            broadcast["all-time"] = 0

        return Response(broadcast, status=200)


# Report
class PerformingReportAPIView(APIView):
    serializer_class = serializers.PerformingReportSerializer

    def get(self, request, *args, **kwargs):
        queryset = models.Report.objects.exclude(status=models.Report.StatusChoices.finished)
        result = self.serializer_class(queryset, many=True).data
        return Response(result)


class PerformedReportAPIView(generics.ListAPIView):
    queryset = models.Report.objects.filter(status=models.Report.StatusChoices.finished)
    serializer_class = serializers.PerformedReportSerializer
    pagination_class = LimitOffsetPagination


class ReportDownloadedAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        report = get_object_or_404(models.Report, pk=kwargs["pk"])
        report.is_downloaded = True
        report.save()
        return Response({"message": "The value of report.is_downloaded field is set to True"}, status=200)


# TODO
class CategoryViewStatAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        period = request.GET.get("period")
        category = request.GET.get("category", "")
        age_group = request.GET.get("age_group") # TODO GET LIST OF AGE_GROUPS WITH "," delimiter
        report_param = request.GET.get("report")
        # TODO age_group - 6-25
        qs_filter = {}
        raw_filter = []
        if category.isnumeric():
            qs_filter["category_id"] = category

        if age_group in models.AGE_GROUPS_LIST:
            raw_filter.append(f"AND (age_group = '{age_group}')")

        try:
            date_format = "%Y-%m-%d-%Hh"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format).replace(minute=59, second=59)
            if period == "hours":
                table_name = "statistic_category_view_hour"
            elif period == "day":
                table_name = "statistic_category_view_day"
            elif period == "month":
                table_name = "statistic_category_view_month"
            else:
                return Response({"error": "period validation"}, status=400)
        except:
            return Response({"error": "date validation"}, status=400)

        
        cursor = connection.cursor()
        # query 1: time, gender, watched_users_count
        # query 2: category1: men: 1, women: 1, children: 1,     
        #          category2: men: 1, women: 1, children: 1  
        res = []
        categories_dict = {}
        query = f"""SELECT time_bucket('1 {period}', time) AS interval, SUM(watched_users_count), age_group, gender, category_id
                    FROM {table_name}
                    WHERE (time BETWEEN '{from_date}' AND '{to_date}')
                    GROUP BY interval, watched_users_count, age_group, gender, category_id"""
        cursor.execute(query)
        stat = cursor.fetchall()
        print("stat", stat)
        children_count = men_count = women_count = 0
        
        if category:
            for s in stat:
                time, watched_users, age_group, gender, category_id = s
                if age_group in utils.CHILDREN_AGE_GROUPS:
                    calculated_gender = "children"
                    women_count += watched_users
                elif gender == "M":
                    calculated_gender = "men"
                    men_count += watched_users
                else:
                    calculated_gender = "women"
                    children_count += watched_users

                if category == str(category_id):
                    # CALCULATE 1 CATEGORY
                    exists = False
                    for val in res:
                        if val.get("time") == time and val.get("gender") == calculated_gender:
                            val["watched_users"] += watched_users
                            exists = True
                    if not exists:
                        res.append({"time": s[0], "watched_users": s[1], "gender": calculated_gender})
                else:
                    # CALCULATE EVERY CATEGORY
                    print("abc")
                    
                print("iter", categories_dict.keys())
                if not(category_id in categories_dict.keys()):
                    categories_dict[category_id] = {"men": 0, "women": 0, "children": 0} 
                categories_dict[category_id][calculated_gender] += watched_users

        if report_param == "True":
            if res:
                pass
            else:
                return Response({"message": "The result of filtration is empty, report will not be created"}, status=417)

        return Response(
            {"total": 0, "children": children_count, "men": men_count, "women": women_count, "categories": categories_dict, "results": res},
            status=200
        )

        # gender_counter = f"""SUM(watched_users_count) FILTER (WHERE gender = 'M') AS men,
        #                      SUM(watched_users_count) FILTER (WHERE gender = 'W') AS women"""
        # query = f"""SELECT time_bucket('1 {period}', time) AS interval, SUM(watched_users_count), {gender_counter}, age_group
        #             FROM {table_name}
        #             WHERE (time BETWEEN '{from_date}' AND '{to_date}') AND {content_id} {episode_id}
        #             GROUP BY interval, watched_users_count, age_group"""
        # cursor.execute(query)
        # stat =  cursor.fetchall()
        # content = self.serializer_class(content).data        
        # for s in stat:
        #     exists = False
        #     for val in data:
        #         if val.get("time") == s[0]:
        #             val["watched_users"] +=  s[1]
        #             exists = True
        #     if not exists:
        #         data.append({"time": s[0], "watched_users": s[1],})
        #     age_group = s[4]
        #     if age_group in children.keys():
        #         children[age_group] += s[1]
        #     else:
        #         if s[2]:
        #             men[age_group] += s[2]
        #         if s[3]:
        #             women[age_group] += s[3]
        #     total_watched_users += s[1]


# Register
class RegisterStatAPIView(APIView):
    serializer_class = serializers.RegisterSerializer

    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get("from_date")
        to_date = self.request.GET.get("to_date")
        period = self.request.GET.get("period")
        report_param = request.GET.get("report")
        if not(period in utils.ALLOWED_PERIODS):
            return Response({"error": "period validation"}, status=400)
        try:
            date_format = "%Y-%m-%d"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format).replace(minute=59, second=59)
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
        data = cursor.fetchall()
        if report_param == "True":
            if data:
                additional_data = {"count": len(data), "period": period, "from_date": str(from_date), "to_date": str(to_date)}

                instance = models.Report.objects.create(
                    section=models.Report.SectionChoices.register, status=models.Report.StatusChoices.generating, additional_data=additional_data
                )
                report.generate_register_report.delay(instance.pk, data, period)
                return Response({"message": "The task for report created"}, status=201)
            else:
                return Response({"message": "The result of filtration is empty, report will not be created"}, status=417)
        res = self.serializer_class(data, many=True)
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
        report_param = request.GET.get("report")
        # validation
        allowed_subs = list(internal_models.AllowedSubscription.objects.all().values_list("pk", flat=True))        
        if not(period in utils.ALLOWED_PERIODS):
            return Response({"error": "period validation"}, status=400)
        try:
            if not(int(sub_id) in allowed_subs):
                return Response({"error": "sub_id validation"}, status=400)
        except:
            return Response({"error": "sub_id validation"}, status=400)
        try:
            date_format = "%Y-%m-%d"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format).replace(minute=59, second=59)
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
        data = cursor.fetchall()
        if report_param == "True":
            if data:
                additional_data = {"count": len(data), "period": period, "from_date": str(from_date), "to_date": str(to_date)}
                if sub_id:
                    additional_data["sub_id"] = sub_id

                instance = models.Report.objects.create(
                    section=models.Report.SectionChoices.subscriptions, status=models.Report.StatusChoices.generating, additional_data=additional_data
                )
                report.generate_subscription_report.delay(instance.pk, data, period, sub_id)
                return Response({"message": "The task for report created"}, status=201)
            else:
                return Response({"message": "The result of filtration is empty, report will not be created"}, status=417)
        res = self.serializer_class(data, many=True)
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


# ------------------------------------------------
class ProfileHourView(APIView):

    def get(self, request, *args, **kwargs):
        print("GET")
        return Response({"worked": True}, status=200)

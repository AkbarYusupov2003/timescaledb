import datetime
from decimal import Decimal, getcontext
from django.db import connection
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from api.v1 import serializers
from api.v1 import utils
from statistic.utils import report, data_extractor
from statistic import models
from internal import models as internal_models


# Contents: http://127.0.0.1:8000/content-stat/?period=month&from_date=2023-12-1-0h&to_date=2023-12-31-23h
# Content detail: http://127.0.0.1:8000/content-stat/3555_10796/?period=hours&from_date=2023-12-1-0h&to_date=2023-12-31-23h

# Subscription: http://127.0.0.1:8000/subscription-stat/?period=day&from_date=2022-12-16&to_date=2023-12-17
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

    def get_queryset(self):
        category_views = self.request.GET.get("category_views", "")
        if category_views == "True":
            return internal_models.Category.objects.all()
        else:
            return internal_models.Category.objects.filter(ordering__isnull=False)


class BroadcastCategoryListAPIView(generics.ListAPIView):
    queryset = internal_models.BroadcastCategory.objects.all()
    serializer_class = serializers.BroadcastCategorySerializer
# Internal ended


# History
class CreateHistoryAPIView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            splay_data = utils.get_data_from_token(request.META["HTTP_AUTHORIZATION"])
            print(splay_data)
            if not splay_data:
                return Response({"Error": "token validation"}, status=400)
            sid = utils.throttling_by_sid(splay_data["sid"])
            age = splay_data.get("age")
            gender = splay_data.get("gender")
            # TODO REMOVE
            age = 18
            gender = "M"
            #
            if (not age) or (not gender):
                return Response({"Error": "age, gender validation"}, status=400)
            age = utils.get_group_by_age(age)
            content_id = int(request.data.get('content_id', 0))
            broadcast_id = int(request.data.get('broadcast_id', 0))
            episode_id = int(request.data.get('episode_id', 0))
        except Exception as e:
            return Response({"Error": str(e)}, status=400)

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
        models.History.objects.create(**data)
        return Response({"message": "The history entry was added"}, status=201)


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
            if ordering == "title":
                ordering = "title_ru"
            elif ordering == "-title":
                ordering = "-title_ru"
            queryset = queryset.order_by(ordering)

        if not (ordering in order_after_execution):
            queryset = queryset[offset:limit+offset]

        res = []

        raw_filter = " ".join(raw_filter) if raw_filter else ""
        cursor = connection.cursor()
        for content in queryset:
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
        except:
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
        content["total-for-period"] = total_watched_users
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
            "id", "-id", "title", "-title"
        )

        if ordering in order_before_execution:
            if ordering == "id":
                queryset = queryset.order_by("broadcast_id")
            elif ordering == "-id":
                queryset = queryset.order_by("-broadcast_id")
            else:
                queryset = queryset.order_by(ordering)

        if not (report_param == "True"):
            queryset = queryset[offset:limit+offset]

        res = []
        cursor = connection.cursor()
        for broadcast in queryset:
            broadcast_id = f"AND (broadcast_id = '{broadcast.broadcast_id}')"
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
            res = []
            total_watched_users = 0
            for s in stat:
                exists = False
                for val in res:
                    if val.get("time") == s[0]:
                        val["watched_users"] +=  s[1]
                        val["watched_duration"] +=  s[2]
                        exists = True
                if not exists:
                    res.append({"time": s[0], "watched_users": s[1], "watched_duration": s[2]})
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
            res = []
            total_watched_users = 0
            for s in stat:
                exists = False
                for val in res:
                    if val.get("time") == s[0]:
                        val["watched_users"] +=  1
                        val["watched_duration"] +=  s[1]
                        exists = True
                if not exists:
                    res.append({"time": s[0], "watched_users": 1, "watched_duration": s[1]})
                total_watched_users += 1

        broadcast["results"] = res
        broadcast["total-for-period"] = total_watched_users
        
        query = f"""SELECT COUNT(*)
                    FROM statistic_broadcast_day
                    WHERE {broadcast_id}"""
        cursor.execute(query)
        all_time = cursor.fetchone()
        broadcast["all-time"] = all_time[0] if all_time[0] else 0

        return Response(broadcast, status=200)


# Category View
class CategoryViewsStatAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        period = request.GET.get("period")
        category = request.GET.get("category", "")
        age_group = request.GET.get("age_group", "").rstrip(",").split(",")
        report_param = request.GET.get("report")

        raw_filter = []
        if (category) and (not category.isnumeric()):
            return Response({"error": "category validation"}, status=400)

        if age_group[0]:
            for age in age_group:
                if raw_filter:
                    raw_filter.append(f"OR age_group = '{age}'")
                else:
                    raw_filter.append(f"AND (age_group = '{age}'")
            raw_filter.append(")")
        
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
        res = []
        categories_dict = {}
        raw_filter = " ".join(raw_filter) if raw_filter else ""
        query = f"""SELECT time_bucket('1 {period}', time) AS interval, watched_users_count, age_group, gender, category_id
                    FROM {table_name}
                    WHERE (time BETWEEN '{from_date}' AND '{to_date}') {raw_filter}
                    GROUP BY interval, watched_users_count, age_group, gender, category_id"""
        cursor.execute(query)
        stat = cursor.fetchall()
        all_time = children_count = men_count = women_count = 0

        for s in stat:
            time, watched_users, raw_age_group, gender, category_id = s
            exists = update_res = False
            if raw_age_group in utils.CHILDREN_AGE_GROUPS:
                calc_gender = "children"
                children_count += watched_users
            elif gender == "M":
                calc_gender = "men"
                men_count += watched_users
            else:
                calc_gender = "women"
                women_count += watched_users
            if category == str(category_id):
                update_res = True
            elif not category:
                update_res = True
            if update_res:
                for val in res:
                    if val.get("time") == time:
                        val[calc_gender] += watched_users
                        exists = True
                if not exists:
                    res.append({"time": time, "men": 0, "women": 0, "children": 0})
                    res[-1][calc_gender] += watched_users
            if not(category_id in categories_dict.keys()):
                categories_dict[category_id] = {"men": 0, "women": 0, "children": 0}
            categories_dict[category_id][calc_gender] += watched_users

        query = f"""SELECT SUM(watched_users_count) FROM statistic_category_view_day"""
        cursor.execute(query)
        val = cursor.fetchone()
        all_time = val[0] if val[0] else 0

        if report_param == "True":
            if res:
                additional_data = {"period": period, "from_date": str(from_date), "to_date": str(to_date)}
                if category:
                    category = models.Category.objects.get(pk=category).name_ru
                    additional_data["category"] = category
                readable_age = []
                if age_group[0]:
                    for age in age_group:
                        readable_age.append(utils.AGE_GROUP_DICT[age])
                    additional_data["age_group"] = age_group
                instance = models.Report.objects.create(
                    section=models.Report.SectionChoices.category_views,
                    status=models.Report.StatusChoices.generating,
                    additional_data=additional_data
                )
                report.generate_category_views_report.delay(instance.pk, res, category, ", ".join(readable_age), period)
                return Response({"message": "The task for report created"}, status=201)
            else:
                return Response({"message": "The result of filtration is empty, report will not be created"}, status=417)

        # try:
        #     for key in list(categories_dict.keys()):
        #         cat_name = models.Category.objects.get(pk=key).name_ru
        #         categories_dict[cat_name] = categories_dict.pop(key)
        # except:
        #     pass
        
        return Response(
            {"all-time": all_time, "children": children_count, "men": men_count, "women": women_count, "categories": categories_dict, "results": res},
            status=200
        )


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


# Register
class RegisterStatAPIView(APIView):
    serializer_class = serializers.RegisterSerializer

    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get("from_date")
        to_date = self.request.GET.get("to_date")
        period = self.request.GET.get("period")
        report_param = request.GET.get("report")
        
        if period == "hours":
            table_name = "statistic_register_hour"
        elif period == "day" or period == "month":
            table_name = "statistic_register_day"
        else:
            return Response({"error": "period validation"}, status=400)

        try:
            date_format = "%Y-%m-%d"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format).replace(minute=59, second=59)
        except:
            return Response({"error": "date validation"}, status=400)
        # ------------------------------------------------------------------------------------------
        cursor = connection.cursor()
        cursor.execute(
            f"""
                SELECT time_bucket('1 {period}', time) AS interval, SUM(count)
                FROM {table_name}
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
                FROM statistic_register_hour
                WHERE (time BETWEEN '{today}' AND '{tomorrow}' )
                GROUP BY interval
                ORDER BY interval DESC;
            """
        )
        return cursor.fetchone()

    def get(self, request, *args, **kwargs):
        total = models.RegisterDay.objects.all().aggregate(Sum("count"))["count__sum"]
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
        
        if period == "hours":
            table_name = "statistic_subscription_hour"
        elif period == "day" or period == "month":
            table_name = "statistic_subscription_day"
        else:
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
        # ------------------------------------------------------------------------------------------
        cursor = connection.cursor()
        cursor.execute(
            f"""
                SELECT time_bucket('1 {period}', time) AS interval, SUM(count)
                FROM {table_name}
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
                FROM statistic_subscription_hour
                WHERE (time BETWEEN '{today}' AND '{tomorrow}' )
                GROUP BY interval
                ORDER BY interval DESC;
            """
        )
        return cursor.fetchone()

    def get(self, request, *args, **kwargs):
        total = models.SubscriptionDay.objects.all().aggregate(Sum("count"))["count__sum"]
        today = self.get_queryset()
        res = {"total": total if total else 0, "today": today[1] if today else 0}
        return Response(res, status=200)


# TODO (not working now)
class DeviceVisitsAPIView(APIView):

    def get(self, request, *args, **kwargs):
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        period = request.GET.get("period")
        app_type = request.GET.get("app_type")
        report_param = request.GET.get("report")

        raw_filter = []
        if app_type in models.APP_TYPES_LIST:
            raw_filter.append(f"AND (app_type = '{app_type}')")

        try:
            date_format = "%Y-%m-%d-%Hh"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format).replace(minute=59, second=59)
            if period == "hours":
                table_name = "statistic_device_visits_hour"
            elif period == "day":
                table_name = "statistic_device_visits_day"
            elif period == "month":
                table_name = "statistic_device_visits_month"
            else:
                return Response({"error": "period validation"}, status=400)
        except:
            return Response({"error": "date validation"}, status=400)
        
        res = {}
        periodic_res = []
        
        raw_filter = " ".join(raw_filter) if raw_filter else ""
        cursor = connection.cursor()
        query = f"""SELECT time_bucket('1 {period}', time) AS interval, device_type, os_type, country, SUM(count)
                    FROM {table_name}
                    WHERE (time BETWEEN '{from_date}' AND '{to_date}') {raw_filter}
                    GROUP BY interval, device_type, os_type, country"""
        cursor.execute(query)
        stat = cursor.fetchall() 
        
        for s in stat:
            time, device_type, os_type, country, count = s
            time = str(time)
            if country != "UZ":
                country = "ANOTHER"
            # res
            if not(device_type in res.keys()):
                res[device_type] = {}

            device = res[device_type]
            if not (os_type in device.keys()):
                device.update({os_type: {"UZ": 0, "ANOTHER": 0}})
                
            device[os_type][country] += count
            # periodic_res
            exists = False
            for x in periodic_res:
                if time in x.keys():
                    x[time][country] += count
                    exists = True
            
            if not exists:
                to_append = {time: {"UZ": 0, "ANOTHER": 0}}
                to_append[time][country] += count
                periodic_res.append(to_append)
        
        if report_param == "True":
            print("Report")
        
        
        return Response({"by_devices": res, "by_time": periodic_res}, status=200)


# ------------------------------------------------
class MostViewedContentAPIView(APIView):
        
    def get(self, request, *args, **kwargs):
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        category = request.GET.get("category", "1")
        age_group = request.GET.get("age_group", "").rstrip(",").split(",")
        gender = request.GET.get("gender")

        raw_filter = []

        if age_group[0]:
            for age in age_group:
                if raw_filter:
                    raw_filter.append(f"OR age_group = '{age}'")
                else:
                    raw_filter.append(f"AND (age_group = '{age}'")
            raw_filter.append(")")

        if gender in models.GENDERS_LIST:
            raw_filter.append(f"AND (gender = '{gender}')")

        try:
            date_format = "%Y-%m-%d"
            from_date = datetime.datetime.strptime(from_date, date_format)
            to_date = datetime.datetime.strptime(to_date, date_format).replace(minute=59, second=59)
        except:
            return Response({"error": "date validation"}, status=400)

        cursor = connection.cursor()
        raw_filter = " ".join(raw_filter) if raw_filter else ""
        # LAST MONTH VIEWS
        now = datetime.datetime.today()
        month_ago = now - datetime.timedelta(days=30)
        query = f"""SELECT time_bucket('30 days', time) AS interval, SUM(total_views)
                    FROM statistic_daily_total_views
                    WHERE (time BETWEEN '{month_ago}' AND '{now}') {raw_filter}
                    GROUP BY interval"""
        cursor.execute(query)
        stat = cursor.fetchall()
        last_views = []
        for s in stat:
            last_views.append({"time": s[0], "count": s[1]})
        # MOST VIEWED
        query = f"""SELECT content_id, episode_id, category_id, SUM(total_views)
                    FROM statistic_daily_content_views
                    WHERE (time BETWEEN '{from_date}' AND '{to_date}') {raw_filter}
                    GROUP BY content_id, episode_id, category_id"""
        cursor.execute(query)
        stat = cursor.fetchall()
        content_views = []
        for s in stat:
            content_id, episode_id, category_id, total_views = s
            exists = False
            for val in content_views:
                if val.get("content_id") == content_id and val.get("episode_id") == episode_id:
                        val["total_views"] += total_views
                        exists = True
            if not exists:
                content_views.append({"content_id": content_id, "episode_id": episode_id, "category": category_id, "total_views": total_views})            

        most_viewed = sorted(content_views, key=lambda d: d["total_views"], reverse=True)
        most_viewed_by_category = []
        for view in most_viewed:
            if len(most_viewed_by_category) <= 5:
                if str(view["category"]) == category:
                    most_viewed_by_category.append(view.copy())
            else:
                break

        most_viewed = most_viewed[:5]
        for view in most_viewed:
            to_update = data_extractor.get_data(data_extractor.CONTENT_DETAIL_PICTURE_URL.format(view["content_id"]), {})
            content = internal_models.Content.objects.get(content_id=view["content_id"])
            if view["episode_id"]:
                to_update["episode_id"] = content.title_ru.split("|")[-2].strip()
            to_update["category"] = internal_models.Category.objects.get(pk=view["category"]).name_ru
            view.update(to_update)

        for view in most_viewed_by_category:
            to_update = data_extractor.get_data(data_extractor.CONTENT_DETAIL_PICTURE_URL.format(view["content_id"]), {})
            content = internal_models.Content.objects.get(content_id=view["content_id"])
            if view["episode_id"]:
                to_update["episode_id"] = content.title_ru.split("|")[-2].strip()
            to_update["category"] = internal_models.Category.objects.get(pk=view["category"]).name_ru
            view.update(to_update)

        return Response(
            {"last_views": last_views, "most_viewed": most_viewed, "most_viewed_by_category": most_viewed_by_category},
            status=200
        )

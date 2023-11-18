import requests
from django.conf import settings


CATEGORY_URL = f'{settings.SPLAY_HOST}/ru/api/v3/statistics/categories/?limit=100'
SPONSORS_URL = f'{settings.SPLAY_HOST}/ru/api/v3/statistics/sponsors/?limit=10000'
SUBSCRIPTIONS_URL = f'{settings.SPLAY_HOST}/ru/api/v3/statistics/subscriptions/?limit=100'
CONTENT_DATA_URL = f'{settings.SPLAY_HOST}/ru/api/v3/statistics/content-data/'
BROADCAST_CATEGORY_URL = f'{settings.SPLAY_HOST}/ru/api/v3/statistics/broadcast-category/?limit=100'
BROADCAST_URL = f'{settings.SPLAY_HOST}/ru/api/v3/statistics/broadcast/?limit=1000'
CONTENT_SPONSOR_SUBS_URL = f'{settings.SPLAY_HOST}/ru/api/v3/statistics/content-sponsor-subscriptions/?limit=1000'
PROFILES_URL = f'{settings.SPLAY_HOST}/ru/api/v3/statistics/profiles'
TRANSACTION_URL = 'https://billing.splay.uz/api/v1/transaction-stat/'
SIGNUP_URL = 'https://api.splay.uz/en/api/v2/sevimlistat/account_registration/'


def get_data(url, params):
    count = 1
    result = None
    while count <= settings.MAX_RETRIES:
        try:
            response = requests.get(url, headers={"Sev-Stat-Secret-Key": settings.SPLAY_STAT_SECRET_KEY}, params=params)
            result = response.json()
            break
        except IOError as e:
            count += 1
    return result
    

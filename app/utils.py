import requests
from django.conf import settings


def get_splay_data(url, params):
    count = 1
    result = None
    while count <= settings.MAX_RETRIES:
        try:
            response = requests.get(url, headers={"Sev-Stat-Secret-Key": settings.SPLAY_STAT_SECRET_KEY}, params=params)
            result = response.json()
            break
        except IOError as e:
            print(e)
            count += 1
    return result
    

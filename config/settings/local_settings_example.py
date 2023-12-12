SECRET_KEY = "123" 
DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'timescale.db.backends.postgresql',
        'NAME': 'timescaledb',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

MAX_RETRIES = 3
SPLAY_HOST = ""
SPLAY_STAT_SECRET_KEY = ""

CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"

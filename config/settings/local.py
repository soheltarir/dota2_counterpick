from .base import *


DEBUG = True

# Database related settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "dota2_counterpick",
        "USER": "soheltarir",
        "PASSWORD": "",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

STEAM_API_KEY = "DDD252F22CD7F8A51D383FA99B5BBE89"

RABBITMQ_CELERY_EXCHANGE = "dota2_exchange"
DEFAULT_CELERY_QUEUE = "local_dota2_default_celery_queue"

DISABLE_COLLECTSTATIC = 1

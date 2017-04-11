from .base import *


DEBUG = True

# Database related settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "da81ie509tnnrf",
        "USER": "cpkyfpbrssdzfd",
        "PASSWORD": "459a0e131da479755993ca981152b1afd2148785bfad1160a197297e7181f002",
        "HOST": "ec2-107-22-250-33.compute-1.amazonaws.com",
        "PORT": "5432",
    }
}

STEAM_API_KEY = "DDD252F22CD7F8A51D383FA99B5BBE89"

RABBITMQ_CELERY_EXCHANGE = "heroku_dota2_exchange"
DEFAULT_CELERY_QUEUE = "heroku_dota2_default_celery_queue"

DISABLE_COLLECTSTATIC = 1

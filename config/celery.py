from __future__ import absolute_import

from celery import Celery
from django.conf import settings  # noqa
from kombu import Queue, Exchange
# from celery.schedules import crontab


# set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('config')

# CELERY_TIMEZONE = 'Asia/Kolkata'
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# CELERY_DEFAULT_QUEUE = 'default'

exchange = Exchange(name=settings.RABBITMQ_CELERY_EXCHANGE, type='topic', durable=True)

app.conf.update(
    CELERY_ROUTES=("config.celery_router.CeleryRouter", ),
    CELERY_QUEUES=(
         Queue(settings.DEFAULT_CELERY_QUEUE, exchange, routing_key=settings.DEFAULT_CELERY_QUEUE),
    )
)

if __name__ == '__main__':
    app.start()

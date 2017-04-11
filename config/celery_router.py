from django.conf import settings


class CeleryRouter:
    def route_for_task(self, task, args=None, kwargs=None):
        return settings.DEFAULT_CELERY_QUEUE

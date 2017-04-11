from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django_extensions.db.models import TimeStampedModel


class DotaHero(TimeStampedModel):
    popular_name = models.CharField(max_length=255, unique=True)
    system_name = models.CharField(max_length=255)
    image = models.ImageField()

    class Meta:
        app_label = "heroes"
        db_table = "dota_hero"

    def __str__(self):
        return self.popular_name

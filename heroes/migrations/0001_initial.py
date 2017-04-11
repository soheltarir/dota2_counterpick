# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-07 12:23
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DotaHero',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('popular_name', models.CharField(max_length=255, unique=True)),
                ('system_name', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='')),
            ],
            options={
                'db_table': 'dota_hero',
            },
        ),
    ]

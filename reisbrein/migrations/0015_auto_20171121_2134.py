# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-21 20:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reisbrein', '0014_auto_20171121_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertravelplan',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

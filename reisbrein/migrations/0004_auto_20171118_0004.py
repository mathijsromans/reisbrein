# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-17 23:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reisbrein', '0003_auto_20171117_2309'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertravelpreferences',
            name='has_car',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='usertravelpreferences',
            name='home_address',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]

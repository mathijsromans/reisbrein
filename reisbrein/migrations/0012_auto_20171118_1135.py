# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-18 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reisbrein', '0011_auto_20171118_1014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertravelpreferences',
            name='has_bicycle',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='usertravelpreferences',
            name='has_car',
            field=models.BooleanField(default=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-18 06:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reisbrein', '0007_auto_20171118_0346'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertravelpreferences',
            name='show_n_results',
            field=models.IntegerField(default=10),
        ),
    ]
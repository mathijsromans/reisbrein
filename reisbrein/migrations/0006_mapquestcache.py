# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-18 02:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reisbrein', '0005_auto_20171118_0106'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapQuestCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search', models.CharField(max_length=80)),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
            ],
        ),
    ]

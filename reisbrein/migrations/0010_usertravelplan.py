# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-18 09:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reisbrein', '0009_auto_20171118_0736'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTravelPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.CharField(max_length=500)),
                ('end', models.CharField(max_length=500)),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-datetime_created'],
            },
        ),
    ]

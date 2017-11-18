from django.db import models
from django.contrib.auth.models import User


class UserTravelPreferences(models.Model):
    user = models.OneToOneField(User)
    home_address = models.CharField(max_length=500, blank=True, default="")
    has_bicycle = models.BooleanField(default=False, blank=True)
    has_car = models.BooleanField(default=False, blank=True)
    travel_time_importance = models.IntegerField(default=5)
    likes_to_bike = models.IntegerField(default=5)
    show_n_results = models.IntegerField(default=15)
    datetime_update = models.DateTimeField(auto_now=True)


class UserTravelPlan(models.Model):
    user = models.ForeignKey(User)
    start = models.CharField(max_length=500)
    end = models.CharField(max_length=500)
    datetime_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-datetime_created']


class MapQuestCache(models.Model):
    search = models.CharField(max_length=80)
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)

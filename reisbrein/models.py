from django.db import models
from django.contrib.auth.models import User


class UserTravelPreferences(models.Model):
    user = models.OneToOneField(User)
    home_address = models.CharField(max_length=500, blank=True, default="")
    has_bicycle = models.BooleanField(default=False, blank=True)
    has_car = models.BooleanField(default=False, blank=True)
    travel_time_importance = models.IntegerField(default=5)
    likes_to_bike = models.IntegerField(default=5)
    datetime_update = models.DateTimeField(auto_now=True)

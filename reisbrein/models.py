from django.db import models
from django.contrib.auth.models import User


class UserTravelPreferences(models.Model):
    user = models.OneToOneField(User)
    travel_time_importance = models.IntegerField(default=50)
    has_bicycle = models.BooleanField(default=False, blank=True)
    likes_to_bike = models.IntegerField(default=50)
    datetime_update = models.DateTimeField(auto_now=True)

from django.db import models
from django.contrib.auth.models import User


class UserTravelPreferences(models.Model):
    user = models.OneToOneField(User)
    home_address = models.CharField(max_length=500, blank=True, default="")
    has_bicycle = models.BooleanField(default=True, blank=True)
    has_car = models.BooleanField(default=True, blank=True)
    avoid_highways = models.BooleanField(default=False, blank=False)
    #reduce_number_of_transfers = models.BooleanField(default=False, blank=False)
    travel_time_importance = models.IntegerField(default=5)
    likes_to_bike = models.IntegerField(default=5)
    save_CO2 = models.IntegerField(default=0)
    show_n_results = models.IntegerField(default=15)
    datetime_update = models.DateTimeField(auto_now=True)


class UserTravelPlan(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    start = models.CharField(max_length=500)
    end = models.CharField(max_length=500)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-datetime_updated']


class Request(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    start = models.CharField(max_length=500)
    end = models.CharField(max_length=500)
    timedelta = models.FloatField(default=0)
    datetime_created = models.DateTimeField(auto_now_add=True)


class TravelTime(models.Model):
    flat = models.FloatField()
    flon = models.FloatField()
    tlat = models.FloatField()
    tlon = models.FloatField()
    distance = models.IntegerField()
    transport_type = models.IntegerField()
    time_sec = models.IntegerField()
    datetime_created = models.DateTimeField(auto_now_add=True)

    @property
    def speed(self):
        if self.time_sec != 0:
            return self.distance/self.time_sec
        return 0.0


class ApiCache(models.Model):
    url = models.CharField(max_length=250)
    params = models.CharField(max_length=250)
    headers = models.CharField(max_length=250)
    result = models.TextField()
    datetime_updated = models.DateTimeField(auto_now=True)



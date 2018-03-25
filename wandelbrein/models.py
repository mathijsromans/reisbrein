from django.db import models


class Trail(models.Model):
    title = models.CharField(max_length=500)
    wandelpagina_id = models.CharField(unique=True, primary_key=True, max_length=100)
    wandelpagina_url = models.URLField(blank=True, null=True, max_length=500)
    nswandel_url = models.URLField(blank=True, null=True, max_length=500)
    begin_lon = models.FloatField()
    begin_lat = models.FloatField()
    end_lon = models.FloatField()
    end_lat = models.FloatField()
    distance = models.FloatField()
    gpx = models.TextField(blank=True, default="")

    @property
    def distance_km(self):
        return self.distance / 1000
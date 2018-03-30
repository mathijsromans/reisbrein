from wandelbrein.scraper import get_groene_wissels_data
from wandelbrein.models import Trail


def scrape_and_create_trails(max_trails=None):
    trails_data = get_groene_wissels_data(max_trails)
    for trail_data in trails_data:
        trail = Trail()
        trail.title = trail_data.title
        trail.distance = trail_data.distance_m
        trail.wandelpagina_id = trail_data.wandelpagina_id
        trail.wandelpagina_url = trail_data.wandelpagina_url
        trail.nswandel_url = trail_data.nswandel_url
        trail.begin_lon = trail_data.begin_point.longitude
        trail.begin_lat = trail_data.begin_point.latitude
        trail.end_lon = trail_data.end_point.longitude
        trail.end_lat = trail_data.end_point.latitude
        trail.gpx = trail_data.gpx
        Trail.objects.filter(wandelpagina_id=trail.wandelpagina_id).delete()
        trail.save()


def delete_trails():
    Trail.objects.all().delete()

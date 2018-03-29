from django.contrib import admin
from reisbrein.models import UserTravelPlan, UserTravelPreferences, Request, TravelTime, ApiCache
from reisbrein.primitives import TransportType
from django.conf.locale.en import formats as en_formats
import csv
from django.http import HttpResponse
from io import StringIO

en_formats.DATETIME_FORMAT = "d M Y H:i:s"

class UserTravelPlanAdmin(admin.ModelAdmin):
    model = UserTravelPlan
    list_display = ('user', 'start', 'end', 'datetime_updated')


class UserTravelPreferencesAdmin(admin.ModelAdmin):
    model = UserTravelPreferences
    list_display = ('user', 'has_bicycle', 'has_car', 'travel_time_importance', 'likes_to_bike', 'show_n_results')


class RequestAdmin(admin.ModelAdmin):
    model = Request
    list_display = ('user', 'start', 'end', 'timedelta', 'datetime_created')


class TravelTimeAdmin(admin.ModelAdmin):

    actions = ['download_csv']

    @staticmethod
    def transport_type_dutch(travel_time):
        return TransportType(travel_time.transport_type).to_dutch()

    # from https://www.endpoint.com/blog/2012/02/22/dowloading-csv-file-with-from-django
    @staticmethod
    def download_csv(self, request, queryset):
        f = StringIO()
        writer = csv.writer(f)
        writer.writerow(['flat', 'flon', 'tlat', 'tlon', 'transport_type_dutch', 'distance', 'time_sec', 'speed', 'datetime_created'])

        for s in queryset:
            writer.writerow([s.flat, s.flon, s.tlat, s.tlon, TravelTimeAdmin.transport_type_dutch(s), s.distance, s.time_sec, s.speed, s.datetime_created])

        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=stat-info.csv'
        return response
    download_csv.short_description = "Download CSV file for selected stats."

    model = TravelTime
    list_display = ('flat', 'flon', 'tlat', 'tlon', 'transport_type_dutch', 'distance', 'time_sec', 'speed', 'datetime_created')


class ApiCacheAdmin(admin.ModelAdmin):
    model = ApiCache
    list_display = ('url', 'datetime_updated')


admin.site.register(UserTravelPlan, UserTravelPlanAdmin)
admin.site.register(UserTravelPreferences, UserTravelPreferencesAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(TravelTime, TravelTimeAdmin)
admin.site.register(ApiCache, ApiCacheAdmin)

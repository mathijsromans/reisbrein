from django.contrib import admin
from reisbrein.models import UserTravelPlan, UserTravelPreferences, Request, TravelTime, ApiCache
from reisbrein.primitives import TransportType
from django.conf.locale.en import formats as en_formats
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

    @staticmethod
    def transport_type_dutch(travel_time):
        return TransportType(travel_time.transport_type).to_dutch()

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

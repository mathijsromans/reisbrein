from django.contrib import admin
from reisbrein.models import UserTravelPlan, UserTravelPreferences, Request, TravelTime
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
    list_display = ('user', 'start', 'end', 'datetime_created')


class TravelTimeAdmin(admin.ModelAdmin):
    model = TravelTime
    list_display = ('flat', 'flon', 'tlat', 'tlon', 'transport_type', 'distance', 'time_sec', 'speed', 'datetime_created')


admin.site.register(UserTravelPlan, UserTravelPlanAdmin)
admin.site.register(UserTravelPreferences, UserTravelPreferencesAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(TravelTime, TravelTimeAdmin)

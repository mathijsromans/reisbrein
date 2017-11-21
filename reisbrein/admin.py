from django.contrib import admin
from reisbrein.models import UserTravelPlan, UserTravelPreferences


class UserTravelPlanAdmin(admin.ModelAdmin):
    model = UserTravelPlan
    list_display = ('user', 'start', 'end')


class UserTravelPreferencesAdmin(admin.ModelAdmin):
    model = UserTravelPreferences
    list_display = ('user', 'has_bicycle', 'has_car', 'travel_time_importance', 'likes_to_bike', 'show_n_results')


admin.site.register(UserTravelPlan, UserTravelPlanAdmin)
admin.site.register(UserTravelPreferences, UserTravelPreferencesAdmin)

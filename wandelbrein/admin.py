from django.contrib import admin
from wandelbrein.models import Trail


class TrailAdmin(admin.ModelAdmin):
    model = Trail
    list_display = (
        'id', 'wandelpagina_id', 'title', 'distance', 'nswandel_url', 'wandelpagina_url', 'nswandel_url', 'begin_lon', 'begin_lat', 'end_lon', 'end_lat'
    )


admin.site.register(Trail, TrailAdmin)

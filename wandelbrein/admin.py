from django.contrib import admin
from wandelbrein.models import Trail

admin.site.register(Trail, admin.ModelAdmin)

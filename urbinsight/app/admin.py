from django.contrib import admin

# Register your models here.
from django.contrib.gis import admin
from app.models import Region

admin.site.register(Region, admin.GeoModelAdmin)
from django.contrib import admin

# Register your models here.
from django.contrib.gis import admin
from rescape_region.models import Region

admin.site.register(Region, admin.GeoModelAdmin)
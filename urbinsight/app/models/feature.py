from app.helpers.geometry_helpers import geometry_from_feature, ewkt_from_feature
from django.contrib.gis.db import models
from django.contrib.gis.db.models import MultiPolygonField, PolygonField, GeometryField
from django.contrib.gis.geos import MultiPolygon
from django.db.models import (
    CharField, IntegerField, Model,
    DateTimeField)
from django.contrib.postgres.fields import JSONField


def default():
    return dict()


default_geometry = ewkt_from_feature(
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon", "coordinates": [[[-85, -180], [85, -180], [85, 180], [-85, 180], [-85, -180]]]
        }
    }
)


class Feature(Model):
    """
        Models a geospatial feature. Location is the geometry with a type and coordinates. All other properties
        become properties when represented in graphql or as geojson. Feature is a foreign key to classes like
        Resource.
    """

    name = CharField(max_length=50, null=True)
    description = CharField(max_length=500, unique=False, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    location = GeometryField(null=False, default=default_geometry)

    class Meta:
        app_label = "app"

    def __str__(self):
        return self.name

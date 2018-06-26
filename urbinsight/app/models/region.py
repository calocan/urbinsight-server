from django.db.models import (
    CharField, IntegerField, Model
)
from django.contrib.postgres.fields import JSONField


class Region(Model):
    """
        Models a geospatial region
    """
    name = CharField(max_length=50, unique=True, null=False)
    data = JSONField(null=False, default=lambda: dict())

    class Meta:
        app_label = "app"

    def __str__(self):
        return self.name

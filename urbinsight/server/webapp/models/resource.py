from django.db.models import (
    CharField, IntegerField, Model
)
from django.contrib.postgres.fields import JSONField

class Resource(Model):
    """
        Models a resource, such as water
    """
    name = CharField(max_length=50, unique=True, null=False)
    data = JSONField(null=False, default=lambda: dict())

    def __str__(self):
        return self.name

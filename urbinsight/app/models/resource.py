from django.db.models import (
    CharField, IntegerField, Model,
    DateTimeField)
from django.contrib.postgres.fields import JSONField

def default():
    return dict()

class Resource(Model):
    """
        Models a resource, such as water
    """
    name = CharField(max_length=50, unique=True, null=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    data = JSONField(null=False, default=default)

    class Meta:
        app_label = "app"

    def __str__(self):
        return self.name

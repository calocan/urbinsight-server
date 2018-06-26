from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models import Model, ForeignKey

def default():
    return dict(resources=[])


class UserSettings(Model):
    user = ForeignKey(User)
    data = JSONField(null=False, default=default)

    class Meta:
        app_label = "app"

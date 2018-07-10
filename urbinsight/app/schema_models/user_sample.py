from app.helpers.geometry_helpers import ewkt_from_feature
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rescape_graphene import ramda as R
from app.models import Feature, Region
from django.db import transaction

sample_users = [
    dict(username="lion", first_name='Simba', last_name='The Lion',
                                  password=make_password("roar", salt='not_random')),
    dict(username="cat", first_name='Felix', last_name='The Cat',
                                  password=make_password("meow", salt='not_random'))
]


def create_user(user_dict):
    # Save the region with the complete data

    user = get_user_model()(**user_dict)
    user.save()
    return user
